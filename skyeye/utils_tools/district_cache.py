"""
行政区划边界缓存模块
查询优先级: 本地 GeoJSON (一级) → 高德 API 缓存 (二级) → 高德 API 实时 (三级)
首次查询时从本地 GeoJSON 获取，未命中则降级到高德 API 并缓存。
"""
import json
import os
import time
import logging
import configparser
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GEOJSON_DIR = os.path.join(settings.BASE_DIR, 'geojson')
GEOJSON_INDEX_FILE = os.path.join(GEOJSON_DIR, 'index.json')
CACHE_FILE = os.path.join(settings.BASE_DIR, 'district_cache.json')

SUB_REGION_COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#F8C471', '#82E0AA', '#F1948A', '#85929E', '#AED6F1',
]


def _get_api_key():
    config = configparser.ConfigParser()
    config.read(os.path.join(settings.BASE_DIR, 'config.ini'), encoding='utf-8')
    return config.get('amap', 'api_key')


def _parse_polyline(polyline):
    """高德 polyline → [{lng, lat}, ...] 二维数组"""
    points = []
    if polyline:
        for block in polyline.split('|'):
            pts = []
            for pair in block.split(';'):
                parts = pair.split(',')
                if len(parts) == 2:
                    pts.append({'lng': float(parts[0]), 'lat': float(parts[1])})
            points.append(pts)
    return points


_cache = None  # 模块级内存缓存，进程生命周期内只加载一次


def load_cache():
    global _cache
    if _cache is not None:
        return _cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                _cache = json.load(f)
                logger.info(f'缓存已加载: {len(_cache)} 条记录 ({len(json.dumps(_cache)) / 1024 / 1024:.1f} MB)')
                return _cache
        except (json.JSONDecodeError, IOError):
            pass
    _cache = {}
    return _cache


def save_cache(cache):
    global _cache
    _cache = cache
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _call_district_api(keywords, subdistrict=0, max_retries=3):
    """调用高德行政区划 API（含重试）"""
    api_key = _get_api_key()
    params = {
        'key': api_key, 'keywords': keywords,
        'subdistrict': subdistrict, 'extensions': 'all',
    }
    for attempt in range(max_retries):
        try:
            resp = requests.get('https://restapi.amap.com/v3/config/district', params=params, timeout=15)
            return resp.json()
        except Exception as e:
            logger.warning(f'  API 第{attempt+1}次失败 ({keywords}): {e}')
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))  # 2s, 4s 退避
    return {'status': '0', 'info': 'ALL_RETRIES_FAILED'}


def _geocode(address, city=''):
    api_key = _get_api_key()
    params = {'key': api_key, 'address': address, 'output': 'JSON'}
    if city:
        params['city'] = city
    try:
        resp = requests.get('https://restapi.amap.com/v3/geocode/geo', params=params, timeout=10)
        data = resp.json()
        if data.get('status') == '1' and data.get('geocodes'):
            loc = data['geocodes'][0]['location']
            lng, lat = loc.split(',')
            return {'lat': float(lat), 'lng': float(lng),
                    'address': data['geocodes'][0].get('formatted_address', address)}
    except Exception:
        pass
    return None


def _process_district(dist):
    """标准化行政区数据"""
    name = dist.get('name', '')
    points = _parse_polyline(dist.get('polyline', ''))
    center_str = dist.get('center', '')
    center = None
    if center_str:
        c = center_str.split(',')
        if len(c) == 2:
            center = {'lng': float(c[0]), 'lat': float(c[1])}
    return {'name': name, 'polygon': points, 'center': center}


def _filter_by_city(districts, city):
    """过滤同名异城结果（纬度差 < 1 度）"""
    if not city or len(districts) <= 1:
        return districts
    city_geo = _geocode(city)
    if not city_geo:
        return districts
    filtered = []
    for d in districts:
        cs = d.get('center', '')
        if cs:
            cc = cs.split(',')
            if len(cc) == 2 and abs(float(cc[1]) - city_geo['lat']) < 1.0:
                filtered.append(d)
    return filtered if filtered else districts


