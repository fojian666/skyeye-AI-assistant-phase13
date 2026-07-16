# 金陵阡陌（SkyEye）— 低空遥感智能巡检平台

> **Phase 6.5** — 多会话管理 · 提示词模板 · 响应式缩放 · 微交互动画 · 鲁棒性加固

## 项目概述

金陵阡陌（SkyEye）是一个基于低空遥感与无人机技术的智能巡检平台，集成了 **GIS 地图（2D/3D）**、**全景图像分析**、**AI 目标检测**、**航线规划**、**图斑变化检测** 等核心功能。平台通过 **DeepSeek 大模型** 提供 AI 智能助手，支持自然语言驱动地图定位、区域圈定、页面跳转（含 AI 设置页）、任务查询和数据检索。

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Vue 2 + Element UI | SPA 应用 |
| 2D 地图 | Leaflet | 开源轻量 GIS |
| 3D 地图 | Cesium | 三维地球引擎 |
| 全景图 | Pannellum | 浏览器全景渲染 |
| 动效 | GSAP + WebGL Shader + CSS Animation | 面板动画 / 极光背景 / 呼吸光斑 / 消息交错入场 |
| 图表 | ECharts | 数据可视化 |
| 设计 Token | CSS 自定义属性 (clamp 响应式缩放) | `--rail-width` / `--conv-list-width` / 百分比布局 |
| 持久化 | localStorage | AI 设置项 + 会话历史 + 提示词模板 |
| 后端框架 | Django | Python Web 框架 |
| 大模型 | DeepSeek (LangChain + LangGraph) | AI 对话与工具调用 |
| 流式输出 | SSE (Server-Sent Events) | real-time 阶段反馈 |
| 地理编码 | 高德地图 API | 地名 → 坐标 / 行政区边界 |
| 实时通信 | MQTT + WebSocket | 无人机遥测数据 |
| 数据库 | PostgreSQL | config.ini 配置连接 |

---

## 项目结构

