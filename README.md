# 金陵阡陌（SkyEye）— 低空遥感智能巡检平台

> **Phase 13** — POI 点位查询与地图标记 · 移除自动摘要 · 地名模糊匹配修复 · 暗色灵动岛修复 · 时钟冻结修复

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
| 设计 Token | CSS 自定义属性 (cyber-tokens + ai-tokens) | `--ai-text-*` / `--ai-glass-*` / `--ai-mode-*` 语义体系 |
| 持久化 | localStorage | AI 设置项 + 会话历史 + 提示词模板 |
| 后端框架 | Django | Python Web 框架 |
| 大模型 | DeepSeek (LangChain + LangGraph) | AI 对话与工具调用 |
| 流式输出 | SSE (Server-Sent Events) | real-time 阶段反馈 |
| 地理编码 | 本地 GeoJSON | 地名 → 坐标 / 行政区边界（690 地市 + 5651 县区 + 22841 村） |
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
│   ├── district_cache.json            # 行政区域缓存（内存+文件双重）
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

点击侧边栏大圆按钮循环切换，或从灵动岛下拉面板操作。模式色统一应用到灵动岛圆点 + 面板边框 + 底部 + 侧边栏按钮 + 下拉面板。

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
| 灵动岛 | 32px 纯色实心圆 → hover 展开胶囊 "● 金陵阡陌 ▾" → 点击弹出下拉控制面板（5 个操作按钮） |
| iOS 状态栏 | 时间 + 信号/WiFi/电池 SVG 图标，与灵动岛同行 |
| 流式输出 | SSE 实时显示处理阶段，打字机逐字渲染 Markdown |
| 减少动效 | 灵动岛下拉面板按钮切换，关闭呼吸光晕/WebGL，跳过打字机直接渲染全文 |
| 停止生成 | 红色胶囊按钮，中止请求：有部分文本追加 `…[已停止]` + 重试，无文本显示"已停止生成"保持对话完整 |
| 重试 | 出错/中断后一键重发最后一条消息 |
| 复制回答 | hover 显示复制按钮，点击后"已复制"提示 |
| 清空对话 | 确认弹窗防误操作，不可撤销 |
| 保留会话 | 关闭窗口不丢失历史 |
| 拖拽 | 上半部分 (phone-top-section) 整体可拖拽，边界碰撞检测 |
| 四角缩放 | 四个角落均可拖拽缩放 (br/bl/tr/tl)，左上/左侧方向同步移动面板位置 |
| 吸附 | 点 → 吸附为全高右栏，← 恢复浮动 |
| 点击外部收起 | 点击 ChatModel 组件外部 → 自动返回 FAB 悬浮按钮（docked 模式下不触发） |
| Double-Bezel | 外层托盘壳 (panel-shell) + 内核 (chat-panel) 同心圆角，手机壳体质感 |
| 侧边栏 | 左侧 hover 展开：会话列表 / 模式切换 / 系统设置 |
| 会话列表面板 | 展开时与主面板无缝融合（统一背景/边框/光效），左侧无接缝、底部对齐 |
| 删除确认 | 清空对话 + 删除会话均弹 $confirm 防误操作 |
| 快速提问 | 欢迎页常用问题卡片一键发送（可从设置页自定义模板） |
| 主题适配 | 亮色/暗色自动适配（同步 data-theme 属性） |
| 无障碍 | focus-visible 键盘导航、aria-label 全覆盖、prefers-reduced-motion 系统级兜底 |
| 并发锁 | 三层防护：动画锁(模式切换/dock 300ms) + 发送锁(防重复提交) + streaming watcher 自动释放 |
| 多模式气泡 | 用户消息气泡随 chat(蓝)/query(红)/summary(琥珀) 模式变色，亮暗双主题适配 |
| 消息入场 | msgSlideIn 交错 60ms 滑入 + dot-pulse 呼吸替代 bounce |

### AI 设置页

路由 `/ai-settings`，从灵动岛下拉面板 ⚙ 按钮或 LLM 意图推理（"打开设置"）进入，返回自动恢复聊天面板（sessionStorage 闭环）。

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

### Phase 6.5 多会话 & 提示词模板 & 响应式缩放

