# 金陵阡陌 — AI 助手 (Phase 13)

无人机巡检智能平台前端，集成 AI 对话面板与可视化参数设置。

## 技术栈

| 层 | 技术 |
|---|------|
| 框架 | Vue 2 + Vuex + Vue Router |
| UI 库 | Element UI |
| 动效 | GSAP + WebGL Shader + CSS Animation |
| 地图 | 天地图 (TMap) |
| 样式 | SCSS + CSS 自定义属性 (cyber-tokens, ai-tokens) |

## 项目结构

```
skyeye-ui/src/
├── components/
│   └── chat/
│       └── ChatModel.vue          # AI 对话面板（浮动、拖拽、吸附、多模式）
├── views/
│   └── aiSettings/
│       └── index.vue              # AI 设置页（模型、参数、外观、对话默认）
├── css/theme/
│   └── cyber-tokens.css           # 设计 Token（圆角、颜色、间距）
├── router/
│   └── index.js                   # 路由配置
└── layout/
    └── index.vue                  # 全局布局（挂载 ChatModel）
```

## Phase 12 新增功能

### 灵动岛一体化控制中心

`chat-header` 行被移除，所有头部功能收敛到灵动岛：

- **紧凑默认态**: 32×32px 纯色实心圆（按模式蓝/红/琥珀），悬浮展开为胶囊 "● 金陵阡陌 ▾"
- **下拉控制面板**: 点击展开毛玻璃卡片，包含标题信息 + 5 个操作按钮（动态效果 / 吸附 / 设置 / 清空 / 关闭）
- **模式色全联动**: 圆点、展开态边框、光晕、下拉面板副标题、按钮栏分隔线均随 chat/query/summary 三模式切换
- **淡入淡出动画**: `cubic-bezier(0.25, 1.1, 0.4, 1)` 弹簧缓动，`min-width`/`border-radius`/`opacity` 联合过渡

### 手机外壳外观

- **iOS 状态栏**: 时间 + 信号/WiFi/电池 SVG 图标（源自 ContraQuest 项目），14px top padding
- **灵动岛同行**: 状态栏三区布局（时间 | 灵动岛 | 图标），Flex 居中
- **设备级投影**: `panel-shell` 三层 `box-shadow` 模拟手机壳体厚度与圆角
- **玻璃折射**: 定向光伪元素 `::before`/`::after` 模拟物理玻璃折射

### 会话列表与面板一体化

- **无缝边框**: 展开会话列表时，`panel-shell` 左侧 `border-left: none`，由 `conv-list-panel` 承接上-左-下边框
- **统一背景**: `conv-list-panel` 与 `panel-shell` 共用相同的多层渐变 + `backdrop-filter` + 光晕伪元素
- **底部对齐**: `.chat-wrapper.drawer-open .panel-shell` 设置 `align-self: stretch`，消除底部错位

### 四角缩放

- 四个角落 (`br/bl/tr/tl`) 均支持拖拽缩放，各自正确的光标方向
- 左侧/顶部方向缩放时同步移动面板位置，保持对侧/对边不动
- 三角指示器颜色按暗/亮双主题适配

### 点击外部收起至 FAB

- `document mousedown` 监听，点击 `.chat-wrapper` 外部 → `closeChat()` 返回悬浮按钮
- docked 模式下不触发（嵌入页面时不收起）
- 与灵动岛下拉关闭共用同一 `_onDocMouseDown` 事件

### 欢迎区重构

- 统一静态能力列表，列出三种模式及核心能力（对话/数据查询/智能摘要）
- 引导文案全部指向灵动岛："点击顶部灵动岛可展开控制面板"

---

## 历史功能摘要

### AI 对话面板 (`ChatModel.vue`)

- **多模式对话**: 聊天 / 数据查询 / 智能摘要，模式切换联动面板配色
- **工具调用**: LLM 可通过 `navigate_page`、`map_action`、`lookup_task`、`query_data` 四个工具控制系统行为
- **流式渲染**: SSE 流式响应 + 打字机效果 + 阶段指示器（理解中/查询中/生成中）
- **交互增强**: 拖拽定位、右下吸附 (dock)、四角缩放、侧栏快捷操作、Cmd+K 快捷键
- **视觉系统**: iOS Liquid Glass 双层玻璃 (panel-shell + chat-panel)、backdrop-filter 模糊、多模式光晕
- **无障碍**: focus-visible 键盘导航、aria-label、prefers-reduced-motion、reduceMotion 手动开关

### AI 设置页 (`aiSettings/index.vue`)

- **打字机入场**: 标题/副标题逐字打印 + 卡片幕布揭幕动画
- **模型与参数**: DeepSeek-V3 / R1 选择、Temperature 滑块（四段颜色映射）、MaxTokens 文本域 + 预览条
- **对话默认**: 三模式默认选择、自动摘要开关、减少动态效果、组合快捷键参考
- **数据持久化**: localStorage 双向同步，ChatModel 和设置页共享 `skyeye_ai_settings` 键
- **从聊天打开设置**: LLM 意图推理 `navigate_page` → 设置页返回自动恢复聊天面板（sessionStorage 闭环）
- **视觉系统**: WebGL 极光着色器 + CSS 氛围光斑 + 便当盒网格 + 双层玻璃卡片
- **工具提示**: 自定义 tooltip 气泡，支持防出界对齐
- **滚动词条**: Hallmark Ft8 风格水平无限滚动跑马灯，三模式颜色联动
- **滚动触发布局入场**: `IntersectionObserver` 逐个触发卡片入场动画