```
skyeye/
├── README.md
├── .gitignore
├── skyeye/                            # Django 后端
│   ├── manage.py                      # Django 管理入口
│   ├── config.py                      # 全局配置
│   ├── logger.py                      # 日志模块
│   ├── gen_computerlic.py             # 许可证生成
│   ├── config.ini                     # API Key / 数据库 配置（gitignore）
│   ├── district_cache.json            # 江苏省 13 市 95 区县多边形缓存
│   ├── apps/
│   │   ├── system/                    # 系统管理 + AI Chat API
│   │   │   ├── views.py              # ★ chat_completions（SSE 流式）+ geocode + district
│   │   │   ├── urls.py               # API 路由
│   │   │   ├── models.py
│   │   │   └── serialirzers.py
│   │   ├── drone_track/              # 无人机轨迹（MQTT + WebSocket Channels）
│   │   │   ├── consumers.py          # WebSocket 消费者
│   │   │   ├── mqtt_drone_sub.py     # MQTT 订阅
│   │   │   └── routing.py            # WebSocket 路由
│   │   ├── experience/               # 体验模块
│   │   └── interpretation/           # AI 解译分析（最大模块）
│   │       ├── ai_analysis/
│   │       │   ├── function_api.py          # AI 功能入口
│   │       │   ├── change_detection/        # 变化检测（BIT 算法）
│   │       │   ├── data_process/            # 遥感预处理（大气校正/辐射定标/融合/裁剪）
│   │       │   └── image_segmentation/      # 图像分割（MMSegmentation）
│   │       └── urls.py
│   └── utils_tools/
│       ├── common.py                 # 通用工具
│       ├── utils.py                  # 工具函数
│       ├── authentication.py         # 认证模块
│       ├── district_cache.py         # 行政区划缓存
│       ├── oss_module.py             # OSS 对象存储
│       └── verify_license.py         # 许可证验证
│
└── skyeye-ui/                         # Vue 前端
    ├── README.md                      # 前端详细文档（Phase 5 更新）
    ├── src/
    │   ├── App.vue                    # 根组件
    │   ├── main.js                    # 入口
    │   ├── router/index.js            # 路由配置
    │   ├── store/                     # Vuex 状态管理
    │   │   ├── index.js               # store 入口（主题切换）
    │   │   ├── user.js                # 用户状态
    │   │   └── filter.js              # 筛选器状态
    │   ├── layout/                    # 布局框架
    │   │   ├── index.vue              # 主布局（Header + 侧栏 + 内容区 + ChatModel）
    │   │   └── components/
    │   │       ├── Header.vue         # 顶部导航
    │   │       ├── ChangePassword.vue # 修改密码
    │   │       ├── UserManagement.vue # 用户管理
    │   │       └── 404.vue            # 404 页面
    │   ├── components/                # 公共组件
    │   │   ├── chat/ChatModel.vue     # ★ AI 助手悬浮窗（Liquid Glass 双层玻璃 + 导航闭环）
    │   │   ├── panoramaViewer/        # 全景查看器
    │   │   ├── sceneLayer/            # 场景图层管理器
    │   │   ├── smallMap/              # 小地图
    │   │   ├── virtual-list/          # 虚拟列表
    │   │   └── ...                    # 查询/分页/下载/颜色选择器等
    │   ├── api/                       # 接口封装
    │   │   ├── request.js             # Axios 封装
    │   │   ├── commonApi.js           # 通用接口
    │   │   ├── taskMgmtApi.js         # 任务管理接口
    │   │   └── userAPi.js            # 用户接口
    │   ├── utils/                     # 工具函数
    │   │   ├── authUtil.js            # 认证工具
    │   │   ├── login.js               # 登录逻辑
    │   │   ├── utils.js               # 通用工具
    │   │   ├── panoramaTools.js       # 全景工具
    │   │   ├── MovingMarker.js        # 移动标记
    │   │   └── ...                    # 流播放器/矢量样式/地图加载等
    │   ├── views/
    │   │   ├── aiSettings/            # ★ AI 助手设置页（Liquid Glass + WebGL 极光 + 呼吸光斑）
    │   │   ├── home/                  # 首页
    │   │   ├── login/                 # 登录
    │   │   ├── dashboard/             # 仪表盘
    │   │   ├── portal/                # 门户入口
    │   │   ├── dataManagement/        # 数据管理（一张图 2D/3D + 全景影像 + 订单管理）
    │   │   ├── resource-center/       # 资源中心（概览/目录/登记/系统管理/机巢/日志/模型）
    │   │   ├── panoramicDetection/    # 全景检测（核心模块：检测/核查/报告/统计/场景/网格/任务）
    │   │   ├── intelligentMonitoring/  # 智能监控（目标检测/全景拼接/卫星检测/视频检测）
    │   │   ├── intelligent/           # 智能解译（地类变化/分割/处理分析）
    │   │   ├── clueVerify/            # 线索核查
    │   │   ├── pattern-verifiy/       # 图斑核实
    │   │   ├── taskManagementModule/  # 任务管理（任务列表/核查/数据上传）
    │   │   ├── routePlanning/         # 航线规划（算法/手动/全景）
    │   │   ├── liveMonitor/           # 实时监控
    │   │   ├── statisticHome/         # 统计首页
    │   │   ├── statisticalAnalysis/   # 统计分析
    │   │   ├── algorithm-mall/        # 算法商城
    │   │   ├── videoDetection/        # 视频检测
    │   │   ├── videoStreaming/        # 视频流
    │   │   ├── panoramaView/          # 全景查看
    │   │   └── mapScreenshot/         # 地图截图
    │   ├── css/                       # 全局样式
    │   │   └── theme/                 # 亮/暗主题（CSS 变量 + 设计 Token）
    │   ├── assets/                    # 静态资源（图标/图片/标记图标）
    │   ├── plugins/                   # 插件初始化（Element UI / Leaflet）
    │   ├── js/                        # 第三方 JS（ECharts / Leaflet 扩展）
    │   └── less/                      # 字体
    └── public/
        ├── config/config.js           # ★ 运行时配置（baseUrl / 全景图 / 地图服务等）
        ├── static/Cesium/             # Cesium 3D 引擎
        └── theme/                     # 亮色/暗色主题 CSS
```

---

## AI 智能助手

### 入口

