#!/usr/bin/env python3
"""
Shapefile → GeoJSON 批量转换工具
将 border-resources 的数据转为标准 GeoJSON，供地图边界查询使用。

支持:
  - 县级/地市级边界 (WGS-84, EPSG:4326)
  - 江苏省村界 (CGCS2000 投影 → WGS-84, EPSG:4549→4326)
  - 字符编码自动处理 (GBK/UTF-8)

输出:
  skyeye/geojson/
    ├── county_2024.geojson       # 县级边界
    ├── city_2024.geojson         # 地市级边界
    ├── village_jiangsu.geojson   # 江苏村界
    └── index.json                # 名称→文件+位置索引
"""
import json
import os
import sys
import time
import struct
from pathlib import Path
from collections import defaultdict

import fiona
import geopandas as gpd
from shapely.geometry import mapping, shape
from shapely import make_valid

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
RESOURCES_DIR = BASE_DIR / 'border-resources'
OUTPUT_DIR = BASE_DIR / 'skyeye' / 'geojson'

# 坐标系定义
WGS84 = 'EPSG:4326'
CGCS2000_120E = 'EPSG:4549'  # CGCS2000 3度带 中央经线120E


# ==================== 工具函数 ====================

def detect_dbf_encoding(shp_path):
    """
    检测 .dbf 文件的字符编码。
    优先看 .cpg 文件，否则通过检测 .dbf 头部的语言驱动ID推断。
    """
    cpg_path = shp_path.with_suffix('.cpg')
    if cpg_path.exists():
        cpg = cpg_path.read_text().strip()
        if cpg.lower() in ('utf-8', 'utf8'):
            return 'utf-8'
        if cpg.lower() in ('gbk', 'gb2312', '936', 'ansi', 'oem'):
            return 'gbk'

    # 无 .cpg: 读取 .dbf 第29字节（语言驱动ID）
    dbf_path = shp_path.with_suffix('.dbf')
    if dbf_path.exists():
        try:
            with open(dbf_path, 'rb') as f:
                f.seek(29)
                lang_id = f.read(1)[0]
                # 0x57 = 87 = ANSI(GBK on Chinese systems), 0x00 = default
                if lang_id in (0x57, 0x00):
                    return 'gbk'
        except Exception:
            pass

    return 'utf-8'


def simplify_polygon(geom, tolerance=0.0001):
    """轻度简化 polygon 以减少文件体积"""
    try:
        from shapely import simplify
        return simplify(geom, tolerance=tolerance, preserve_topology=True)
    except Exception:
        return geom


def coords_to_geojson_polygon(geom):
    """将 shapely geometry 转为 GeoJSON 多边形坐标（6位精度）"""
    if geom is None:
        return []
    if not geom.is_valid:
        geom = make_valid(geom)
    geo = mapping(geom)
    if geo['type'] == 'MultiPolygon':
        return geo['coordinates']
    elif geo['type'] == 'Polygon':
        return [geo['coordinates']]
    return []


def get_center(geom):
    """获取多边形中心点"""
    if geom is None or geom.is_empty:
        return None
    centroid = geom.centroid
    return {'lng': round(centroid.x, 6), 'lat': round(centroid.y, 6)}


# ==================== 转换函数 ====================

def convert_county(shp_path, output_path):
    """转换县级边界"""
    print(f'[1/4] 转换县级边界: {shp_path.name}')
    enc = detect_dbf_encoding(shp_path)
    print(f'  编码: {enc}')

    features = []
    index_entries = {}
    total = 0

    with fiona.open(shp_path, encoding=enc) as src:
        for feat in src:
            props = feat['properties']
            geom = feat['geometry']
            if geom is None or geom.get('coordinates') is None:
                continue

            name = props.get('地名', '') or props.get('县级', '')
            code = props.get('区划码', '') or props.get('县级码', '')
            parent = props.get('地级', '')
            parent_code = props.get('地级码', '')
            province = props.get('省级', '')
            province_code = props.get('省级码', '')
            level_type = props.get('县级类', '')
            year = props.get('year', '')

            if not name:
                continue

            # 构造 GeoJSON Feature
            shp = shape(geom)
            geom_simple = simplify_polygon(shp)
            geo_mapping = mapping(geom_simple)

            features.append({
                'type': 'Feature',
                'properties': {
                    'name': name,
                    'code': code,
                    'level': 'county',
                    'level_type': level_type,
                    'parent': parent,
                    'parent_code': parent_code,
                    'province': province,
                    'province_code': province_code,
                    'year': year,
                    'center': get_center(shp),
                },
                'geometry': geo_mapping,
            })

            # 索引: 支持简称(去掉"区/县/市"后缀)和全名
            key_name = name
            short_name = name.rstrip('区县市')
            index_entries[key_name] = index_entries.get(key_name, []) + [len(features) - 1]
            if short_name != key_name:
                index_entries[short_name] = index_entries.get(short_name, []) + [len(features) - 1]

            total += 1

    # 写入 GeoJSON
    geojson = {'type': 'FeatureCollection', 'features': features}
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False)
    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f'  OK: {total} 条记录, {size_mb:.1f} MB')

    return index_entries


