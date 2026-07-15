# 金陵阡陌 — AI 助手 (Phase 5)

无人机巡检智能平台前端，集成 AI 对话面板与可视化参数设置。

## 技术栈

| 层 | 技术 |
|---|------|
| 框架 | Vue 2 + Vuex + Vue Router |
| UI 库 | Element UI |
| 动效 | GSAP + WebGL Shader + CSS Animation |
| 地图 | 天地图 (TMap) |
| 样式 | SCSS + CSS 自定义属性 (cyber-tokens) |

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

- Dock 模式下滚动条出现导致右侧缩进 → 锁定 `.chat-panel.docked` 宽度
- tooltip 被 `.pod-core` overflow:hidden 裁剪 → 移除 overflow 限制 + 右侧防出界对齐
- 导航清空对话历史 → 改为保留历史 + FAB badge 指示
- 打字机动画在 reduceMotion 下仍播放 → 跳过动画直接渲染
- 工具调用空白 assistant 消息残留 → 导航分支清理中间消息

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