| 效果 | 技术 | 说明 |
|------|------|------|
| 动态极光 | WebGL Ether Shader | GPU 并行渲染，暗色主题专用 |
| 呼吸光斑 | CSS `@keyframes pulse` × 3 | 蓝/紫/粉交错 4s 周期，blur(80px) |
| 噪点纹理 | CSS `background-image` SVG data URI | 透明度 0.025，磨砂质感 |
| Liquid Glass | Double-Bezel + backdrop-filter blur | panel-shell(20px) + chat-panel(40px) / pod-shell(12px) + pod-core(40px) |
| 自定义 Tooltip | CSS `attr(data-tip)` + `::after` 气泡 | 防裁剪、防出界右对齐 |
| 智能滚动 | `_userScrolledUp` 检测 | 打字机跟随，手动上翻停止 + 回到底部按钮 |

### Phase 7 液玻璃视觉重塑 & 引导式 Onboarding

| 改进 | 类型 | 说明 |
|------|------|------|
| 侧栏渐进式引导 | 交互 | 前 3 次打开面板展示圆点 + 文字标签（会话/对话/设置），大圆呼吸脉冲，localStorage 持久化计数，3 次后回归 hover-only |
| 引导重置入口 | 交互 | 设置页 actions-bar 新增"重新展示侧栏引导"按钮，`storage` 事件跨标签页实时同步 |
| 欢迎区重构 | 视觉 | 机器人图标居中 → 能力列表（3 条业务说明）→ 分割线 → 操作提示，双主题适配 |
| 深色模式液玻璃 | 视觉 | `panel-shell`/`chat-panel` 用径向光球 `::before`/`::after` 替代 `linear-gradient` 渐变，降低不透明度至 0.38–0.42 增强背景穿透感 |
| 亮色模式液玻璃 | 视觉 | 微渐变底色 `linear-gradient(135deg, 蓝→紫→粉)` + 淡光晕伪元素，解决"白上叠白"虚无感 |
| 定向光叠加层 | 视觉 | `panel-shell`/`chat-header`/`chat-footer`/`.assistant .msg-content` 各加 `::before` 线性光伪元素，模拟左上光线打在玻璃上的折射 |
| 玻璃折射高光线 | 视觉 | `box-shadow` 从单条 `inset` 改为双层（顶部高光 + 底部暗边），物理边缘感 |
| 输入框聚焦光环 | 视觉 | `chat-input-wrap:focus-within` 扩散光晕 + `scale(1.008)` 微缩放 |
| 消息气泡尺寸 | 视觉 | `max-width` 70%→85%，输入框 `font-size` 13→14px，`padding` 7→9px |
| 响应式硬约束 | 修复 | `max-width: calc(100vw - 64px)` 硬截断防止面板被挤出视口；resize 时重夹持 x/y 百分比 |
| fab badge 修复 | 修复 | 用 `lastReadMsgCount` 替代 `visible` 判断，关闭面板后不立即重亮；`watch.visible` 标记已读 |
| conv-list 动画对齐 | 修复 | `transition` 0.28s→0.02s 瞬关对齐面板动画；关闭面板时顺手 `convListVisible = false` |
| 参考项目借鉴 | 设计 | 借鉴 iOS 26 Liquid Glass Chatbot 的定向光渐变、玻璃折射边缘、聚焦光环等 4 个设计模式 |

### Phase 8 设计 Token 体系化 & Surface 深度层次

