# 金陵阡陌 — AI 助手 (Phase 8)

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

## Phase 5 新增功能

### AI 对话面板 (`ChatModel.vue`)

- **多模式对话**: 聊天 / 数据查询 / 智能摘要，模式切换联动面板配色
- **工具调用**: LLM 可通过 `navigate_page`、`map_action`、`lookup_task`、`query_data` 四个工具控制系统行为
- **流式渲染**: SSE 流式响应 + 打字机效果 + 阶段指示器（理解中/查询中/生成中）
- **交互增强**: 拖拽定位、右下吸附 (dock)、四角缩放、侧栏快捷操作、Cmd+K 快捷键
- **视觉系统**: iOS 26 Liquid Glass 双层玻璃 (panel-shell + chat-panel)、backdrop-filter 模糊、多模式光晕
- **无障碍**: focus-visible 键盘导航、aria-label、prefers-reduced-motion、reduceMotion 手动开关

### AI 设置页 (`aiSettings/index.vue`)

- **打字机入场**: 标题/副标题逐字打印 + 卡片幕布揭幕动画
- **模型与参数**: DeepSeek-V3 / R1 选择、Temperature 滑块（四段颜色映射）、MaxTokens 文本域 + 预览条
- **对话默认**: 三模式默认选择、自动摘要开关、减少动态效果、组合快捷键参考
- **数据持久化**: localStorage 双向同步，ChatModel 和设置页共享 `skyeye_ai_settings` 键
- **从聊天打开设置**: LLM 意图推理 `navigate_page` → 设置页返回自动恢复聊天面板（sessionStorage 闭环）
- **视觉系统**: WebGL 极光着色器 + CSS 呼吸光斑 + 噪声纹理 + 双层玻璃卡片 (pod-shell/pod-core)
- **工具提示**: 自定义 tooltip 气泡，支持防出界对齐

### 设计 Token (`cyber-tokens.css`)

- `--app-accent` (indigo #6366f1) 统一主色调
- `--radius-sm/md/lg/xl/2xl` 六级圆角弹性系统
- `--font-mono` 代码/数据等宽字体栈

### 修复记录

#### Phase 5
- Dock 模式下滚动条出现导致右侧缩进 → 锁定 `.chat-panel.docked` 宽度
- tooltip 被 `.pod-core` overflow:hidden 裁剪 → 移除 overflow 限制 + 右侧防出界对齐
- 导航清空对话历史 → 改为保留历史 + FAB badge 指示
- 打字机动画在 reduceMotion 下仍播放 → 跳过动画直接渲染
- 工具调用空白 assistant 消息残留 → 导航分支清理中间消息

#### Phase 6 鲁棒性加固

- **13 项生命周期清理**: `beforeDestroy` 中 AbortController.abort() / GSAP killTweensOf / 定时器清理 / WebGL rAF 取消 / copyTimer / mapDispatchTimer
- **fetch 60s 硬超时**: setTimeout + AbortController，防止请求永久挂起
- **打字机生命周期保护**: `_typewriterCancelled` 标志，路由跳转后立即停止
- **JSON.parse 保护**: LLM 畸形参数 → 捕获并显示友好错误气泡，不死锁 streaming
- **`_storageError` 可重置**: 存储恢复后警告横幅自动消失
- **`savePrefs` 300ms 防抖**: 快速拖 slider 只写一次 localStorage
- **输入防护**: textarea `maxlength=5000` + 字符计数提示 + trim 空消息拦截

#### Phase 6 交互增强

- **工具冲突裁决**: 四个工具 (`navigate_page`/`map_action`/`lookup_task`/`query_data`) 互相引反例 + 后端 5 条裁决规则；消除"数据概览"→误跳页面的歧义
- **三层并发锁**: 动画锁 (模式切换/dock 400ms) + 发送锁 (防重复提交) + streaming watcher 自动释放
- **多模式用户气泡**: 用户消息随 chat(蓝)/query(红)/summary(琥珀) 模式变色，亮暗双主题适配
- **eyebrow 排版修复**: 去 uppercase + 字号 11→12px + letter-spacing 收紧

#### Phase 7 液玻璃视觉重塑 & 引导式 Onboarding

- **侧栏渐进式引导**: 前 3 次打开面板展示圆点 + 文字标签（会话/对话/设置），大圆呼吸脉冲，localStorage 持久化计数，3 次后回归 hover-only
- **欢迎区重构**: 机器人图标居中 → 能力列表（3 条业务说明）→ 分割线 → 操作提示
- **液玻璃背景**: 深色模式用径向光球替代 linear-gradient，亮色模式用微渐变底色解决"白上叠白"
- **定向光叠加层**: panel-shell/chat-header/chat-footer/消息气泡各加 `::before` 线性光伪元素
- **玻璃折射高光线**: `box-shadow` 双层 inset（顶部高光 + 底部暗边）
- **输入框聚焦光环**: `focus-within` 扩散光晕 + `scale(1.008)`
- **响应式硬约束**: `max-width: calc(100vw - 64px)` 防止面板被挤出
- **fab badge 修复**: `lastReadMsgCount` 替代 `visible` 判断

#### Phase 8 设计 Token 体系化 & Surface 深度层次

- **AI 语义 Token 体系**: 92 个 Token 8 大类（文本/玻璃/边框/模式色/光晕/模糊/交互态/组件级+投影），亮暗双主题自动切换
- **硬编码值 Token 化**: ChatModel 16 处 + aiSettings 51 处硬编码值替换为语义 Token
- **WCAG AA 对比度**: aiSettings 暗色模式 16 处文本颜色提升至 ≥4.5:1 (正文) / ≥3:1 (辅助)
- **Surface 深度层次**: 卡片 hover 抬升 (translateY -2px)、bg-orb 滚动视差、消息区景深渐变 (.chat-body)
- **气泡顶部高光条**: `.msg-content::after` 1px 光线掠射
- **发送按钮居中**: `.chat-send-btn` 添加 `align-self: center`

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
