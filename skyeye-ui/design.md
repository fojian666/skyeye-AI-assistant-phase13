# SkyEye AI 助手 — 设计文档

> Phase 12 · 灵动岛一体化 · 手机外壳 · 一体化会话抽屉

---

## 1. 设计哲学

- **Liquid Glass（液玻璃）**：以 Double-Bezel 双层玻璃 + `backdrop-filter` 毛玻璃 + 定向光伪元素模拟物理玻璃的光折射与深度感。
- **灵动岛一体化** (Phase 12)：所有头部功能收敛至灵动岛控制中枢，紧凑默认态为 32px 纯色实心圆，悬浮展开为胶囊，点击展开下拉面板。
- **手机壳体外壳** (Phase 12)：iOS 状态栏（时间 + 信号/WiFi/电池）+ 设备级投影 + 定向光折射，灵感来自 iOS 原生界面。
- **设计 Token 体系**: 92 个语义 Token 三层次架构 (Primitive → Semantic → Component)，7 大类别，亮暗双主题自动切换。
- **页面装饰系统**: Hallmark Ft8 风格滚动词条 + 高斯模糊氛围光斑，三模式颜色联动。
- **双主题完整覆盖**：暗色模式以径向光球叠加，亮色模式以微渐变底色解决"白上叠白"。所有组件均有 `.theme-light` 覆盖。
- **渐进式引导**：前 3 次打开面板时侧栏展示文字标签 + 大圆呼吸脉冲，3 次后回归 hover-only。
- **clamp() 响应式缩放**：所有关键尺寸均使用 `clamp()` + CSS 自定义属性联动，无硬编码 px。
- **减少动效 / prefers-reduced-motion**：用户可切换"减少动态效果"，系统级 `prefers-reduced-motion: reduce` 兜底。

---

## 2. ChatModel.vue — AI 助手悬浮窗

**文件路径**: `src/components/chat/ChatModel.vue`

### 2.1 整体布局