| 改进 | 类型 | 说明 |
|------|------|------|
| AI 语义 Token 体系 | 架构 | 新增 92 个 Token 8 大类：文本 6 级 / 玻璃表面 10 级 / 边框 4 级 / 模式色 9 级 / 光晕 4 级 / 模糊 5 级 / 交互状态 4 级 / 组件级 5 级 + 投影 3 级；亮暗双主题自动切换 |
| 硬编码值 Token 化 | 重构 | ChatModel (16) + aiSettings (51) 合计 67 处 `rgba`/`hex` 硬编码值替换为语义 Token，一处修改全局生效 |
| WCAG AA 对比度修复 | 无障碍 | aiSettings 暗色模式 16 处文本颜色提升至 ≥4.5:1 (正文) / ≥3:1 (辅助文字/placeholder) |
| 卡片 hover 抬升 | 视觉 | `.pod-shell:hover` 增加 `translateY(-2px)` + 投影加深至 `0 14px 44px` |
| 背景光斑滚动视差 | 视觉 | 3 个 bg-orb 以不同速率 (0.06x/0.08x/0.04x) 随滚动偏移，`requestAnimationFrame` 驱动 + reduceMotion 启停控制 |
| 消息区景深分层 | 视觉 | `.chat-body` 渐变背景 (浅→深)，模拟"近深远浅"玻璃折射 |
| 气泡顶部高光条 | 视觉 | `.msg-content::after` 1px 高光线，两端透明中间亮 |
| 发送按钮居中修复 | 修复 | `.chat-send-btn` 添加 `align-self: center` 覆盖父容器底部对齐 |

### Phase 9 FAB 数字徽章 & 侧栏液态灌满 & 光斑系统瘦身

| 改进 | 类型 | 说明 |
|------|------|------|
| FAB 新消息数字徽章 | 交互 | 红色圆点 → 数字胶囊（99+ 截断），显示未读消息数 |
| FAB 生成中呼吸微光 | 视觉 | 按 chat/query/summary 模式变色呼吸光效 (`fab-glow` 2s)，`reduce-motion` 禁用 |
| FAB grab 光标 + 按下反馈 | 微交互 | 默认 `grab` / 拖拽 `grabbing`，`:active` 缩放 0.95×、`focus-visible` 聚焦环 |
| 侧栏大圆"水面灌满" | 视觉 | `::before` 伪元素 `clip-path: inset(100% 0 0 0)` → hover 自下而上灌满纯色填充 |
| 侧栏 focus-visible | 无障碍 | 大圆/小圆 `outline: 3px solid color-mix(...)` 圆环聚焦轮廓 |
| 侧栏标签字体升级 | 视觉 | 字体 Plus Jakarta Sans / Geist / Inter，字号 11→12px，letter-spacing -0.01em |
| 回到底部胶囊化 | 视觉 | 圆形 36px → 胶囊 32px，hover 展开"最新"文字，SVG 16→14px |
| 切换会话保留列表 | 交互 | `switchConversation` 不再自动关闭会话列表面板 |
| 亮色侧栏模式色 | 视觉 | 亮色主题下查询/摘要模式大圆 background + border-color 按模式适配 |
| 过渡时长缩减 | 性能 | FAB/侧栏 hover/active transition 从 0.55s→0.35s，内耗项 0.25s→0.16s |
| 移除呼吸光斑系统 | 瘦身 | aiSettings 删除 3 个 `bg-orb` + `noise-overlay` + `@keyframes orb-breathe` + 滚动视差 rAF |
| 亮色模式氛围光替代 | 视觉 | `.light-gradient-overlay` 纯 CSS 渐变层（页面温度 + 右上自然光），零 JS 零动画 |

### Phase 10 页面装饰系统 & 滚动触发入场

| 改进 | 类型 | 说明 |
|------|------|------|
| 滚动词条装饰 | 视觉 | Hallmark Ft8 风格水平无限滚动跑马灯，页面顶部紧贴，三模式（indigo/red/amber）颜色联动，`backdrop-filter` 玻璃底座 + 双层边框 + 文字发光 `text-shadow`，`reduce-motion` 冻结 |
| 两侧氛围光斑 | 视觉 | 4 个固定定位高斯模糊光斑（左上 320px / 右上 260px / 右下 380px / 左侧中 220px），`filter: blur(100px)`，三模式颜色联动 1.2s 过渡，亮暗双主题适配，`pointer-events: none` + `aria-hidden` |
| 滚动触发布局入场 | 交互 | `IntersectionObserver` 替代全量一次性幕布揭示，5 张卡片在打字机完成后进入"可触发"状态，滚入视口（threshold 0.1 + rootMargin -8%）时逐个 `curtain-revealed`，one-shot `unobserve`，`reduceMotion` 直接全显示 |
| 静态资源补全 | 修复 | Leaflet/SuperMap CDN 文件从 `node_modules` 复制到 `public/static/lib/cdn/`，解决 404 加载错误 |

