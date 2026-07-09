"""
行政区划边界缓存模块
首次查询时从高德 API 获取并缓存到本地 JSON，后续直接读缓存。
"""
import json
import os
import time
import logging
import configparser
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

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


def query_district(keywords, city='', use_cache=True):
    """
    查询行政区数据（优先缓存）
    返回 { name, polygon, center, sub_regions: [...] }
    """
    cache_key = f'{keywords}|{city}' if city else keywords

    if use_cache:
        cache = load_cache()
        if cache_key in cache:
            logger.info(f'缓存命中: {cache_key}')
            return cache[cache_key]

    logger.info(f'实时查询: {keywords} city={city}')
    data = _call_district_api(keywords, subdistrict=1)
    if data.get('status') != '1' or not data.get('districts'):
        logger.error(f'API 异常: {data}')
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
            # 需要单独查询子区域
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
                logger.info(f'  查询子区域: {child_name}')
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
                    logger.warning(f'    {child_name} API 失败')

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