```
.chat-wrapper (fixed, z-index: 1000, max-width: calc(100dvw - 64px))
├── .chat-fab                          # 悬浮胶囊按钮（面板关闭时显示）
└── .panel-row (.docked)               # 面板行：左侧栏 + 面板
    ├── .conv-list-panel (.open)       # 会话列表抽屉（从面板左侧滑出，与面板无缝融合）
    ├── .side-rail (.visible / .onboard) # 左侧拓展槽（会话 / 模式 / 设置）
    └── .panel-shell                   # 外壳（Double-Bezel 铝合金托盘 + 手机壳体质感）
        └── .chat-panel (.docked)      # 内核玻璃面板
            ├── .phone-top-section     # 上半部分拖拽区域（Phase 12 新增）
            │   ├── .phone-status-bar  # iOS 状态栏（时间 + 灵动岛同行 + 信号/WiFi/电池）
            │   │   ├── .sb-time       # 当前时间
            │   │   ├── .dynamic-island # 灵动岛 · 紧凑圆点 → 胶囊 · hover 展开
            │   │   └── .sb-icons      # 信号 / WiFi / 电池 SVG 图标
            │   ├── .di-dropdown       # 灵动岛下拉控制面板（v-if 切换）
            │   │   ├── .di-dd-header  # 标题行（Logo + "金陵阡陌 AI 助手" + 模式标签）
            │   │   └── .di-dd-actions # 5 个操作按钮（动效/吸附/设置/清空/关闭）
            │   └── .di-mode-switcher  # 预留（未来模式切换入口）
            ├── .chat-body             # 消息区（空状态 / 消息列表 / 打字中）
            ├── .scroll-bottom-btn     # 回到底部浮动按钮
            ├── .chat-footer           # 输入区
            │   └── .chat-input-wrap   # 输入框胶囊
            └── .resize-handle-{br/bl/tr/tl}  # 四角缩放把手（Phase 12 新增）
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
| 生成中微光 | `fab-glow` 呼吸光晕，按模式变色 (chat 蓝 / query 红 / summary 琥珀)，`reduce-motion` 禁用 |
| 亮色 | `rgba(255,255,255,0.7)` 白玻璃 + 蓝色 hover 边框 |

### 2.3 Double-Bezel 玻璃系统

#### 外壳 — `.panel-shell`

| 属性 | 暗色 | 亮色 |
|------|------|------|
| 背景 | `rgba(5,18,42,0.38)` | `linear-gradient(150deg, 蓝白→紫白→粉白)` |
| blur | `28px saturate(110%)` | 同 |
| 边框 | `1.5px solid rgba(100,180,255,0.1)` | `1.5px solid rgba(180,200,230,0.25)` |
| 圆角 | 默认 `24px`；drawer-open 时 `0 24px 24px 0`（左侧平直与抽屉融合） | 同 |
| border-left (drawer-open) | `none`（由 conv-list-panel 承接） | 同 |
| 内阴影 | 顶部高光 `inset 0 1px 0 rgba(255,255,255,0.1)` + 底部暗边 `inset 0 -1px 0 rgba(0,0,0,0.18)` | 同理亮色版本 |
| 外阴影 | 三层设备级投影，模拟手机壳体厚度 |
| 伪元素 `::before` | 双径向光球（蓝左上 + 紫右下） | 单径向光球（蓝左上） |
| 伪元素 `::after` | 斜向金属高光线 | 同 |
| align-self (drawer-open) | `stretch`（与抽屉等高对齐） | 同 |

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

### 2.4 会话列表抽屉 — `.conv-list-panel`

**Phase 12 重构为一元化**：抽屉与面板背景、边框、光效完全统一，视觉上为一体。

| 特性 | 值 |
|------|-----|
| 位置 | Flex 子元素，面板左侧滑出，打开时面板等比收缩 |
| 宽度 | `max-width: 0` → `var(--conv-list-width)`（`clamp(195px,12vw,250px)`） |
| 动画 | `transition: max-width, opacity` |
| 背景 | 与 panel-shell 完全一致的多层渐变 + `blur(28px) saturate(110%)` |
| 边框 | `1.5px solid rgba(100,180,255,0.1)`（与 panel-shell 统一） |
| 伪元素 `::before` | 径向光晕（与 shell 对齐） |
| 伪元素 `::after` | 斜向金属高光 |
| 圆角 | `24px 0 0 24px`（左侧圆角，右侧平直与面板融合） |
| 面板侧 border-left (drawer-open) | `none`（消除接缝） |
| 面板侧 align-self | `stretch`（消除底部错位） |
| 内层 | 固定宽度防回流 |
| 会话项 | 交错入场 `convItemIn`（40ms stagger），hover 高亮，active 左边框 + 蓝紫底色 |
| 上限 | 最多 20 个会话，超出禁用新建按钮 |
| z-index | `1015`，高于侧栏(1010) |

**亮色主题**：白色半透明 + 浅色边框，与 panel-shell 的亮色渐变同步。

### 2.5 侧栏 — `.side-rail`

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

**"水面灌满"动画**：hover 时 `::before` 伪元素 `clip-path: inset(100% 0 0 0) → inset(0 0 0 0)` 自下而上灌满纯色填充

**引导大圆脉冲动画**：
```css
@keyframes rail-pulse {
    0%,100% { box-shadow: ..., 0 0 0 0 rgba(59,130,246,0.35); }
    50%    { box-shadow: ..., 0 0 0 8px rgba(59,130,246,0); }
}
```

### 2.6 phone-top-section — 上半部分拖拽区域 + 灵动岛

Phase 12 完全重构：移除原有的 `.chat-header` 行，将其功能迁移至灵动岛控制中枢，并在上方叠加 iOS 风格状态栏。

#### 拖拽手柄

整个 `.phone-top-section` 是拖拽手柄（`@mousedown="startDrag"`），覆盖状态栏 + 灵动岛 + 下拉面板全区域。光标 `cursor: grab`，active 时 `grabbing`。

#### iOS 状态栏 — `.phone-status-bar`

```
┌──────────────────────────────────────────┐
│  14:22    ● 金陵阡陌 ▾    ≡  ⌂  ▯▯▯▮⠐  │
│  时间      灵动岛         信号 WiFi 电池   │
└──────────────────────────────────────────┘
```

| 特性 | 值 |
|------|-----|
| 布局 | Flex 三区：左-时间 / 中-灵动岛 / 右-图标 |
| padding | `14px 16px 6px`（480px: `10px 14px`，375px: `8px 10px`） |
| 颜色 | `rgba(255,255,255,0.92)` |
| 字体 | `-apple-system, 'SF Pro Display', 'Helvetica Neue', sans-serif` |
| 时间 | 计算属性 `currentTime`，格式 `HH:MM` |
| 信号图标 | 20×13px SVG，四条高度递减圆角条 |
| WiFi 图标 | 18×13px SVG，三弧 + 中心点 |
| 电池图标 | 28×13px SVG，外壳 + 正极帽 + 满电填充 |
| 图标间距 | `7px` |

SVG 路径源自 ContraQuest 项目的 iOS 原生设计，保证与 iPhone 状态栏像素级一致。

#### 灵动岛 — `.dynamic-island`

三态演化：

| 状态 | 视觉 | 触发 |
|------|------|------|
| **默认** | 32×32px 纯色实心圆（无文字） | 无交互 |
| **hover** | 胶囊展开（`min-width: 140px`），文字 "● 金陵阡陌 ▾" 渐显 | 鼠标悬浮 |
| **expanded** | 同上 + 下方弹出 `.di-dropdown` 下拉面板 | 点击 |
| **streaming** | 强制展开（防止回复中用户找不到控制区） | LLM 流式输出中 |

**模式色映射**：

| 模式 | 默认圆色 | 展开发光 | 下拉面板边框 |
|------|---------|---------|------------|
| chat | 蓝 `#3b82f6` | 蓝色微光 `rgba(59,130,246,0.2)` | `rgba(59,130,246,0.15)` |
| query | 红 `#ef4444` | 红色微光 `rgba(239,68,68,0.2)` | `rgba(239,68,68,0.18)` |
| summary | 琥珀 `#f59e0b` | 琥珀微光 `rgba(245,158,11,0.2)` | `rgba(245,158,11,0.18)` |