# ==================== 本地 GeoJSON 查询 (一级) ====================

_geojson_index = None       # name → [{file, feature_idx}]
_geojson_file_cache = {}    # file_path → geojson dict (LRU 由 Python dict 保持加载顺序)


def _load_geojson_index():
    """加载 GeoJSON 索引（进程生命周期内单次加载）"""
    global _geojson_index
    if _geojson_index is not None:
        return _geojson_index
    if os.path.exists(GEOJSON_INDEX_FILE):
        try:
            with open(GEOJSON_INDEX_FILE, 'r', encoding='utf-8') as f:
                _geojson_index = json.load(f)
                logger.info(f'GeoJSON 索引已加载: {len(_geojson_index)} 个地名')
                return _geojson_index
        except (json.JSONDecodeError, IOError):
            logger.warning(f'GeoJSON 索引文件损坏: {GEOJSON_INDEX_FILE}')
    _geojson_index = {}
    return _geojson_index


def _load_geojson_file(filename):
    """懒加载单个 GeoJSON 文件"""
    if filename in _geojson_file_cache:
        return _geojson_file_cache[filename]
    filepath = os.path.join(GEOJSON_DIR, filename)
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _geojson_file_cache[filename] = data
            logger.debug(f'  GeoJSON 文件已加载: {filename} ({len(data.get("features", []))} 条)')
            return data
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f'  加载 GeoJSON 文件失败 {filename}: {e}')
        return None


def _geojson_polygon_to_amap_format(feature):
    """
    将 GeoJSON Feature 转为高德 API 兼容格式:
    { name, polygon: [[{lng, lat}, ...]], center: {lng, lat} }
    """
    props = feature.get('properties', {})
    geom = feature.get('geometry', {})
    coords = geom.get('coordinates', [])

    # 转换坐标: GeoJSON [lng, lat] → 高德 {lng, lat}
    polygon = []
    if geom['type'] == 'Polygon':
        for ring in coords:
            polygon.append([{'lng': pt[0], 'lat': pt[1]} for pt in ring])
    elif geom['type'] == 'MultiPolygon':
        for poly in coords:
            polygon.append([{'lng': pt[0], 'lat': pt[1]} for pt in poly[0]])

    center = props.get('center', None)
    # 如果properties没有center，从geometry计算
    if not center and polygon and polygon[0]:
        lats = [p['lat'] for p in polygon[0]]
        lngs = [p['lng'] for p in polygon[0]]
        center = {'lng': round((min(lngs) + max(lngs)) / 2, 6),
                   'lat': round((min(lats) + max(lats)) / 2, 6)}

    return {
        'name': props.get('name', ''),
        'polygon': polygon,
        'center': center,
    }


def _extract_sub_regions(parent_feature, parent_name, cache):
    """
    从同级 GeoJSON 文件中提取子区域
    例如: 查"南京市" → 自动找出所有 parent="南京市" 的县级 features
    或: 查"玄武区" → 找出所有 city/parent="南京市" 对应区下的 village
    """
    props = parent_feature.get('properties', {})
    level = props.get('level', '')

    sub_features = []
    if level == 'city':
        # 查县级子区域
        county_file = _load_geojson_file('county_2024.geojson')
        if county_file:
            for feat in county_file.get('features', []):
                if feat['properties'].get('parent') == parent_name:
                    sub_features.append(feat)
    elif level == 'county':
        # 查村级子区域
        village_file = _load_geojson_file('village_jiangsu.geojson')
        if village_file and props.get('province') == '江苏省':
            county_name = parent_name.rstrip('区县市')
            for feat in village_file.get('features', []):
                v_parent = feat['properties'].get('parent', '')
                if v_parent == county_name or v_parent == parent_name:
                    sub_features.append(feat)

    sub_regions = []
    for i, feat in enumerate(sub_features):
        converted = _geojson_polygon_to_amap_format(feat)
        sub_regions.append({
            'name': converted['name'],
            'polygon': converted['polygon'],
            'center': converted['center'],
            'color': SUB_REGION_COLORS[i % len(SUB_REGION_COLORS)],
        })
    return sub_regions


