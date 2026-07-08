# 天巡 SkyEye — 低空遥感智能巡检平台

## 项目概述

天巡（SkyEye）是一个基于低空遥感和无人机技术的智能巡检平台，集成了 **GIS 地图（2D/3D）**、**全景图像分析**、**AI 目标检测**、**航线规划**、**图斑变化检测**、**资源管理** 等核心功能。  
平台通过 **DeepSeek 大模型** 提供 AI 智能助手，支持自然语言驱动地图导航、区域圈定、页面跳转等操作。

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Vue 2 + Element UI | SPA 应用 |
| 前端构建 | Vue CLI + Webpack | — |
| 2D 地图 | Leaflet | 开源轻量 GIS |
| 3D 地图 | Cesium | 三维地球引擎 |
| 全景图 | Pannellum | 浏览器全景渲染 |
| 动画库 | GSAP | 高性能 JS 动画 |
| 图表 | ECharts | 数据可视化 |
| 后端框架 | Django | Python Web 框架 |
| 大模型 | DeepSeek (LangChain + LangGraph) | AI 对话与工具调用 |
| 地理编码 | 高德地图 API | 地名 → 坐标 / 行政区边界 |
| 实时通信 | MQTT + WebSocket | 无人机遥测数据 |
| 数据库 | MySQL | — |

---

## 项目结构

```
skyeye/
├── README.md                     # 本文档
├── .gitignore                    # 忽略 config.ini / *.sql / node_modules 等
├── skyeye/                       # Python/Django 后端
│   ├── apps/
│   │   ├── system/               # 系统管理（用户/菜单/角色）+ AI Chat API
│   │   │   ├── views.py          # ★ chat_completions / geocode / district
│   │   │   ├── urls.py           # API 路由
│   │   │   ├── models.py
│   │   │   └── serialirzers.py
│   │   ├── drone_track/          # 无人机轨迹（MQTT + WebSocket）
│   │   ├── experience/           # 体验模块
│   │   └── interpretation/       # AI 解译分析
│   └── config.ini                # API Key 配置（gitignore）
│
├── skyeye-ui/                    # Vue 前端
│   ├── src/
│   │   ├── components/
│   │   │   └── chat/
│   │   │       └── ChatModel.vue # ★ AI 助手悬浮窗组件
│   │   ├── views/
│   │   │   ├── dataManagement/oneMap/       # 一张图（2D/3D）
│   │   │   ├── routePlanning/              # 航线规划
│   │   │   ├── panoramicDetection/         # 全景检测
│   │   │   ├── intelligentMonitoring/      # 智能监测
│   │   │   ├── pattern-verifiy/            # 图斑核实
│   │   │   └── ...                         # 其他 20+ 模块
│   │   ├── router/index.js    # 路由配置
│   │   ├── store/             # Vuex 状态管理
│   │   ├── layout/            # 布局（Header/侧栏/主题切换）
│   │   ├── api/               # 接口封装
│   │   └── utils/             # 工具函数
│   └── public/
│       ├── static/Cesium/     # Cesium 3D 引擎
│       └── theme/             # 亮色/暗色主题 CSS
```

---

## AI 智能助手

### 入口

右下角悬浮 **胶囊形按钮**（🤖 AI 助手），点击弹性弹出毛玻璃聊天面板。

### 核心链路

```
用户输入 → DeepSeek 大模型 → Tool Call → 后端执行 → 前端响应事件
```

### 工具列表

| 工具名 | 功能 | 调用条件 |
|------|------|------|
| `navigate_page` | 跳转系统页面 | 用户要求跳转 |
| `map_action` | 地图定位 + 区域边界绘制 | 用户提及任何地点/区域 |
| `query_data` | 查询系统数据 | 用户询问数据 |

### 路由映射

AI 选择简短路径，前端自动补全到真实路由：

| AI 路径 | 实际跳转 |
|------|------|
| `/task-mgmt` | `/task-mgmt/verify-clue` |
| `/data-management` | `/data-management/one-map` |
| `/route-planning` | `/route-planning/manual-planning` |
| `/panoramic-detection` | `/panoramic-detection/task-management` |
| `/pattern-verifiy` | `/pattern-verifiy/map_overview` |
| `/data_overview` | `/data_overview` |

### 地图导航

- 后端调高德 `geocode` API → 地名 → 经纬度
- 前端 `navigate-map` 事件 → 2D Map `flyTo()` / 3D Map `camera.flyTo()`
- 平滑飞行动画

### 区域圈定

- 后端调高德 `config/district` API → 地名 → polygon 边界坐标
- 前端 `draw-region` 事件 → 2D `L.polygon()` / 3D `viewer.entities.add({ polygon })`
- 同步执行 `navigate-map`，定位到区域中心

### 主题适配

Header 切换亮色/暗色时：
- `App.vue` → `document.documentElement.setAttribute('data-theme', theme)`
- ChatModel 通过 `html[data-theme='light']` CSS 选择器适配
- algorithmPlanning 侧栏同理

### 组件特性

| 特性 | 说明 |
|------|------|
| 毛玻璃 | `backdrop-filter: blur(24px)` 半透明面板 |
| GSAP 动画 | 打开弹性弹出 `back.out(1.7)` |
| 拖拽 | fab / 面板头部均可拖拽 |
| 右侧吸附 | 点 `→` 吸附为全高右边栏，`←` 恢复浮动 |
| 关闭 | 即时消失，无残留黑条 |

---

## 运行说明

### 前端

```bash
cd skyeye-ui
npm install
npm run serve        # 开发模式，默认 http://localhost:8088
```

### 后端

```bash
cd skyeye
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```

### 配置

编辑 `skyeye/config.ini`：

```ini
[deepseek]
api_key = your_deepseek_key
api_url = https://api.deepseek.com/v1
model = deepseek-chat

[amap]
api_key = your_amap_key
```

> `config.ini` 已加入 `.gitignore`，不会提交到仓库。

---

## 许可证

内部使用项目
