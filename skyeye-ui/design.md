# SkyEye AI 助手 — 设计文档

> Phase 11 · 三模式欢迎语 · 停止生成补充 · 地图查询鲁棒性

---

## 1. 设计哲学

- **Liquid Glass（液玻璃）**：以 Double-Bezel 双层玻璃 + `backdrop-filter` 毛玻璃 + 定向光伪元素模拟物理玻璃的光折射与深度感。灵感来自 iOS 26 Liquid Glass Chatbot。
- **设计 Token 体系** (Phase 8)：30+ 语义 Token 三层次架构 (Primitive → Semantic → Component)，7 大类别覆盖文本/表面/边框/模式色/光晕/面板/模糊，亮暗双主题自动切换，165 处硬编码值 Token 化。
- **页面装饰系统** (Phase 10)：Hallmark Ft8 风格滚动词条 + 高斯模糊氛围光斑，三模式颜色联动，`reduce-motion` / `aria-hidden` 全覆盖。
- **滚动触发入场** (Phase 10)：`IntersectionObserver` 替代全量一次性幕布揭示，卡片随滚动逐个触发入场动画，one-shot 不重触发。
- **双主题完整覆盖**：暗色模式以径向光球叠加，亮色模式以微渐变底色解决"白上叠白"的虚无感。所有组件均有 `.theme-light` 覆盖。
- **渐进式引导**：前 3 次打开面板时侧栏展示文字标签 + 大圆呼吸脉冲，3 次后回归 hover-only。localStorage 持久化计数，设置页提供重置入口。
- **clamp() 响应式缩放**：所有关键尺寸（面板宽高 / 侧栏 / 会话列表 / 字体 / 按钮）均使用 `clamp()` + CSS 自定义属性联动，无硬编码 px。
- **减少动效 / prefers-reduced-motion**：用户可切换"减少动态效果"，关闭呼吸光晕、WebGL 极光、打字机动画、消息入场动画、滚动视差。系统级 `prefers-reduced-motion: reduce` 兜底。

---

## 2. ChatModel.vue — AI 助手悬浮窗

**文件路径**: `src/components/chat/ChatModel.vue`

### 2.1 整体布局

```
.chat-wrapper (fixed, z-index: 1000, max-width: calc(100dvw - 64px))
├── .chat-fab                          # 悬浮胶囊按钮（面板关闭时显示）
└── .panel-row (.docked)               # 面板行：左侧栏 + 面板
    ├── .conv-list-panel (.open)       # 会话列表抽屉（从面板左侧滑出）
    ├── .side-rail (.visible / .onboard) # 左侧拓展槽（会话 / 模式 / 设置）
    └── .panel-shell                   # 外层铝合金托盘（Double-Bezel 外壳）
        └── .chat-panel (.docked)      # 内核玻璃面板
            ├── .chat-header           # 头部（拖拽把手 + 控制按钮）
            ├── .chat-body             # 消息区（空状态 / 消息列表 / 打字中）
            ├── .scroll-bottom-btn     # 回到底部浮动按钮
            ├── .chat-footer           # 输入区
            │   └── .chat-input-wrap   # 输入框胶囊
            └── .resize-handle         # 右下角缩放把手
```

**CSS 尺寸 Token** (定义在 `.chat-wrapper` 和 `.panel-row`):

```css
--conv-list-width: clamp(195px, 12vw, 250px);  /* 会话列表宽度 */
--rail-width:      clamp(100px, 6.25vw, 135px); /* 侧栏宽度 */
--rail-height:     clamp(180px, 12vw, 235px);   /* 侧栏高度 */
```

### 2.2 FAB — 悬浮胶囊按钮