def query_district_local(keywords, city=''):
    """
    从本地 GeoJSON 文件查询行政区数据
    返回 { name, polygon, center, sub_regions: [...] } 或 None
    """
    # 省级/直辖市：GeoJSON 无对应数据，直接走 高德 API
    PROVINCE_KEYWORDS = {'北京市', '上海市', '天津市', '重庆市'}
    if keywords.endswith(('省', '自治区')) or keywords in PROVINCE_KEYWORDS:
        return None

    index = _load_geojson_index()
    if not index:
        return None

    # 1. 精确匹配
    candidates = index.get(keywords, [])

    # 2. 命名变体匹配
    if not candidates:
        for variant in [keywords + '区', keywords + '县', keywords + '市',
                         keywords + '街道', keywords + '镇']:
            if variant in index:
                candidates = index[variant]
                break

    # 3. 模糊匹配（包含关系，限制长度差 ≤ 2 防误匹配）
    if not candidates:
        matches = []
        for name in index:
            if keywords in name and len(name) - len(keywords) <= 2:
                matches.extend(index[name])
            elif name in keywords:
                matches.extend(index[name])
        if matches:
            candidates = matches
            logger.info(f'GeoJSON 模糊匹配: "{keywords}" → {len(matches)} 条')

    if not candidates:
        return None

    # 如果指定了 city，用 city 筛选同名异城结果
    if city and len(candidates) > 1:
        filtered = []
        for c in candidates:
            geojson = _load_geojson_file(c['file'])
            if geojson:
                feat = geojson['features'][c['feature_idx']]
                parent = feat['properties'].get('parent', '')
                province = feat['properties'].get('province', '')
                if city in parent or city in province:
                    filtered.append(c)
        if filtered:
            candidates = filtered

    # 取第一个匹配
    entry = candidates[0]
    geojson = _load_geojson_file(entry['file'])
    if not geojson:
        return None

    feature = geojson['features'][entry['feature_idx']]
    result = _geojson_polygon_to_amap_format(feature)

    # 提取子区域
    sub_regions = _extract_sub_regions(feature, result['name'], cache=None)
    result['sub_regions'] = sub_regions

    logger.info(f'GeoJSON 命中: {keywords} → {entry["file"]}#{entry["feature_idx"]}'
                f' ({len(sub_regions)} 个子区域)')
    return result