**亮色主题**：默认态同样使用模式纯色，展开后切换为白色毛玻璃底。

**动画曲线**：`cubic-bezier(0.25, 1.1, 0.4, 1)`（弹簧缓出），`min-width`/`max-width`/`border-radius`/`gap`/`opacity` 联合过渡。

**无障碍**：`role="button"` + `aria-expanded`。

#### 下拉控制面板 — `.di-dropdown`

从灵动岛下方弹出，两者视觉无断层（共享背景色，无缝连接）：

```
┌──────────────────────────────────────┐
│  🤖 金陵阡陌 AI 助手                  │
│  数据查询模式（模式色文字）            │
│  ──────────────────────────────────  │
│  [▶∥]  [⇄⇥]  [⚙]  [+]  [✕]        │
└──────────────────────────────────────┘
```

| 特性 | 值 |
|------|-----|
| 定位 | `absolute`，top 在灵动岛下方 |
| 宽度 | `220px` |
| 背景 | `rgba(10,25,50,0.92)` + `blur(24px)` |
| 边框 | `1px solid rgba(mode-color, 0.15-0.18)` |
| 光晕 | 同色系 `box-shadow` 微光 |
| Logo 底色 | `rgba(mode-color, 0.15)`，随模式切换 |
| 副标题文字 | 模式色（query 红 / summary 琥珀 / 默认灰色） |
| 按钮栏 | 5 个圆形按钮 + 中间分隔线（模式色调） |
| 关闭 | 点击灵动岛本身 toggle、点击页面其他位置自动收起 |
| z-index | `15`（高于消息区，低于 resize-handle） |

**按钮功能**：
1. 动态效果切换（播放/暂停图标）
2. 吸附/取消吸附到右侧
3. AI 助手设置（`openSettings`）
4. 清空当前对话
5. 关闭面板（返回 FAB）

**亮色主题**：白色底 + 浅色边框 + 更低透明度模式色。

### 2.7 底部 `.chat-footer` + 输入框 `.chat-input-wrap`

**消息区景深分层**：`.chat-body` 添加 `linear-gradient` 背景（浅→深），比底部输入区稍亮，模拟"近深远浅"的玻璃折射感，与 `.chat-footer` 的深色底形成视觉对比。

| 特性 | 值 |
|------|-----|
| 背景 | `rgba(3,12,28,0.85)` + `blur(24px)`，顶部分隔线 `rgba(0,180,240,0.08)` |
| 输入框形状 | 胶囊形 `border-radius: 24px` |
| 输入框背景 | `linear-gradient(145deg, 深蓝→深蓝)` 三色渐变模拟金属凹陷 |
| 输入框伪元素 | `::before` 顶部光带 `linear-gradient(180deg, 蓝光→transparent)` |
| focus-within | 蓝光边框 + 4px 扩散光晕 `rgba(59,130,246,0.18)` + `scale(1.008)` |
| 字体 | `font-size: 14px`，`padding: 9px 0` |
| placeholder | `rgba(255,255,255,0.55)`（WCAG AA 对比度） |
| 发送按钮 | 蓝色渐变圆形，`align-self: center` 垂直居中，hover `scale(1.06)` + 扩散阴影 |
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
| 高光条 | — | `::after` 1px 顶部高光线，两端透明中间 `rgba(255,255,255,0.12)` | — |
| 模式色 | query(红) / summary(琥珀) | 无变化 | query(红) / summary(琥珀) |
| 代码块 | `pre` 暗底 + `code` 内联标记 | 同 | 同 |
| strong | `--brand-accent: #60a5fa` | 同 | `#2563eb` |