| 特性 | 值 |
|------|-----|
| 形状 | 灵动岛胶囊形，`border-radius: 28px` |
| 尺寸 | `height: clamp(42px, 2.8vw, 52px)`，`min-width: clamp(42px, 2.8vw, 52px)` |
| 背景 | 暗色 `rgba(0,0,0,0.55)` + `backdrop-filter: blur(18px)` |
| 内容 | 机器人 SVG 图标 + "AI 助手"文字（hover 展开） |
| 动画 | hover `scale(1.05)` + 文字 `max-width` 展开（`cubic-bezier(0.16,1,0.3,1)`），图标旋转 `-12deg scale(1.15)` |
| badge | 右上角 8px 圆点，`--app-accent` 色，仅在 `messages.length > lastReadMsgCount` 时显示 |
| 亮色 | `rgba(255,255,255,0.7)` 白玻璃 + 蓝色 hover 边框 |

### 2.3 Double-Bezel 玻璃系统

#### 外壳 — `.panel-shell`

| 属性 | 暗色 | 亮色 |
|------|------|------|
| 背景 | `rgba(5,18,42,0.38)` | `linear-gradient(150deg, 蓝白→紫白→粉白)` |
| blur | `22px saturate(115%)` | 同 |
| 边框 | `rgba(0,180,240,0.12)` | `rgba(255,255,255,0.8)` |
| 内阴影 | 顶部高光 `inset 0 1px 0 rgba(255,255,255,0.1)` + 底部暗边 `inset 0 -1px 0 rgba(0,0,0,0.18)` | 同理亮色版本 |
| 外阴影 | `0 16px 56px rgba(0,0,0,0.6)` | `0 12px 48px rgba(0,0,0,0.12)` |
| 伪元素 `::before` | 双径向光球（蓝左上 + 紫右下） | 单径向光球（蓝左上） |

#### 内核 — `.chat-panel`

| 属性 | 暗色 | 亮色 |
|------|------|------|
| 背景 | `rgba(4,16,36,0.42)` | `linear-gradient(160deg, 白→蓝白→紫白)` |
| blur | `44px saturate(125%)` | `40px saturate(120%)` |
| 边框 | `rgba(0,200,255,0.14)` | `rgba(255,255,255,0.6)` |
| 圆角 | `20px`（docked: `12px 0 0 12px`） | 同 |
| `::before` 光球 | 左上蓝色径向光球 `300×300px`，`blur(28px)` | `linear-gradient` 淡光晕 |
| `::after` 光球 | 右下紫色径向光球 `260×260px`，`blur(24px)` | 无 |
| 尺寸 | `max-width: clamp(400px,27vw,560px)`，`max-height: clamp(480px,85vh,900px)` | 同 |
| docked | `width: clamp(340px,22vw,460px)`，全高（减顶部 margin） | 同 |

### 2.4 侧栏 — `.side-rail`

**交互模式**：
- **引导阶段**（前 3 次打开面板）：始终可见（`opacity:1`），小圆 `opacity:0.55`，大圆呼吸脉冲 `rail-pulse`，标签展开到 `max-width:50px`
- **正常阶段**（3 次后）：`opacity:0`，鼠标靠近面板左边缘 100px 范围内浮现，hover 保持可见
- **hover 时**：小圆 `scale(1)` 散开成弧（交错延迟 0s / 0.06s / 0.06s / 0.12s），标签展开

**布局**（绝对定位在半透明弧面上）：

| 位置 | 元素 | 说明 |
|------|------|------|
| `left:30%, top:4%` | spread-top-2 | 预留（未使用） |
| `left:7%, top:26%` | spread-top-1 | 会话列表入口（小圆） |
| 居中 | `.rail-item.large` | 模式切换大圆（`clamp(48px,3vw,60px)`） |
| `left:7%, top:57%` | spread-bot-1 | 系统设置入口（小圆） |
| `left:30%, top:79%` | spread-bot-2 | 预留（未使用） |

**大圆模式色**：chat(蓝) / query(红) / summary(琥珀)，`backdrop-filter: blur(12px)`

**引导标签布局**：
- 上方小圆标签：`left: calc(100% + 8px)`（向右展开）
- 大圆标签：`right: calc(100% + 2px)`（向左展开 `.rail-label--left`），与上方小圆交错

**引导大圆脉冲动画**：
```css
@keyframes rail-pulse {
    0%,100% { box-shadow: ..., 0 0 0 0 rgba(59,130,246,0.35); }
    50%    { box-shadow: ..., 0 0 0 8px rgba(59,130,246,0); }
}
```

