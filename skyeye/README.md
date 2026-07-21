# SkyEye 后端

无人机智能监管平台 Django 服务，集成 DeepSeek 大模型 AI 智能助手。

> **Phase 11** — 移除高德 API 依赖，纯本地 GeoJSON 查询

## AI 助手 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `chat_completions` | POST (SSE) | 流式对话，支持工具调用 |
| `geocode` | GET | 地名地理编码（本地 GeoJSON 查询） |
| `district` | GET | 行政区划边界（GeoJSON 本地查询） |

### 三种模式

| 模式 | 功能 |
|------|------|
| 聊天模式 | 自由对话 + 导航定位 + 页面跳转 + 任务查询 |
| 数据查询模式 | 检索系统线索/图斑/批次 + 数据统计 + 导航定位 |
| 智能摘要模式 | 当前页面综合摘要 + 风险评估 + 进度跟踪 + 决策建议 |

### 工具列表

| 工具 | 功能 |
|------|------|
| `navigate_page` | 跳转系统页面（18 条路由映射，含 AI 设置页） |
| `map_action` | 地图定位 + 区域边界绘制（GeoJSON polygon / 中心点定位） |
| `query_data` | 查询系统数据（数量/状态/统计/列表/明细） |
| `lookup_task` | 按任务编号查询并跳转 |

### 行政区划查询

纯本地 GeoJSON 查询，零外部 API 依赖：
- `geojson/` 目录：`city_2024.geojson`(690 地市) + `county_2024.geojson`(5651 县区) + `village_jiangsu.geojson`(22841 江苏村)
- 模块级内存缓存，首次加载后常驻
- 管理命令：`python manage.py preload_districts`（验证索引状态）

**数据转换工具**：`scripts/convert_to_geojson.py` — Shapefile → GeoJSON，支持 CGCS2000→WGS-84 坐标转换

**已知限制**：省级和乡镇级 GeoJSON 无覆盖，查询返回 None 由 LLM 文字回复引导。

## 安装教程

```
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```

## 配置

编辑 `config.ini`：

```ini
[deepseek]
api_key = your_deepseek_key
api_url = https://api.deepseek.com/v1
model = deepseek-chat
```

## Celery 启动

```bash
celery -A gtus.celery_config worker -l info -c 1
```