### Phase 11 三模式欢迎语 & 地图查询鲁棒性 & 停止生成补充

| 改进 | 类型 | 说明 |
|------|------|------|
| 三模式欢迎语区分 | 交互 | `chatMode` 联动欢迎区：对话模式（导航定位/页面跳转/任务查询/通用问答）、数据查询模式（数据统计/导航/跳转/任务）、摘要模式（综合摘要/风险评估/进度跟踪/决策建议），底部提示语随模式变化 |
| 手动停止对话补充 | 交互 | 有部分文本时追加 `…[已停止]` 后缀 + 重试按钮，无文本时插入"已停止生成"保持 user/assistant 交替结构，对话逻辑完整 |
| GeoJSON 本地缓存体系 | 性能 | Shapefile → GeoJSON 批量转换（`convert_to_geojson.py`），覆盖全国 690 地市 + 5651 县区 + 江苏省 22841 村级单位，纯本地查询零外部 API 依赖 |
| 省级查询跳过 | 设计 | 省级/直辖市（X省/X自治区/京沪津渝）GeoJSON 无覆盖，直接返回 None，LLM 文字回复引导 |
| GeoJSON 模糊匹配限制 | 修复 | `keywords in name` 匹配增加 `len(name) - len(keywords) <= 2` 约束，防止"江苏省"(3字) 误匹配"江苏省国营江心沙农场虚拟生活区"(14字) |
| 乡镇级重心定位 | 修复 | 无 polygon 但有 center 的查询（如"塔里木乡"）新增 `elif` 分支直接用中心坐标定位，不再静默跳过 |
| geocoding 城市限制兜底 | 修复 | 带 city="南京" geocoding 失败后自动重试全国搜索，解决非南京地区地名无法定位的问题 |
| 导航消息会话兼容 | 修复 | `_skipContext` 从过滤改为替换"收到"，保持 user/assistant 交替结构，避免 LLM 混淆回第一条历史查询 |
| 缓存脏数据清理 | 修复 | 删除 `district_cache.json` 中"江苏省|南京"→"江心沙农场"的错误缓存，重启 Django 内存缓存刷新 |

### Phase 12 灵动岛一体化 & 手机外壳 & 会话抽屉无缝融合

| 改进 | 类型 | 说明 |
|------|------|------|
| 灵动岛控制中枢 | 交互 | 移除 chat-header 行，所有头部功能收敛至灵动岛：32px 纯色实心圆（按模式蓝/红/琥珀）→ hover 展开胶囊 → 点击弹出下拉控制面板（动效/吸附/设置/清空/关闭 5 个按钮），模式色全联动 |
| iOS 状态栏 | 视觉 | 时间 + 信号/WiFi/电池 SVG 图标（源自 ContraQuest 项目 iOS 原生设计），与灵动岛同行 Flex 布局，3 个响应式断点适配 |
| 手机外壳外观 | 视觉 | panel-shell 三层设备级投影 + 定向光伪元素玻璃折射 + 边框 1.5px，模拟手机壳体质感 |
| 会话列表与面板一体化 | 视觉 | 展开时 conv-list-panel 与 panel-shell 共用背景/边框/光效，border-left: none 消除接缝，align-self: stretch 消除底部错位 |
| 四角缩放 | 交互 | 四个角落 (br/bl/tr/tl) 均可拖拽缩放，左侧/顶部方向同步移动面板位置，三角指示器暗/亮双主题适配 |
| 点击外部收起 | 交互 | document mousedown 检测 .chat-wrapper 外部点击 → closeChat() 返回 FAB，与灵动岛下拉关闭共用事件，docked 模式不触发 |
| 欢迎区灵动岛引导 | 交互 | 统一静态能力列表（对话/查询/摘要），引导文案全部指向 "点击顶部灵动岛可展开控制面板" |

### Phase 13 POI 点位查询与地图标记 · 去自动化

