# SkyEye 后端

无人机智能监管平台 Django 服务，集成 DeepSeek 大模型 AI 智能助手。

> **Phase 8** — 前端 Design Token 体系化 & Surface 深度层次 & WCAG 无障碍（后端无变更）

## AI 助手 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `chat_completions` | POST (SSE) | 流式对话，支持工具调用 |
| `geocode` | GET | 地名地理编码（高德 API + 自动全国兜底） |
| `district` | GET | 行政区划边界（GeoJSON本地 → 高德缓存 → 高德API三级查询） |

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
| `map_action` | 地图定位 + 区域边界绘制（支持重心定位/有polygon边界/无polygon兜底） |
| `query_data` | 查询系统数据（数量/状态/统计/列表/明细） |
| `lookup_task` | 按任务编号查询并跳转 |

### 行政区划缓存

三级查询体系：
1. **GeoJSON 本地** (一级)：`geojson/` 目录，覆盖全国 690 地市 + 5651 县区 + 江苏省 22841 村，模块级常驻内存
2. **高德缓存** (二级)：`district_cache.json` 文件 + 内存双缓存，命中即返回
3. **高德 API** (三级)：实时查询 + 自动写入缓存

**数据转换工具**：`scripts/convert_to_geojson.py` — Shapefile → GeoJSON，支持 CGCS2000→WGS-84 坐标转换

**已知限制**：乡镇级（镇/乡/街道）GeoJSON 无覆盖，降级到高德 API 仅返回中心坐标无 polygon 边界。

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

[amap]
api_key = your_amap_key
```

## Celery 启动

```bash
celery -A gtus.celery_config worker -l info -c 1
```