**消息入场动画**: `msgSlideIn` — `translateY(12px) scale(0.97)` → 原位，`cubic-bezier(0.16,1,0.3,1)`，60ms stagger

**消息操作**: hover 显示复制 + 重试按钮。复制成功后 "已复制" toast。出错/中断的消息显示重试按钮。

### 2.9 欢迎区（空状态）— Phase 12 重构为灵动岛引导

```
welcome-robot-icon (40px SVG, 居中)
  ↓
"你好！我是金陵阡陌 AI 助手" (16px, 600w)
  ↓
"点击顶部灵动岛可展开控制面板，如需切换功能模式：" (引导标签)
  ↓
三种模式能力统一列表:
  1. 对话模式：导航定位、任务查询、通用问答
  2. 数据查询：统计分析航线、任务、异常数据
  3. 智能摘要：对选中要素自动生成分析报告
  ↓
分割线 (1px rgba white 0.04)
  ↓
"💡 试试下方快捷提问，或点击顶部灵动岛展开更多设置"
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
| 拖拽 | phone-top-section `@mousedown` → `mousemove` 计算百分比位置 → `mouseup`。边界碰撞检测 4px 阈值。 |
| 四角缩放 | resize-handle-{br/bl/tr/tl} `@mousedown` 传入角落标识 → `mousemove` 计算增量和位移 → `mouseup`。左侧/顶部方向同步移动面板位置。范围 360-35vw × 420-85vh。 |
| 吸附 | `docked` 切换：全高右栏 `width: clamp(340px,22vw,460px)`，圆角收窄。 |
| 窗口缩放 | `resize` 事件重夹持 dragPos 百分比，wrapper `max-width: calc(100dvw - 64px)` 硬截断。 |
| 面板关闭 | GSAP `to({ opacity: 0, scale: 0.92 })` → `visible = false` → 重置 `convListVisible`。 |
| 点击外部收起 | `_onDocMouseDown` 检测 `.chat-wrapper` 外点击 → `closeChat()`（docked 模式下不触发）。 |
| 并发锁 | `_animating`(300ms 动画锁) + `_sending`(发送锁) + `streaming` watcher 自动释放。 |

**四角缩放手柄**：

| 位置 | CSS 光标 | 三角指示器方向 | 行为 |
|------|---------|-------------|------|
| 右下 (br) | `nwse-resize` | 135deg ▼ | 向右下增大宽高 |
| 左下 (bl) | `nesw-resize` | 45deg ▼ | 向左下增大宽高 + 同步移动 left |
| 右上 (tr) | `nesw-resize` | 225deg ▲ | 向右上增大宽高 + 同步移动 top |
| 左上 (tl) | `nwse-resize` | 315deg ▲ | 向左上增大宽高 + 同步移动 left+top |

手柄尺寸 8×8px，三角指示器使用 `box-shadow` 对角遮罩实现，深色主题白色三角、亮色主题黑色三角。

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

### 3.1 背景系统

| 层级 | 元素 | 说明 |
|------|------|------|
| z-index: 0 | `.aurora-canvas` | WebGL Ether Shader 动态极光（仅深色+非减少动效） |
| z-index: 0 | `.ambient-orbs` | 4 个固定定位高斯模糊光斑，分布于页面四角，`filter: blur(100px)`，三模式颜色联动 1.2s 过渡，亮暗双主题适配，`reduce-motion` 隐藏 |
| z-index: 0 (sticky) | `.marquee-strip` | Hallmark Ft8 风格水平无限滚动跑马灯，`position: sticky; top: 0`，p+2px 双边框 + `text-shadow` 文字发光 + `backdrop-filter` 玻璃底座，32s 周期，三模式颜色联动，`reduce-motion` 冻结 |
| z-index: 1 | `.light-gradient-overlay` | 亮色模式纯 CSS 渐变层（页面温度 + 右上自然光），零 JS 零动画 |
| z-index: 2 | `.settings-main` | 主内容容器，`max-width: 880px`，居中 |

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
- hover: 边框提亮 + `transform: translateY(-2px)` 抬升 + 外阴影加深 `0 14px 44px rgba(0,0,0,0.5)`
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
| 重新展示侧栏引导 | 时钟图标 | 重置 `localStorage.skyeye_rail_onboard` → 0 |
| 恢复默认 | 刷新图标 | 重置所有设置项 + 提示词模板到默认值 |

### 3.7 页面动画序列

1. **打字机**（非 reduceMotion）: eyebrow "AI 助手" (50ms) → title "设置" (70ms) → subtitle "个性化你的智能对话体验" (40ms)，光标闪烁 `cursor-blink`
2. **滚动触发布局入场**: 打字机完成后，`IntersectionObserver` 监听 5 张 `.curtain-item` 卡片，`threshold: 0.1` + `rootMargin: 0px 0px -8% 0px`，卡片滚入视口时逐个添加 `.curtain-revealed` 触发入场动画（`opacity/brightness/transform` 过渡），one-shot `unobserve`。`reduceMotion` 时直接全量显示。

### 3.8 滚动词条装饰 — `.marquee-strip`

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
| 动画 | `marquee-scroll` 32s 线性无限循环，`translateX(-50%)` |
| 世界发光 | `text-shadow: 0 0 12px rgba(靛蓝, 0.25)` |
| 无障碍 | `aria-hidden="true"`，`pointer-events: none` |

### 3.9 两侧氛围光斑 — `.ambient-orbs`

4 个固定定位的高斯模糊光斑，填充页面两侧空档，与三模式颜色联动。

| 光斑 | 位置 | 尺寸 | 默认颜色 | 说明 |
|------|------|------|---------|------|
| `.orb--tl` | `top: -8%; left: -5%` | 320×320px | indigo `rgb(99,102,241)` | 左上角主光斑 |
| `.orb--tr` | `top: 12%; right: -3%` | 260×260px | cyan `rgb(56,189,248)` | 右上角补光 |
| `.orb--br` | `bottom: -10%; right: -6%` | 380×380px | violet `rgb(139,92,246)` | 右下角最大光斑 |
| `.orb--ml` | `top: 55%; left: -4%` | 220×220px | indigo `rgb(99,102,241)` | 左侧中部补充 |

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

---

## 4. 共享设计要素

### 4.1 颜色系统

#### AI 语义 Token 架构

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

#### 原有 Token

| Token | 用途 |
|-------|------|
| `--app-accent: #6366f1` | FAB badge、active 标记 |
| `--brand-accent: #60a5fa` (暗) / `#2563eb` (亮) | 消息 strong、流式光标、dot-pulse |
| 蓝紫 `#3b82f6 / #2563eb` | 发送按钮、用户气泡、focus 光环 |
| 红 `#ef4444 / #dc2626` | query 模式（边框/头部/底部/气泡/侧栏/灵动岛） |
| 琥珀 `#f59e0b / #d97706` | summary 模式（边框/头部/底部/气泡/侧栏/灵动岛） |