右下角悬浮胶囊按钮，点击弹性弹出毛玻璃聊天面板。面板可拖拽移动、缩放、吸附为侧边栏。

### 三种模式

| 模式 | 功能 | 视觉 |
|------|------|------|
| **聊天模式** | 自由对话，通用问答 | 蓝色系 |
| **数据查询模式** | 检索系统线索、图斑、批次等数据 | 红色系 |
| **智能摘要模式** | 当前页面数据分析 | 金色系 |

点击侧边栏大圆按钮循环切换，切换时有 toast 提示当前模式及用途。模式色统一应用到面板边框 + 头部 + 底部 + 侧边栏按钮。

### 核心链路

```
用户输入 → DeepSeek 大模型 → Tool Call → 后端 SSE 流式返回 → 前端逐阶段展示
```

流式阶段：`🔍 理解问题 → 🗺️ 地理编码 → 📊 查询数据 → 🔎 查找任务 → ✍️ 生成回答`

### 工具列表

| 工具 | 功能 | 触发条件 |
|------|------|------|
| `navigate_page` | 跳转系统页面（含 AI 设置页） | 用户说出具体页面名称（"一张图""全景检测""航线规划"） |
| `map_action` | 地图定位 + 区域边界绘制 | 用户提及任何地点/区域/行政区名称 |
| `query_data` | 查询系统数据（数量/状态/统计/列表/明细） | 用户询问数据量、统计、状态、列表；"数据概览""当前页面" |
| `lookup_task` | 按任务编号查询并跳转 | 用户提供 batch_id 格式编号 |

> 四个工具互相引用 **禁止调用场景**（反例），消除歧义。后端 SYSTEM_PROMPT 新增 **工具冲突裁决规则**：`navigate_page` 不处理"数据概览""统计汇总""当前页面数据"；`map_action` 不处理页面名和统计类用语；`query_data` 不处理页面名和地名。

### 面板交互

| 特性 | 说明 |
|------|------|
| 流式输出 | SSE 实时显示处理阶段，打字机逐字渲染 Markdown |
| 减少动效 | 头部按钮切换，关闭呼吸光晕/WebGL，跳过打字机直接渲染全文 |
| 停止生成 | 红色胶囊按钮，支持中止请求和打字输出 |
| 重试 | 出错/中断后一键重发最后一条消息 |
| 复制回答 | hover 显示复制按钮，点击后"已复制"提示 |
| 清空对话 | 确认弹窗防误操作，不可撤销 |
| 保留会话 | 关闭窗口不丢失历史 |
| 拖拽 | FAB / 面板头部均可拖拽，边界碰撞检测 |
| 缩放 | 右下角拖拽把手，宽 360–35vw，高 400–85vh（全部 clamp 响应式） |
| 吸附 | 点 → 吸附为全高右栏，← 恢复浮动 |
| Double-Bezel | 外层托盘壳 (panel-shell) + 内核 (chat-panel) 同心圆角，硬件质感 |
| 侧边栏 | 左侧 hover 展开：会话列表 / 模式切换 / 系统设置 |
| 会话列表 | 点击侧边栏顶部按钮滑出，新建/切换/删除会话，首条消息自动标题，localStorage 持久化 |
| 删除确认 | 清空对话 + 删除会话均弹 $confirm 防误操作 |
| 快速提问 | 欢迎页常用问题卡片一键发送（可从设置页自定义模板） |
| 主题适配 | 亮色/暗色自动适配（同步 data-theme 属性） |
| 无障碍 | focus-visible 键盘导航、aria-label 全覆盖、prefers-reduced-motion 系统级兜底 |
| 并发锁 | 三层防护：动画锁(模式切换/dock 300ms) + 发送锁(防重复提交) + streaming watcher 自动释放 |
| 多模式气泡 | 用户消息气泡随 chat(蓝)/query(红)/summary(琥珀) 模式变色，亮暗双主题适配 |
| 消息入场 | msgSlideIn 交错 60ms 滑入 + dot-pulse 呼吸替代 bounce |

### AI 设置页

路由 `/ai-settings`，从 AI 助手面板头部 ⚙ 按钮或 LLM 意图推理（"打开设置"）进入，返回自动恢复聊天面板（sessionStorage 闭环）。