### 设计 Token (`cyber-tokens.css`)

- 92 个语义 Token 8 大类（文本/玻璃/边框/模式色/光晕/模糊/交互态/组件级+投影），亮暗双主题自动切换
- `--app-accent` (indigo #6366f1) 统一主色调
- `--radius-sm/md/lg/xl/2xl` 六级圆角弹性系统

## 修复记录

### Phase 5
- Dock 模式下滚动条出现导致右侧缩进 → 锁定 `.chat-panel.docked` 宽度
- tooltip 被 `.pod-core` overflow:hidden 裁剪 → 移除 overflow 限制 + 右侧防出界对齐
- 导航清空对话历史 → 改为保留历史 + FAB badge 指示
- 打字机动画在 reduceMotion 下仍播放 → 跳过动画直接渲染
- 工具调用空白 assistant 消息残留 → 导航分支清理中间消息

### Phase 6 鲁棒性加固

- **13 项生命周期清理**: `beforeDestroy` 中 AbortController.abort() / GSAP killTweensOf / 定时器清理 / WebGL rAF 取消 / copyTimer / mapDispatchTimer
- **fetch 60s 硬超时**: setTimeout + AbortController，防止请求永久挂起
- **打字机生命周期保护**: `_typewriterCancelled` 标志，路由跳转后立即停止
- **JSON.parse 保护**: LLM 畸形参数 → 捕获并显示友好错误气泡，不死锁 streaming
- **`_storageError` 可重置**: 存储恢复后警告横幅自动消失
- **`savePrefs` 300ms 防抖**: 快速拖 slider 只写一次 localStorage
- **输入防护**: textarea `maxlength=5000` + 字符计数提示 + trim 空消息拦截

### Phase 6 交互增强

- **工具冲突裁决**: 四个工具互相引反例 + 后端 5 条裁决规则
- **三层并发锁**: 动画锁 + 发送锁 + streaming watcher 自动释放
- **多模式用户气泡**: 用户消息随模式变色，亮暗双主题适配

### Phase 7 液玻璃视觉重塑 & 引导式 Onboarding

- **侧栏渐进式引导**: 前 3 次打开面板展示圆点 + 文字标签，大圆呼吸脉冲
- **液玻璃背景**: 径向光球替代 linear-gradient
- **定向光叠加层**: 各容器 `::before` 线性光伪元素

### Phase 8 设计 Token 体系化 & Surface 深度层次

- **92 个语义 Token**: 8 大类，亮暗双主题自动切换
- **WCAG AA 对比度**: aiSettings 暗色模式 16 处文本 ≥4.5:1
- **Surface 深度层次**: 卡片 hover 抬升、消息区景深渐变

### Phase 9 微交互润色 & 视觉瘦身

- **FAB 数字徽章**: 未读消息数字胶囊 (99+ 截断)
- **FAB 生成中呼吸微光**: 按模式变色
- **侧栏"水面灌满"**: clip-path 动画
- **回到底部胶囊化**: hover 展开"最新"标签
- **移除呼吸光斑系统**: 删除 3 个 bg-orb + noise-overlay + 滚动视差 rAF

### Phase 10 页面装饰系统 & 滚动触发入场

- **滚动词条**: Hallmark Ft8 风格跑马灯，三模式颜色联动
- **氛围光斑**: 4 个固定定位 blur(100px) 光斑，三模式颜色联动
- **滚动触发布局入场**: IntersectionObserver 逐个触发

### Phase 11 模式欢迎语 & 停止生成补充 & 地图跳转修复

- **三模式欢迎语**: chatMode 联动欢迎区能力列表和底部提示
- **手动停止对话补充**: 追加 `…[已停止]` / "已停止生成"
- **导航消息兼容**: `_skipContext` 标记消息替换为"收到"
- **地图跳转 timer 修复**: 设置前清除旧 timer

### Phase 12 灵动岛 & 手机外壳 & 一体化会话抽屉

- **灵动岛一体化**: 聊天头部功能全部收敛至灵动岛（小圆→胶囊→下拉面板），模式色全联动
- **手机外壳外观**: iOS 状态栏（时间 + 信号/WiFi/电池） + 设备级投影 + 玻璃折射
- **会话列表一体化**: 与面板无缝融合（统一背景/边框/光效），底部对齐
- **四角缩放**: 四个角落均可拖拽缩放
- **点击外部收起**: 点击 ChatModel 外部自动返回 FAB

### Phase 13 POI 点位查询与地图标记 · 去自动化

- **POI 点位查询**: 南京 79 万条 POI 数据集成，`map_action` 行政区未命中自动回退 POI
- **地图 pin 标记**: POI/区划查询后地图中心落蓝色 pin + popup 信息，2D Leaflet + 3D Cesium 双支持
- **移除自动摘要**: 不再自动生成摘要，改为用户主动触发；清理 AiSettings `autoSummary` 及 ChatModel 路由/mode watcher 触发
- **地名匹配修复**: 模糊匹配加长度约束防误匹配；无 polygon 行政区优先 POI
- **POI 匹配优化**: 优先以关键词开头且无括号修饰的结果
- **暗色灵动岛修复**: query/summary 模式悬浮态背景正确显示暗色毛玻璃
- **时钟修复**: `currentTime` 改 data + 定时器，解决冻结问题
- **GeoJSON 格式化**: 26 个文件 indent=2 可读化

## 快速开始

```
npm install
npm run serve
```

## 构建部署

```
npm run build
```

静态资源输出至 `dist/`，由 Nginx 反向代理到后端 API。