### 2.5 会话列表抽屉 — `.conv-list-panel`

| 特性 | 值 |
|------|-----|
| 位置 | Flex 子元素，面板左侧滑出，打开时面板等比收缩 |
| 宽度 | `max-width: 0` → `var(--conv-list-width)`（`clamp(195px,12vw,250px)`） |
| 动画 | `transition: max-width 0.02s, opacity 0.02s`（瞬关对齐面板动画） |
| 背景 | 暗色 `rgba(5,18,42,0.78)` + `blur(20px)` |
| 内层 | 固定宽度防回流，装饰光晕 `::before` |
| 会话项 | 交错入场 `convItemIn`（40ms stagger），hover 高亮，active 左边框 + 蓝紫底色 |
| 上限 | 最多 20 个会话，超出禁用新建按钮 |
| z-index | `1015`，高于侧栏(1010) |

**亮色主题**：白色半透明 + 浅色边框。

### 2.6 头部 `.chat-header`

| 特性 | 说明 |
|------|------|
| 结构 | 左侧 logo+标题+副标题，右侧 4 个圆形图标按钮 |
| 背景 | `rgba(3,12,28,0.85)` + `blur(24px)` |
| 伪元素 | `::before` 线性光 `linear-gradient(180deg, white 0.04→transparent 60%)` 模拟顶部高光 |
| 按钮 | 32px 圆形，hover 深色底；从左到右：减少动效 / 吸附 / 设置 / 清空 / 关闭 |
| 模式色联动 | query-mode 红色底 + 红边框；summary-mode 琥珀色底 + 金色边框 |
| 拖拽 | `@mousedown` 触发头拖拽（不干扰按钮点击）|

### 2.7 底部 `.chat-footer` + 输入框 `.chat-input-wrap`

**消息区景深分层** (Phase 8)：`.chat-body` 添加 `linear-gradient` 背景（浅→深），比底部输入区稍亮，模拟"近深远浅"的玻璃折射感，与 `.chat-footer` 的深色底形成视觉对比。

| 特性 | 值 |
|------|-----|
| 背景 | `rgba(3,12,28,0.85)` + `blur(24px)`，顶部分隔线 `rgba(0,180,240,0.08)` |
| 输入框形状 | 胶囊形 `border-radius: 24px` |
| 输入框背景 | `linear-gradient(145deg, 深蓝→深蓝)` 三色渐变模拟金属凹陷 |
| 输入框伪元素 | `::before` 顶部光带 `linear-gradient(180deg, 蓝光→transparent)` |
| focus-within | 蓝光边框 + 4px 扩散光晕 `rgba(59,130,246,0.18)` + `scale(1.008)` |
| 字体 | `font-size: 14px`，`padding: 9px 0` |
| placeholder | `rgba(255,255,255,0.55)`（WCAG AA 对比度） |
| 发送按钮 | 蓝色渐变圆形，`align-self: center` 垂直居中 (Phase 8)，hover `scale(1.06)` + 扩散阴影 |
| 停止按钮 | 红色胶囊 `rgba(239,68,68,0.12)` + 脉冲方块 `stop-pulse` 动画 |
| 模式色 | query: 红边框 + 红发送按钮；summary: 琥珀边框 + 金色发送按钮 |

### 2.8 消息气泡

| 属性 | 用户（暗色） | 助手（暗色） | 亮色 |
|------|------------|------------|------|
| max-width | 85% | 85% | 85% |
| padding | `clamp(10px,0.8vw,16px)` | 同 | 同 |
| font-size | `clamp(12px,0.75vw,14px)` | 同 | 同 |
| 背景 | `linear-gradient(135deg, #3b82f6, #2563eb)` | `rgba(8,22,46,0.75)` + `::before` 高光 | 用户蓝渐变 / 助手灰底 |
| 圆角 | `18px 4px 18px 18px` | `4px 18px 18px 18px` | 同 |
| 阴影 | `0 4px 14px rgba(37,99,235,0.25)` | 无 | 同 |
| 高光条 | — | `::after` 1px 顶部高光线，两端透明中间 `rgba(255,255,255,0.12)` (Phase 8) | — |
| 模式色 | query(红) / summary(琥珀) | 无变化 | query(红) / summary(琥珀) |
| 代码块 | `pre` 暗底 + `code` 内联标记 | 同 | 同 |
| strong | `--brand-accent: #60a5fa` | 同 | `#2563eb` |