def convert_city(shp_path, output_path):
    """转换地市级边界"""
    print(f'[2/4] 转换地市级边界: {shp_path.name}')
    enc = detect_dbf_encoding(shp_path)
    print(f'  编码: {enc}')

    features = []
    index_entries = {}
    total = 0

    with fiona.open(shp_path, encoding=enc) as src:
        for feat in src:
            props = feat['properties']
            geom = feat['geometry']
            if geom is None or geom.get('coordinates') is None:
                continue

            name = props.get('地名', '') or props.get('地级', '')
            code = props.get('区划码', '') or props.get('地级码', '')
            province = props.get('省级', '')
            province_code = props.get('省级码', '')
            level_type = props.get('地级类', '')
            year = props.get('year', '')

            if not name:
                continue

            shp = shape(geom)
            geom_simple = simplify_polygon(shp)

            features.append({
                'type': 'Feature',
                'properties': {
                    'name': name,
                    'code': code,
                    'level': 'city',
                    'level_type': level_type,
                    'province': province,
                    'province_code': province_code,
                    'year': year,
                    'center': get_center(shp),
                },
                'geometry': mapping(geom_simple),
            })

            key_name = name
            short_name = name.rstrip('市')
            index_entries[key_name] = index_entries.get(key_name, []) + [len(features) - 1]
            if short_name != key_name:
                index_entries[short_name] = index_entries.get(short_name, []) + [len(features) - 1]

            total += 1

    geojson = {'type': 'FeatureCollection', 'features': features}
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False)
    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f'  OK: {total} 条记录, {size_mb:.1f} MB')

    return index_entries


def convert_village(shp_path, output_path):
    """转换江苏村界 (CGCS2000→WGS-84)"""
    print(f'[3/4] 转换江苏村界: {shp_path.name}')
    print(f'  坐标系: CGCS2000(4549) → WGS-84(4326)')
    enc = detect_dbf_encoding(shp_path)
    print(f'  编码: {enc}')

    features = []
    index_entries = {}
    total = 0
    skipped = 0

    with fiona.open(shp_path, encoding=enc) as src:
        src_crs = src.crs
        print(f'  原始 CRS: {src_crs}')

        for feat in src:
            props = feat['properties']
            geom = feat['geometry']
            if geom is None or geom.get('coordinates') is None:
                skipped += 1
                continue

            name = props.get('NAME', '')
            adcode = str(props.get('adcode', ''))
            cityname = props.get('cityname', '')
            adname = props.get('adname', '')
            entiid = props.get('ENTIID', '')

            if not name:
                skipped += 1
                continue

            shp = shape(geom)
            if shp is None or shp.is_empty:
                skipped += 1
                continue

            # 创建 GeoDataFrame 进行坐标变换
            gdf = gpd.GeoDataFrame(geometry=[shp], crs=src_crs)
            gdf_wgs84 = gdf.to_crs(WGS84)
            shp_wgs84 = gdf_wgs84.geometry[0]

            geom_simple = simplify_polygon(shp_wgs84)

            features.append({
                'type': 'Feature',
                'properties': {
                    'name': name,
                    'code': adcode,
                    'level': 'village',
                    'parent': adname,
                    'city': cityname,
                    'entiid': entiid,
                    'province': '江苏省',
                    'province_code': '320000',
                    'center': get_center(shp_wgs84),
                },
                'geometry': mapping(geom_simple),
            })

            key_name = name
            index_entries[key_name] = index_entries.get(key_name, []) + [len(features) - 1]

            total += 1
            if total % 5000 == 0:
                print(f'  进度: {total}...')

    geojson = {'type': 'FeatureCollection', 'features': features}
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False)
    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f'  OK: {total} 条记录, 跳过 {skipped}, {size_mb:.1f} MB')

    return index_entries