| 设置项 | 说明 |
|--------|------|
| 模型选择 | DeepSeek-V3 (通用) / DeepSeek-R1 (推理) |
| Temperature | 0 ~ 2.0，精确 ↔ 创造，四段色温映射 |
| 最大输出长度 | 512 ~ 8192 tokens，预览条可视化 |
| 深色主题 | 亮色/暗色主题切换 |
| 减少动态效果 | 关闭 CSS 光斑 + WebGL + 打字机动画 |
| 默认模式 | 自由对话 / 数据查询 / 智能摘要 |
| 自动摘要 | 进入页面时自动触发摘要 |
| 提示词模板 | 三模式独立 3-5 条可编辑模板，localStorage 持久化，自由对话/数据查询/智能摘要各一套默认 |

**数据流**：设置页 ↔ localStorage (`skyeye_ai_settings`) ↔ ChatModel ↔ 后端 `chat_completions` API

### 多会话管理

| 特性 | 说明 |
|------|------|
| 会话列表 | 侧边栏顶部按钮滑出面板，吸附在 side-rail 左侧，与 chat-panel 等高三栏布局 |
| 新建会话 | 蓝色虚线按钮，最多 20 个会话，超出上限禁用新建 |
| 切换会话 | 点击切换，自动保存当前会话 → 加载目标会话 messages（含流式 abort 保护） |
| 删除会话 | 红色 × 按钮 + $confirm 确认弹窗，删除活跃会话自动切到前一个 |
| 标题自动生成 | 取首条用户消息截断 20 字，空会话显示"新对话" |
| 数据迁移 | 向前兼容旧的单会话 key `skyeye_chat_history` → 自动转 `skyeye_conversations` |
| 持久化 | conversations deep watch → 1s 防抖 → localStorage，恢复时优先读新 key |
| 列表动画 | convItemIn 交错 40ms 淡入 + translateX，打开面板时 staggered reveal |

### Phase 5 视觉增强

| 效果 | 技术 | 说明 |
|------|------|------|
| 动态极光 | WebGL Ether Shader | GPU 并行渲染，暗色主题专用 |
| 呼吸光斑 | CSS `@keyframes pulse` × 3 | 蓝/紫/粉交错 4s 周期，blur(80px) |
| 噪点纹理 | CSS `background-image` SVG data URI | 透明度 0.025，磨砂质感 |
| Liquid Glass | Double-Bezel + backdrop-filter blur | panel-shell(20px) + chat-panel(40px) / pod-shell(12px) + pod-core(40px) |
| 自定义 Tooltip | CSS `attr(data-tip)` + `::after` 气泡 | 防裁剪、防出界右对齐 |
| 智能滚动 | `_userScrolledUp` 检测 | 打字机跟随，手动上翻停止 + 回到底部按钮 |

### Phase 6 鲁棒性 & 交互增强