**消息入场动画**: `msgSlideIn` — `translateY(12px) scale(0.97)` → 原位，`cubic-bezier(0.16,1,0.3,1)`，60ms stagger

**消息操作**: hover 显示复制 + 重试按钮。复制成功后 "已复制" toast。出错/中断的消息显示重试按钮。

### 2.9 欢迎区（空状态）— Phase 11 重构为三模式联动

欢迎区能力列表和底部提示随 `chatMode` 动态切换，反映每种模式实际可用的工具。

```
welcome-robot-icon (40px SVG, 居中)
  ↓
"你好！我是金陵阡陌 AI 助手" (16px, 600w) — 静态，所有模式共用
  ↓
"当前为[对话/数据查询/智能摘要]模式，我可以帮你：" (13px, 引导标签)
  ↓
【对话模式】能力列表（4 条）:
  1. 导航定位：带你去指定地点查看地图         ← 对应 map_action
  2. 页面跳转：打开航线、任务、全景等页面     ← 对应 navigate_page
  3. 任务查询：查找巡检任务和检测数据         ← 对应 lookup_task
  4. 通用问答：解答巡检业务相关问题          ← 无工具直接文本回复
【数据查询模式】能力列表（4 条）:
  1. 数据查询：统计分析航线、任务、异常数据   ← 对应 query_data
  2. 导航定位：带你去指定地点查看地图
  3. 页面跳转：打开航线、任务、全景等页面
  4. 任务查询：查找当前检测任务详情
【智能摘要模式】能力列表（4 条）:
  1. 综合摘要：对选中要素自动生成分析报告
  2. 风险评估：识别高风险区域和异常指标
  3. 进度跟踪：汇总整体完成情况和瓶颈
  4. 决策建议：基于数据提供下一步行动建议
  ↓
分割线 (1px rgba white 0.04)
  ↓
【对话模式】底部提示: "💡 试试下方快捷提问，或直接说出你的需求；左侧圆点可切换模式和会话"
【查询模式】底部提示: "💡 试试下方快捷提问，或直接输入数据查询需求；左侧圆点可切换模式和会话"
【摘要模式】底部提示: "💡 先在数据页选中要素，然后试试下方快捷提问；左侧圆点可切换模式和会话"
  ↓
快捷提问按钮（flex-wrap 胶囊，从设置页自定义模板读取，各模式独立）
```

**亮色适配**: 所有颜色反转为深色系 (`#1e293b` / `#64748b`)

### 2.10 Stream 状态

| 状态 | 展示 |
|------|------|
| 无文本、有 phase | 阶段图标 + 阶段文字 + 呼吸点（dot-pulse） |
| 有 streamingText | 打字机逐字渲染 Markdown，光标闪烁 `streaming-cursor` |
| 面板光环 | `thinking-glow` — border 呼吸 `breathe-glow` + `::after` 呼吸光环 `breathe-ring` |
| 手动停止 | 有部分文本追加 `…[已停止]` 后缀 (_interrupted=true → 重试按钮)，无文本插入"已停止生成"保持对话完整 |
| 回到底部 | 用户上滚时显示浮动按钮，新消息自动滚到底部 |

### 2.11 面板交互