### 4.2 动画缓动函数

| 用途 | 函数 |
|------|------|
| 面板开合、拖拽、四角缩放 | `cubic-bezier(0.16, 1, 0.3, 1)` (ease-out-expo 风格) |
| 灵动岛展开/收起 | `cubic-bezier(0.25, 1.1, 0.4, 1)` (弹簧缓出) |
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
- 灵动岛 `role="button"` + `aria-expanded`
- `:focus-visible` 紫色轮廓环（`outline: 2px solid rgba(99,102,241,0.6)`）
- `@media (prefers-reduced-motion: reduce)` 全局关闭所有动画
- ChatModel 键盘操作：`Ctrl+K` 唤起，`Esc` 关闭，`Enter` 发送
- **WCAG AA 对比度**: aiSettings 暗色模式 14 处文本颜色提升至 ≥4.5:1 (正文) / ≥3:1 (辅助文字/placeholder)

---

## 5. 响应式断点

| 断点 | 行为 |
|------|------|
| `max-width: 768px` | aiSettings 便当盒退化为单列，padding 减少 |
| `max-width: 480px` | ChatModel 状态栏 padding 收缩、图标缩小 |
| `max-width: 375px` | ChatModel 状态栏最小化、灵动岛文字隐藏 |
| `max-width: calc(100dvw - 64px)` | ChatModel wrapper 硬截断防止溢出 |
| 窗口 resize | ChatModel 重夹持 `dragPos` 百分比，`_onWindowResize` |
| drawer open | wrapper `max-width` 减去 `--conv-list-width` |