def query_district(keywords, city='', use_cache=True):
    """
    查询行政区数据
    优先级: 本地 GeoJSON (一级) → 高德缓存 (二级) → 高德 API 实时 (三级)
    返回 { name, polygon, center, sub_regions: [...] }
    """
    # 省级/直辖市：GeoJSON 无对应数据，跳过缓存直接查 高德 API
    PROVINCE_KEYWORDS = {'北京市', '上海市', '天津市', '重庆市'}
    if keywords.endswith(('省', '自治区')) or keywords in PROVINCE_KEYWORDS:
        use_cache = False

    cache_key = f'{keywords}|{city}' if city else keywords

    # ====== 一级: 本地 GeoJSON ======
    local_result = query_district_local(keywords, city)
    if local_result:
        # 将本地结果也写入缓存，供后续重复查询使用
        if use_cache:
            cache = load_cache()
            cache[cache_key] = local_result
            save_cache(cache)
        return local_result

    # ====== 二级: 高德缓存 ======
    if use_cache:
        cache = load_cache()
        if cache_key in cache:
            logger.info(f'高德缓存命中: {cache_key}')
            return cache[cache_key]

    # ====== 三级: 高德 API 实时查询 ======
    logger.info(f'高德 API 实时查询: {keywords} city={city}')
    data = _call_district_api(keywords, subdistrict=1)
    if data.get('status') != '1' or not data.get('districts'):
        logger.error(f'高德 API 异常: {data}')
        return None

    districts = _filter_by_city(data['districts'], city)
    dist = districts[0]
    result = _process_district(dist)

    # 解析子区域
    children = dist.get('districts', [])
    sub_regions = []
    cache = load_cache() if use_cache else {}

    for i, child in enumerate(children):
        child_name = child.get('name', '')
        child_polyline = child.get('polyline', '')

        if child_polyline:
            # 子区域自带 polyline（极少情况）
            cp = _parse_polyline(child_polyline)
            if cp or child_name:
                sub_regions.append({
                    'name': child_name, 'polygon': cp,
                    'center': _parse_center(child.get('center', '')),
                    'color': SUB_REGION_COLORS[i % len(SUB_REGION_COLORS)],
                })
        elif child_name:
            # 优先查本地 GeoJSON
            child_local = query_district_local(child_name, city)
            if child_local:
                sub_regions.append({
                    'name': child_name, 'polygon': child_local['polygon'],
                    'center': child_local.get('center'),
                    'color': SUB_REGION_COLORS[i % len(SUB_REGION_COLORS)],
                })
            else:
                child_key = f'{child_name}|{city}'
                if child_key in cache:
                    cached = cache[child_key]
                    sub_regions.append({
                        'name': child_name, 'polygon': cached['polygon'],
                        'center': cached.get('center'),
                        'color': SUB_REGION_COLORS[i % len(SUB_REGION_COLORS)],
                    })
                else:
                    # 串行查询，间隔 1 秒防频率限制
                    time.sleep(1.0)
                    logger.info(f'  高德子区域查询: {child_name}')
                    child_data = _call_district_api(child_name, subdistrict=0)
                    if child_data.get('status') == '1' and child_data.get('districts'):
                        cd = _filter_by_city(child_data['districts'], city)
                        cr = _process_district(cd[0])
                        if cr.get('polygon'):
                            cache[child_key] = cr
                            sub_regions.append({
                                'name': child_name, 'polygon': cr['polygon'],
                                'center': cr.get('center'),
                                'color': SUB_REGION_COLORS[i % len(SUB_REGION_COLORS)],
                            })
                            logger.info(f'    {child_name} OK')
                        else:
                            logger.warning(f'    {child_name} 无边界')
                    else:
                        logger.warning(f'    {child_name} 高德 API 失败')

    result['sub_regions'] = sub_regions

    if use_cache:
        cache[cache_key] = result
        save_cache(cache)

    return result


def _parse_center(center_str):
    """'lng,lat' → {lng, lat}"""
    if center_str:
        c = center_str.split(',')
        if len(c) == 2:
            return {'lng': float(c[0]), 'lat': float(c[1])}
    return None


def preload_jiangsu_all():
    """预加载江苏省所有城市及区县（用于首次启动）"""
    logger.info('=== 预加载江苏省 ===')
    data = _call_district_api('江苏省', subdistrict=1)
    if data.get('status') != '1' or not data.get('districts'):
        return 0

    cities = data['districts'][0].get('districts', [])
    logger.info(f'共 {len(cities)} 个城市')
    total = 0

    for city in cities:
        city_name = city.get('name', '')
        if not city_name:
            continue
        city_short = city_name.replace('市', '')
        logger.info(f'--- {city_name} ---')
        try:
            r = query_district(city_name, city=city_short, use_cache=True)
            if r:
                n = len(r.get('sub_regions', []))
                total += n
                logger.info(f'  {n} 个区县')
        except Exception as e:
            logger.error(f'  {city_name} 失败: {e}')

    logger.info(f'=== 完成，共 {total} 个区县 ===')
    return total
