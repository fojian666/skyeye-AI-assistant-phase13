"""
验证 GeoJSON 行政区划索引状态
用法: python manage.py preload_districts
"""
from django.core.management.base import BaseCommand
from utils_tools.district_cache import query_district


class Command(BaseCommand):
    help = '验证 GeoJSON 行政区划索引是否正常加载'

    def handle(self, *args, **options):
        self.stdout.write('验证 GeoJSON 索引...')

        # 触发索引加载
        result = query_district('南京市')
        if result:
            self.stdout.write(self.style.SUCCESS(
                f'索引正常 — 南京市: {result["name"]}, {len(result["sub_regions"])} 个子区域'
            ))
        else:
            self.stdout.write(self.style.ERROR('索引加载失败，请检查 geojson/ 目录'))

        # 测试几个典型地名
        for name in ['鼓楼区', '玄武区', '栖霞区', '海门区', '广陵区']:
            r = query_district(name, city='南京')
            status = 'OK' if r else 'MISS'
            self.stdout.write(f'  {name}: {status}')
