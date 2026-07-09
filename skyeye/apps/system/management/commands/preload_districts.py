"""
预加载江苏省行政区划边界到本地缓存
用法: python manage.py preload_districts
"""
from django.core.management.base import BaseCommand
from utils_tools.district_cache import preload_jiangsu_all


class Command(BaseCommand):
    help = '预加载江苏省所有城市及区县边界到 district_cache.json'

    def handle(self, *args, **options):
        self.stdout.write('开始预加载...（约 3~5 分钟）')
        total = preload_jiangsu_all()
        self.stdout.write(self.style.SUCCESS(f'完成！共 {total} 个区县'))