| 交互 | 实现 |
|------|------|
| 拖拽 | 头部/FAB `@mousedown` → `mousemove` 计算百分比位置 → `mouseup`。边界碰撞检测 4px 阈值。 |
| 缩放 | 右下角 `resize-handle` → `mousemove` 计算增量宽高 → `mouseup`。范围 360-35vw × 420-85vh。 |
| 吸附 | `docked` 切换：全高右栏 `width: clamp(340px,22vw,460px)`，圆角收窄。 |
| 窗口缩放 | `resize` 事件重夹持 dragPos 百分比，wrapper `max-width: calc(100dvw - 64px)` 硬截断。 |
| 面板关闭 | GSAP `to({ opacity: 0, scale: 0.92 })` → `visible = false` → 重置 `convListVisible`。 |
| 并发锁 | `_animating`(300ms 动画锁) + `_sending`(发送锁) + `streaming` watcher 自动释放。 |

### 2.12 键盘快捷键

| 快捷键 | 动作 |
|--------|------|
| `Ctrl/Cmd + K` | 唤起/关闭面板 |
| `Esc` | 关闭面板 |
| `Enter` | 发送消息 |
| `Shift + Enter` | 消息中换行 |

---

## 3. aiSettings — AI 设置页

**文件路径**: `src/views/aiSettings/index.vue`

### 3.1 背景系统（Phase 9-10 重构）

| 层级 | 元素 | 说明 |
|------|------|------|
| z-index: 0 | `.aurora-canvas` | WebGL Ether Shader 动态极光（仅深色+非减少动效） |
| z-index: 0 | `.ambient-orbs` | 4 个固定定位高斯模糊光斑（Phase 10 新增），分布于页面四角，`filter: blur(100px)`，三模式（indigo/red/amber）颜色联动 1.2s 过渡，亮暗双主题适配，`reduce-motion` 隐藏 (Phase 10) |
| z-index: 0 (sticky) | `.marquee-strip` | Hallmark Ft8 风格水平无限滚动跑马灯（Phase 10 新增），`position: sticky; top: 0`，p+2px 双边框 + `text-shadow` 文字发光 + `backdrop-filter` 玻璃底座，32s 周期，三模式颜色联动，`reduce-motion` 冻结 (Phase 10) |
| z-index: 1 | `.light-gradient-overlay` | 亮色模式纯 CSS 渐变层（页面温度 + 右上自然光），零 JS 零动画 (Phase 9) |
| z-index: 2 | `.settings-main` | 主内容容器，`max-width: 880px`，居中 |

> Phase 9 移除了呼吸光斑系统（3 个 `bg-orb` + `noise-overlay` + 滚动视差 rAF + `@keyframes orb-breathe`）。Phase 10 以氛围光斑和滚动词条填补视觉空白。

**亮色主题**: WebGL 不渲染，氛围光斑降低透明度至 0.04–0.06，背景 `#f4f5f9`。

### 3.2 便当盒网格 — `.bento-grid`

```
2 列网格 (1fr 1fr)，gap: 20px，.col-wide 跨 2 列
移动端 ≤768px 退化为单列

[ 模型与参数  (col-wide) ]
[ 外观         ] [ 对话默认    ]
[ 提示词模板   (col-wide) ]
[ 键盘快捷键   ] [ 关于        ]
```

### 3.3 卡片 Pod — Double-Bezel Liquid Glass

**外壳 `.pod-shell`**:
- `padding: 4px` 形成托盘边距
- 暗色 `rgba(255,255,255,0.06)` + `blur(12px)` + `border: 1px solid rgba(255,255,255,0.08)`
- 内阴影顶部高光 `inset 0 1px 0 rgba(255,255,255,0.06)`
- hover: 边框提亮 + `transform: translateY(-2px)` 抬升 + 外阴影加深 `0 14px 44px rgba(0,0,0,0.5)` (Phase 8 增强)
- `transition` 包含 `transform 0.4s` 平滑过渡

**内核 `.pod-core`**:
- `padding: 28px 28px 32px`, `border-radius: 21px`
- 暗色 `rgba(255,255,255,0.04)` + `blur(40px)`
- 伪元素 `::before`: `linear-gradient(135deg, white 0.06→transparent 50%)` 模拟玻璃折射高光

**图标区 `.pod-icon-wrap`**: 44px 圆角方块，`rgba(99,102,241,0.12)` 底 + 紫色边框

**亮色**: 外壳 `rgba(0,0,0,0.03)`，内核 `rgba(255,255,255,0.45)`，高光白色增强。