| 改进 | 类型 | 说明 |
|------|------|------|
| 组件销毁清理 | 鲁棒性 | `beforeDestroy` 中 AbortController.abort() / GSAP killTweensOf / 定时器清理 / WebGL rAF 取消 |
| fetch 60s 硬超时 | 鲁棒性 | setTimeout + AbortController，防止请求永久挂起 |
| 打字机生命周期保护 | 鲁棒性 | `_typewriterCancelled` 标志防止对已销毁组件赋值 |
| JSON.parse 保护 | 鲁棒性 | LLM 畸形参数 → 捕获并显示友好错误气泡，不死锁 streaming |
| `_friendlyError` | 鲁棒性 | 8 种错误 → 8 条中文友好文案（AbortError / 网络异常 / 500/502/503 / 401/403 / 404 / 429 / 兜底）|
| `_storageError` 可重置 | 鲁棒性 | 存储恢复后警告横幅自动消失；双通道独立标记（设置项 + 对话） |
| `savePrefs` 300ms 防抖 | 鲁棒性 | 快速拖 slider 只写一次 localStorage |
| SSE 流边界保护 | 鲁棒性 | 非 JSON 行静默跳过 / phase=error 不中断流 / buffer 截断保留 / done 未收到兜底消息 |
| 工具冲突裁决 | 交互 | 四工具互相引反例 + 后端 5 条裁决规则；消除"数据概览→跳页"歧义 |
| 三层并发锁 | 交互 | 动画锁(300ms) + 发送锁 + streaming watcher 自动释放；防止快速切换/重复提交 |
| 多模式用户气泡 | 视觉 | chat(蓝) / query(红) / summary(琥珀) 用户消息气泡变色，亮暗双主题 |
| 输入防护 | 鲁棒性 | textarea maxlength 5000 + 提示、trim 空消息拦截 |
| eyeType 修复 | UI | eyebrow 去 uppercase + 字号 11→12px + letter-spacing 收紧 |
| 消息入场动画 | 视觉 | msgSlideIn 交错 60ms 滑入 + dot-pulse 呼吸替代 bounce；convItemIn 交错 40ms 淡入 |
| 面板 GSAP 优化 | 性能 | duration 0.5s → 0.3s，符合 product register 150-300ms 范围 |
| clamp 响应式缩放 | 适配 | 全部尺寸 (panel/side-rail/conv-list/font/input/button/chat-fab) 使用 clamp() + CSS 变量联动 |
| 主题同步修复 | 修复 | App.vue `data-theme` setAttribute + ChatModel 主题 class 双路径同步 |

### 地图导航

- 后端调高德 `geocode` API → 地名 → 经纬度 + 完整地址
- 前端 `navigate-map` 事件 → 地图 `flyTo()` 平滑飞行动画
- 自动缩放适配区域边界，确保完整显示

### 区域圈定

- 后端调高德 `config/district` API → polygon 边界坐标
- 输入"南京市"自动获取 11 个区的独立边界，各分配不同颜色
- 前端 `draw-region` 事件：主区域半透明底，子区域彩色填充 + 描边
- 再次触发自动清除上一轮图层

### 行政区划缓存

- 预加载江苏省 13 市 95 区县的多边形边界 → `district_cache.json`
- 模块级内存缓存，首次加载后常驻，后续零磁盘 IO、零 API 调用
- 管理命令：`python manage.py preload_districts`

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

编辑 `skyeye/config.ini`（已 gitignore）：

```ini
[deepseek]
api_key = your_deepseek_key
api_url = https://api.deepseek.com/v1
model = deepseek-chat

[amap]
api_key = your_amap_key
```

### 运行时配置（前端）

部署时修改 `skyeye-ui/public/config/config.js` 中的 `baseUrl` 等字段即可切换 API 地址，无需重新构建。

---

## 未提交内容（.gitignore 排除清单）

| 类别 | 文件/目录 | 说明 |
|------|----------|------|
| 密钥 | `skyeye/config.ini` | DeepSeek / 高德 API Key / 数据库连接 |
| 依赖 | `node_modules/` | npm 包（`npm install` 安装） |
| 构建产物 | `dist/` `build/` | 前端打包输出 |
| Python 缓存 | `__pycache__/` `*.pyc` `*.pyo` `*.egg-info/` | 字节码 / 包元数据 |
| 测试文件 | `test*.py` `*_test.py` `tests/` `*.spec.js` `*.test.js` `*.spec.ts` `*.test.ts` `__tests__/` | 单元测试 |
| SQL | `*.sql` | 数据库脚本 |
| 影像/视频 | `*.tif` `*.mp4` | 影像视频文件 |
| 模型权重 | `*.bin` `*.pth` `*.th` | 二进制模型文件 |
| 多媒体 | `*.swf` `*.air` `*.ipa` `*.apk` | Flash / 移动应用包 |
| 运行时产物 | `skyeye/static/shp/` `skyeye/static/route_jobs/` `skyeye/static/route_plan/` `skyeye/static/layers/` | 地理数据 / 航线缓存 / 图层 |
| 日志 | `*.log` `logs/` `dev-server.log` | 运行日志 |
| IDE | `.idea/` `.vscode/` `*.suo` `*.sln` | 编辑器个人配置 |
| 系统 | `.DS_Store` `Thumbs.db` | OS 生成文件 |

---

## 许可证

内部使用项目