| 改进 | 类型 | 说明 |
|------|------|------|
| POI 点位查询 | 功能 | 集成南京 79 万条 POI 数据（24 类：餐饮/购物/交通/科教等），`map_action` 行政区未命中时自动回退到 POI 点位查询 |
| 地图 pin 标记 | 交互 | POI 查询结果在地图上落蓝色 pin 标记，popup 显示名称/区/分类；区划查询后也自动在中心落 pin，2D Leaflet + 3D Cesium 双地图支持 |
| 移除自动摘要 | 交互 | 不再在进入页面或切换模式时自动生成摘要，改为用户主动触发；清理 AiSettings `autoSummary` 开关及 ChatModel 路由/mode watcher |
| 地名模糊匹配修复 | 修复 | `name in keywords` 增加 `len(keywords) - len(name) <= 2` 约束，防"南县"误匹配"南京邮电大学"；无 polygon 行政区优先查 POI |
| POI 匹配优先级优化 | 修复 | 模糊匹配优先以关键词开头且无括号修饰的结果 |
| 暗色灵动岛悬浮态修复 | 修复 | query/summary 模式下灵动岛悬浮态背景色正确显示暗色毛玻璃（之前被折叠态纯色覆盖） |
| 时钟冻结修复 | 修复 | `currentTime` 从计算属性改为 data + `setInterval` 30s 定时更新 |
| GeoJSON 格式化 | 工程 | 26 个 GeoJSON 文件从单行压缩格式化为 `indent=2` |

### 地图导航

- 后端从本地 GeoJSON 查询地名 → 经纬度 + 完整地址
- 前端 `navigate-map` 事件 → 地图 `flyTo()` 平滑飞行动画
- 自动缩放适配区域边界，确保完整显示

### 区域圈定

- 纯本地 GeoJSON 查询，覆盖全国 690 地市 + 5651 县区，江苏省 22841 村级补充
- 乡镇级和省级 GeoJSON 无覆盖，返回 None 由 LLM 文字回复引导
- 子区域自动提取（市→县、县→村），各分配不同颜色

### 行政区划缓存

- `geojson/` 目录：`city_2024.geojson`(690 地市) + `county_2024.geojson`(5651 县区) + `village_jiangsu.geojson`(22841 江苏村)
- `geojson/index.json`：地名 → Feature 索引，支持精确/变体/模糊匹配
- 模块级内存缓存，首次加载后常驻，后续零磁盘 IO
- 管理命令：`python manage.py preload_districts`（验证索引状态）

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
```

### 运行时配置（前端）

部署时修改 `skyeye-ui/public/config/config.js` 中的 `baseUrl` 等字段即可切换 API 地址，无需重新构建。

---

## 未提交内容（.gitignore 排除清单）

| 类别 | 文件/目录 | 说明 |
|------|----------|------|
| 密钥 | `skyeye/config.ini` | DeepSeek API Key / 数据库连接 |
| 依赖 | `node_modules/` | npm 包（`npm install` 安装） |
| Python 虚拟环境 | `venv/` `.venv/` `env/` `.env/` | Python 虚拟环境目录 |
| 构建产物 | `dist/` `build/` | 前端打包输出 |
| Python 缓存 | `__pycache__/` `*.pyc` `*.pyo` `*.egg-info/` `.eggs/` | 字节码 / 包元数据 |
| 测试文件 | `test*.py` `*_test.py` `tests/` `*.spec.js` `*.test.js` `*.spec.ts` `*.test.ts` `__tests__/` | 单元测试 |
| SQL | `*.sql` | 数据库脚本 |
| 影像/视频 | `*.tif` `*.mp4` | 影像视频文件 |
| 模型权重 | `*.bin` `*.pth` `*.th` | 二进制模型文件 |
| 多媒体 | `*.swf` `*.air` `*.ipa` `*.apk` | Flash / 移动应用包 |
| 运行时产物 | `skyeye/static/shp/` `skyeye/static/route_jobs/` `skyeye/static/route_plan/` `skyeye/static/layers/` | 地理数据 / 航线缓存 / 图层 |
| 日志 | `*.log` `logs/` `dev-server.log` | 运行日志 |
| IDE | `.idea/` `.vscode/` `*.suo` `*.ntvs*` `*.njsproj` `*.sln` | 编辑器个人配置 |
| 系统 | `.DS_Store` `Thumbs.db` | OS 生成文件 |

---

## 许可证

内部使用项目