### 3.4 表单元素

| 元素 | 设计 |
|------|------|
| 下拉选择 `select` | 全宽胶囊 `border-radius: 14px`，`blur(8px)`，自定义 chevron 图标，focus 紫色边框 + 4px 光晕 |
| 滑块 `input[type=range]` | 6px 轨道，22px 白色圆形滑块，hover `scale(1.15)`，active `scale(0.95)` |
| 切换开关 `toggle-switch` | 48×28px 胶囊，白色 knob，active 时 `translateX(20px)`，紫色发光底 |
| 模式芯片 `mode-chip` | Flex 列（图标+标签），active 紫色发光边框 + 背景 |
| 快捷键 `kbd` | 26px 小方块，`inset` 高光模拟物理按键凸起 |

**自定义 Tooltip 系统** (`data-tip`):
- `.field-help` 圆形 "?" 图标触发
- `::after` 气泡: 260px 宽，毛玻璃底，三角箭头 `::before`，hover 时 `opacity: 1; translateY(-2px)`
- 右对齐 `.right` 变体防溢出

### 3.5 提示词模板系统

**结构**:
- 顶部模式标签切换 (`template-mode-tabs`)：自由对话 / 数据查询 / 智能摘要，active 紫色
- 模板列表：序号圆圈 + 输入框 + 删除按钮
- 添加模板按钮（虚线边框，最多 5 条）
- 每模式独立 3 条默认模板，localStorage 持久化

**默认模板**:

| 模式 | 默认内容 |
|------|---------|
| chat | '带我去南京鼓楼区看看', '帮我打开航线规划页面', '当前有哪些检测任务？' |
| query | '当前页面数据概览', '最近有哪些异常情况？', '按状态分类统计' |
| summary | '有哪些高风险项？', '整体完成进度如何？', '下一步建议怎么做？' |

### 3.6 动作按钮行 — `.actions-bar`

| 按钮 | 图标 | 功能 |
|------|------|------|
| 重新展示侧栏引导 | 时钟图标 | 重置 `localStorage.skyeye_rail_onboard` → 0，通过 `storage` 事件跨标签页同步到 ChatModel |
| 恢复默认 | 刷新图标 | 重置所有设置项 + 提示词模板到默认值 |

### 3.7 页面动画序列（Phase 10 重构）

1. **打字机**（非 reduceMotion）: eyebrow "AI 助手" (50ms) → title "设置" (70ms) → subtitle "个性化你的智能对话体验" (40ms)，光标闪烁 `cursor-blink`
2. **滚动触发布局入场**（Phase 10 重构）: 打字机完成后，`IntersectionObserver` 监听 5 张 `.curtain-item` 卡片，`threshold: 0.1` + `rootMargin: 0px 0px -8% 0px`，卡片滚入视口时逐个添加 `.curtain-revealed` 触发入场动画（`opacity/brightness/transform` 过渡），one-shot `unobserve` 后不再重触发。`reduceMotion` 时直接全量显示，跳过监听。

### 3.8 滚动词条装饰 — `.marquee-strip`（Phase 10）

Hallmark Ft8 风格的页面顶部水平无限滚动跑马灯。

**结构**:
```
.marquee-strip (.marquee--free / .marquee--query / .marquee--summary)
└── .marquee-track
    ├── <span> 8 组关键词（DeepSeek-V3 · DeepSeek-R1 · 智能推理 · ...）
    └── <span> 8 组关键词（第二份副本，实现无缝循环）
```

| 特性 | 值 |
|------|-----|
| 定位 | `position: sticky; top: 0; z-index: 10` |
| 背景 | `linear-gradient(180deg, 底色→透明)` + `backdrop-filter: blur(12px)` |
| 边框 | 顶部 2px + 底部 2px indigo 细线 |
| 字体 | 700 粗体，`clamp(14px, 2.5vw, 20px)`，`letter-spacing: 0.08em` |
| 间距 | `2rem`（32px）|
| 动画 | `marquee-scroll` 32s 线性无限循环，`translateX(-50%)` |
| 文字发光 | `text-shadow: 0 0 12px rgba(靛蓝, 0.25)` |
| 模式色 | chat(蓝) / query(红) / summary(琥珀)，CSS 变量 `--mq-*` 联动 |
| 无障碍 | `aria-hidden="true"`，`pointer-events: none`（仅装饰） |

