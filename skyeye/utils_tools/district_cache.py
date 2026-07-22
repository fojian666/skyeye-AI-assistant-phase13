"""
行政区划边界查询模块
从本地 GeoJSON 文件查询行政区数据（全国 690 地市 + 5651 县区 + 江苏省 22841 村）
不支持省级（省/自治区/直辖市）和乡镇级，这些级别 GeoJSON 无覆盖。
"""
import json
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

GEOJSON_DIR = os.path.join(settings.BASE_DIR, 'geojson')
GEOJSON_INDEX_FILE = os.path.join(GEOJSON_DIR, 'index.json')

SUB_REGION_COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#F8C471', '#82E0AA', '#F1948A', '#85929E', '#AED6F1',
]


# ==================== GeoJSON 加载 ====================

_geojson_index = None       # name → [{file, feature_idx}]
_geojson_file_cache = {}    # file_path → geojson dict
_poi_index = None           # name → {category, district, coordinates: [lng, lat]}

POI_INDEX_FILE = os.path.join(GEOJSON_DIR, 'poi', 'poi_index.json')


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


def _geo_feature_to_result(feature):
    """GeoJSON Feature → { name, polygon: [[{lng, lat}, ...]], center: {lng, lat} }"""
    props = feature.get('properties', {})
    geom = feature.get('geometry', {})
    coords = geom.get('coordinates', [])

    polygon = []
    if geom['type'] == 'Polygon':
        for ring in coords:
            polygon.append([{'lng': pt[0], 'lat': pt[1]} for pt in ring])
    elif geom['type'] == 'MultiPolygon':
        for poly in coords:
            polygon.append([{'lng': pt[0], 'lat': pt[1]} for pt in poly[0]])

    center = props.get('center', None)
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


def _extract_sub_regions(parent_feature, parent_name):
    """从同级 GeoJSON 文件中提取子区域（市→县、县→村）"""
    props = parent_feature.get('properties', {})
    level = props.get('level', '')

    sub_features = []
    if level == 'city':
        county_file = _load_geojson_file('county_2024.geojson')
        if county_file:
            for feat in county_file.get('features', []):
                if feat['properties'].get('parent') == parent_name:
                    sub_features.append(feat)
    elif level == 'county':
        village_file = _load_geojson_file('village_jiangsu.geojson')
        if village_file and props.get('province') == '江苏省':
            county_name = parent_name.rstrip('区县市')
            for feat in village_file.get('features', []):
                v_parent = feat['properties'].get('parent', '')
                if v_parent == county_name or v_parent == parent_name:
                    sub_features.append(feat)

    sub_regions = []
    for i, feat in enumerate(sub_features):
        converted = _geo_feature_to_result(feat)
        sub_regions.append({
            'name': converted['name'],
            'polygon': converted['polygon'],
            'center': converted['center'],
            'color': SUB_REGION_COLORS[i % len(SUB_REGION_COLORS)],
        })
    return sub_regions


# ==================== 公开 API ====================

def query_district(keywords, city=''):
    """
    查询行政区数据（仅本地 GeoJSON，无外部 API 依赖）
    返回 { name, polygon, center, sub_regions: [...] } 或 None
    不支持省级和乡镇级，这些级别返回 None
    """
    # 省级/直辖市：GeoJSON 无对应数据，返回 None
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
            elif name in keywords and len(keywords) - len(name) <= 2:
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

    entry = candidates[0]
    geojson = _load_geojson_file(entry['file'])
    if not geojson:
        return None

    feature = geojson['features'][entry['feature_idx']]
    result = _geo_feature_to_result(feature)
    sub_regions = _extract_sub_regions(feature, result['name'])
    result['sub_regions'] = sub_regions

    logger.info(f'GeoJSON 命中: {keywords} → {entry["file"]}#{entry["feature_idx"]}'
                f' ({len(sub_regions)} 个子区域)')
    return result


# ==================== POI 查询 ====================

def _load_poi_index():
    """懒加载 POI 索引（进程生命周期内单次加载）"""
    global _poi_index
    if _poi_index is not None:
        return _poi_index
    if os.path.exists(POI_INDEX_FILE):
        try:
            with open(POI_INDEX_FILE, 'r', encoding='utf-8') as f:
                _poi_index = json.load(f)
                logger.info(f'POI 索引已加载: {len(_poi_index)} 个点位')
                return _poi_index
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f'POI 索引文件加载失败: {e}')
    _poi_index = {}
    return _poi_index


def query_poi(keywords):
    """
    查询南京 POI 点位数据
    返回 { name, lat, lng, category, district } 或 None
    """
    index = _load_poi_index()
    if not index:
        return None

    # 1. 精确匹配
    if keywords in index:
        entry = index[keywords]
        return {
            'name': keywords,
            'lat': entry['coordinates'][1],
            'lng': entry['coordinates'][0],
            'category': entry['category'],
            'district': entry['district'],
        }

    # 2. 模糊匹配（关键词包含在名称中）
    candidates = []
    for name, entry in index.items():
        if keywords in name:
            candidates.append((name, entry))
    if not candidates:
        return None

    # 优选策略: 1) 名称以关键词开头且无括号修饰 > 2) 最短
    def _score(item):
        name = item[0]
        starts_with = 10 if name.startswith(keywords) else 0
        no_parens = 5 if '(' not in name and '（' not in name else 0
        return (starts_with + no_parens, -len(name))

    candidates.sort(key=_score, reverse=True)
    name, entry = candidates[0]

    logger.info(f'POI 模糊匹配: "{keywords}" → "{name}"')
    return {
        'name': name,
        'lat': entry['coordinates'][1],
        'lng': entry['coordinates'][0],
        'category': entry['category'],
        'district': entry['district'],
    }