def convert_poi(shp_path, output_path):
    """
    POI 数据轻量导出，仅保留名称+坐标 (WGS-84)，按类别分组到多个文件。
    798K 条数据全部放一个文件太大，按 type 第一级分类拆分。
    """
    print(f'[4/4] 转换南京POI: {shp_path.name}')
    enc = detect_dbf_encoding(shp_path)
    print(f'  编码: {enc}')

    poi_by_category = defaultdict(list)
    total = 0
    skipped = 0

    with fiona.open(shp_path, encoding=enc) as src:
        for feat in src:
            props = feat['properties']
            geom = feat['geometry']
            if geom is None or geom.get('coordinates') is None:
                skipped += 1
                continue

            name = props.get('name', '')
            if not name:
                skipped += 1
                continue

            loc_x = props.get('locationx', 0)
            loc_y = props.get('locationy', 0)
            poi_type = props.get('type', '其他')
            category = poi_type.split(';')[0] if poi_type else '其他'

            if not loc_x or not loc_y:
                skipped += 1
                continue

            poi_by_category[category].append({
                'type': 'Feature',
                'properties': {
                    'name': name,
                    'type': poi_type,
                    'district': props.get('district', ''),
                    'address': props.get('address', ''),
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [float(loc_x), float(loc_y)],
                },
            })
            total += 1
            if total % 100000 == 0:
                print(f'  进度: {total}...')

    # 写入分类文件
    poi_dir = output_path.parent / 'poi'
    poi_dir.mkdir(parents=True, exist_ok=True)

    # 写一个总览文件（所有POI的name→坐标索引，不带geometry以缩小体积）
    poi_index = {}
    for category, features in poi_by_category.items():
        safe_cat = category.replace('/', '_').replace(' ', '_')
        cat_file = poi_dir / f'poi_{safe_cat}.geojson'
        geojson = {'type': 'FeatureCollection', 'features': features}
        with open(cat_file, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, ensure_ascii=False)
        print(f'  {safe_cat}: {len(features)} 条')

        for feat in features:
            poi_index[feat['properties']['name']] = {
                'category': category,
                'district': feat['properties']['district'],
                'coordinates': feat['geometry']['coordinates'],
            }

    # 写入索引
    index_file = poi_dir / 'poi_index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(poi_index, f, ensure_ascii=False)

    print(f'  OK: 总计 {total} 条, 跳过 {skipped}, {len(poi_by_category)} 个分类')
    return {}


def build_index(all_indices):
    """构建总索引: {name: {file: str, feature_idx: int, level: str, ...}}"""
    index = {}
    for dataset_name, entries in all_indices.items():
        for name, feature_indices in entries.items():
            if name not in index:
                index[name] = []
            for fi in feature_indices:
                index[name].append({
                    'file': dataset_name + '.geojson',
                    'feature_idx': fi,
                })
    return index


# ==================== 主流程 ====================

def main():
    start_time = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f'输出目录: {OUTPUT_DIR}\n')

    all_indices = {}

    # 1. 县级边界
    county_shp = RESOURCES_DIR / '2024年县级边界' / '2024年初县级.shp'
    if county_shp.exists():
        all_indices['county_2024'] = convert_county(
            county_shp, OUTPUT_DIR / 'county_2024.geojson'
        )
    else:
        print(f'[1/4] 跳过: 县级边界文件不存在 ({county_shp})')

    # 2. 地市级边界
    city_shp = RESOURCES_DIR / '2024年地市级边界' / '2024年初地级.shp'
    if city_shp.exists():
        all_indices['city_2024'] = convert_city(
            city_shp, OUTPUT_DIR / 'city_2024.geojson'
        )
    else:
        print(f'[2/4] 跳过: 地市级边界文件不存在 ({city_shp})')

    # 3. 江苏村界
    village_shp = RESOURCES_DIR / '江苏村界' / '江苏省行政村.shp'
    if village_shp.exists():
        all_indices['village_jiangsu'] = convert_village(
            village_shp, OUTPUT_DIR / 'village_jiangsu.geojson'
        )
    else:
        print(f'[3/4] 跳过: 村界文件不存在 ({village_shp})')

    # 4. 南京POI
    poi_shp = RESOURCES_DIR / 'NJPOI_2022' / 'NJPOI_2022.shp'
    if poi_shp.exists():
        convert_poi(poi_shp, OUTPUT_DIR / 'poi_nanjing.geojson')
    else:
        print(f'[4/4] 跳过: POI文件不存在 ({poi_shp})')

    # 5. 生成索引
    print(f'\n[索引] 生成 index.json ...')
    index = build_index(all_indices)
    index_path = OUTPUT_DIR / 'index.json'
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False)
    print(f'  共 {len(index)} 个地名索引, {index_path.stat().st_size / 1024:.1f} KB')

    # 6. 生成元信息
    meta = {
        'version': '1.0',
        'datasets': {
            'county_2024': {'level': 'county', 'crs': 'EPSG:4326',
                            'source': '2024年初全国县级行政边界'},
            'city_2024': {'level': 'city', 'crs': 'EPSG:4326',
                          'source': '2024年初全国地市级行政边界'},
            'village_jiangsu': {'level': 'village', 'crs': 'EPSG:4326',
                                'source': '江苏省行政村边界 (七普数据 2020)'},
            'poi/nanjing': {'level': 'poi', 'crs': 'EPSG:4326',
                            'source': '南京市POI 2022'},
        },
    }
    with open(OUTPUT_DIR / 'meta.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start_time
    print(f'\n=== 完成 === 耗时 {elapsed:.1f}s')
    return 0


if __name__ == '__main__':
    sys.exit(main())