**三模式颜色系统** (CSS 自定义属性):

```css
.marquee--free    { --mq-border: rgba(99,102,241,0.18);  --mq-bg-from: rgba(99,102,241,0.06);  --mq-text: rgba(165,180,252,0.35); --mq-glow: rgba(99,102,241,0.18); }
.marquee--query   { --mq-border: rgba(239,68,68,0.18);   --mq-bg-from: rgba(239,68,68,0.06);   --mq-text: rgba(252,165,165,0.35); }
.marquee--summary { --mq-border: rgba(245,158,11,0.18);  --mq-bg-from: rgba(245,158,11,0.06);  --mq-text: rgba(252,211,77,0.35); }
```

### 3.9 两侧氛围光斑 — `.ambient-orbs`（Phase 10）

4 个固定定位的高斯模糊光斑，填充页面两侧空档，与三模式颜色联动。

| 光斑 | 位置 | 尺寸 | 默认颜色 | 说明 |
|------|------|------|---------|------|
| `.orb--tl` | `top: -8%; left: -5%` | 320×320px | indigo `rgb(99,102,241)` | 左上角主光斑 |
| `.orb--tr` | `top: 12%; right: -3%` | 260×260px | cyan `rgb(56,189,248)` | 右上角补光，`opacity: 0.09` |
| `.orb--br` | `bottom: -10%; right: -6%` | 380×380px | violet `rgb(139,92,246)` | 右下角最大光斑，`opacity: 0.1` |
| `.orb--ml` | `top: 55%; left: -4%` | 220×220px | indigo `rgb(99,102,241)` | 左侧中部补充，`opacity: 0.08` |

**样式核心**:
```css
.orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(100px);
    opacity: 0.12;
    transition: background 1.2s cubic-bezier(0.32, 0.72, 0, 1),
                opacity 1.2s cubic-bezier(0.32, 0.72, 0, 1);
}
```

**三模式颜色联动**: `.orbs--query` / `.orbs--summary` 类级联覆盖每个光斑的 `background` 色，1.2s 平滑过渡。亮色主题降透明度至 0.04–0.06，`reduce-motion` 隐藏。

---

## 4. 共享设计要素

### 4.1 颜色系统

#### AI 语义 Token 架构 (Phase 8 新增)

三层次设计 Token 体系：

```
Layer 1: Primitive (原始值)     Layer 2: Semantic (语义)        Layer 3: Component (组件)
rgba(255,255,255,0.55)  ───→   --ai-text-tertiary     ───→    .pod-desc { color: var(...) }
#3b82f6                  ───→   --ai-mode-chat         ───→    .chat-send-btn { background: ... }
blur(22px)...            ───→   --ai-blur-shell        ───→    .panel-shell { backdrop-filter: ... }
```

**7 大类语义 Token**：

| 类别 | 前缀 | 数量 | 暗色默认 | 亮色覆盖 |
|------|------|------|---------|---------|
| 文本 | `--ai-text-*` | 6 级 | white 0.45→0.95 | Slate 900→400 |
| 玻璃表面 | `--ai-glass-*` | 6 级 | white 0.03→0.15 | black 0.02→0.12 |
| 边框 | `--ai-border-*` | 4 级 | white 0.06→0.2 | black 0.06→0.2 |
| 模式色 | `--ai-mode-*` | 9 级 | 蓝/红/琥珀 (light/dark/主色) | 同 (颜色不变) |
| 光晕 | `--ai-glow-*` | 4 级 | blue/purple/red/amber | 降低不透明度 |
| 面板背景 | `--ai-panel-*` | 4 级 | shell/core/header/footer | — |
| 毛玻璃 blur | `--ai-blur-*` | 5 级 | shell/core/card/input/header | 同 |

**定义位置**：`src/css/theme/cyber-tokens.css`
- 暗色默认：`:root` 块内
- 亮色覆盖：`html[data-theme='light']` 块内
- 替换范围：ChatModel 62 处 + aiSettings 103 处 = 165 处

#### 原有 Token

| Token | 用途 |
|-------|------|
| `--app-accent: #6366f1` | FAB badge、active 标记 |
| `--brand-accent: #60a5fa` (暗) / `#2563eb` (亮) | 消息 strong、流式光标、dot-pulse |
| 蓝紫 `#3b82f6 / #2563eb` | 发送按钮、用户气泡、focus 光环 |
| 红 `#ef4444 / #dc2626` | query 模式（边框/头部/底部/气泡/侧栏） |
| 琥珀 `#f59e0b / #d97706` | summary 模式（边框/头部/底部/气泡/侧栏） |

### 4.2 动画缓动函数

| 用途 | 函数 |
|------|------|
| 面板开合、dragging | `cubic-bezier(0.16, 1, 0.3, 1)` (ease-out-expo 风格) |
| 元素交互 hover/active | `cubic-bezier(0.32, 0.72, 0, 1)` (弹性缓出) |
| 消息入场 | `cubic-bezier(0.16, 1, 0.3, 1)` |
| 幕布卡片入场 | `cubic-bezier(0.32, 0.72, 0, 1)` |

### 4.3 动画 Keyframes

| 名称 | 用途 | 文件 |
|------|------|------|
| `rail-pulse` | 引导阶段大圆呼吸脉冲 | ChatModel |
| `msgSlideIn` | 消息交错滑入 | ChatModel |
| `convItemIn` | 会话列表项交错淡入 | ChatModel |
| `dot-pulse` | AI 思考三点呼吸 | ChatModel |
| `breathe-glow` / `breathe-ring` | 流式输出时面板光环 | ChatModel |
| `stop-pulse` | 停止按钮方块闪烁 | ChatModel |
| `orb-breathe` | 设置页背景光斑呼吸 (Phase 10 已移除) | aiSettings |
| `marquee-scroll` | 滚动词条无限水平滚动 | aiSettings |
| `cursor-blink` | 打字机光标闪烁 | aiSettings |
| `templateFadeIn` | 模板行淡入 | aiSettings |

### 4.4 localStorage 持久化 Key

| Key | 存储内容 | 读写组件 |
|-----|---------|---------|
| `skyeye_ai_settings` | 模型/温度/token/主题/动效/默认模式/自动摘要/提示词模板 | ChatModel(读) + aiSettings(读写) |
| `skyeye_conversations` | 多会话数据 [{id, title, messages, mode, createdAt, updatedAt}] | ChatModel(读写) |
| `skyeye_rail_onboard` | 侧栏引导计数 (0-3) | ChatModel(写) + aiSettings(重置) |

### 4.5 无障碍

- 所有交互元素均有 `aria-label`
- `role="dialog"` / `role="complementary"` / `role="button"` 语义标注
- `:focus-visible` 紫色轮廓环（`outline: 2px solid rgba(99,102,241,0.6)`）
- `@media (prefers-reduced-motion: reduce)` 全局关闭所有动画
- ChatModel 键盘操作：`Ctrl+K` 唤起，`Esc` 关闭，`Enter` 发送
- **WCAG AA 对比度** (Phase 8)：aiSettings 暗色模式 14 处文本颜色提升至 ≥4.5:1 (正文) / ≥3:1 (辅助文字/placeholder)，覆盖副标题、滑块提示、切换提示、重置按钮、帮助图标、模式芯片等元素

---

## 5. 响应式断点

| 断点 | 行为 |
|------|------|
| `max-width: 768px` | aiSettings 便当盒退化为单列，padding 减少 |
| `max-width: calc(100dvw - 64px)` | ChatModel wrapper 硬截断防止溢出 |
| 窗口 resize | ChatModel 重夹持 `dragPos` 百分比，`_onWindowResize` |
| drawer open | wrapper `max-width` 减去 `--conv-list-width` |
