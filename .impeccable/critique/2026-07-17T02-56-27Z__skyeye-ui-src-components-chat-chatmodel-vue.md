---
target: ChatModel.vue
total_score: 25
p0_count: 1
p1_count: 1
timestamp: 2026-07-17T02-56-27Z
slug: skyeye-ui-src-components-chat-chatmodel-vue
---
## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3/4 | 流式阶段指示器、复制 Toast 到位；缺进度预估 |
| 2 | Match System / Real World | 3/4 | 对话隐喻自然；侧栏按钮无标签 |
| 3 | User Control and Freedom | 3/4 | Esc/Cmd+K/拖拽齐全；清空无二次确认 |
| 4 | Consistency and Standards | 2/4 | ChatModel `.theme-light` vs aiSettings `[data-theme='light']` 两套主题约定 |
| 5 | Error Prevention | 3/4 | 发送锁、空值禁用；设置页离开无未保存提示 |
| 6 | Recognition Rather Than Recall | 3/4 | 模式芯片图标+文字双重编码；侧栏轨道纯图标 |
| 7 | Flexibility and Efficiency | 3/4 | 快捷键丰富；缺对话搜索、导出 |
| 8 | Aesthetic and Minimalist Design | 1/4 | 4层背景 + 双层毛玻璃 + 3层阴影 = 视觉过载 |
| 9 | Error Recovery | 2/4 | 重试按钮到位；缺自动重试、离线队列 |
| 10 | Help and Documentation | 2/4 | tooltip 覆盖到位；无首次引导、无键盘可触达 |
| **Total** | | **25/40** | **Acceptable — significant improvements needed** |

## Anti-Patterns Verdict

**LLM assessment**: 视觉层 6/9 高置信度 slop 信号命中（毛玻璃默认语言、幽灵卡片、渐变文字/按钮、噪点网格背景、saturate 叠加、便当布局），但代码层有大量反 slop 工程决策（双路径 reduced-motion、并发锁、localStorage 降级标志）。整体视觉被 AI slop 审美主导但未被完全覆盖。

**Deterministic scan**: detect.mjs 检出 4 条 layout-transition 警告：
- ChatModel:2055 `.fab-label max-width` (debatable，可保留)
- ChatModel:2240 `.conv-list-panel max-width` (false positive，抽屉合法场景)
- ChatModel:2591 `.chat-panel height` (true positive，resize 时 layout thrash)
- aiSettings:2158 `.token-fill width` (debatable，极低影响)
- 漏报：ChatModel:2022 `.chat-fab transition: all` + `padding` 应明确列出 composite-only 属性

## What's Working

1. 主题系统完整度极高 — `.theme-light` 覆盖所有 DOM 元素和状态，浅色模式颜色/阴影/渐变/光晕全部独立重写
2. 运动可访问性双保险 — `reduce-motion` 手动开关 + `@media (prefers-reduced-motion)` 共存
3. 并发安全防护到位 — `_sending`/`_animating`/`_syncingConv`/`_restoring` 多道锁

## Priority Issues

### P0 — 4层实时模糊合成导致 GPU 压力
chat-panel 每帧渲染: WebGL 极光 + 3 CSS 光斑(80px blur each) + SVG 噪点 + panel-shell blur(22px) + chat-panel blur(44px) + 双层 box-shadow。低端设备滚动帧率可能降至 30fps。
**Fix**: 面板用 CSS 渐变替代 backdrop-filter；仅保留最外层一个 blur

### P1 — 视觉层级塌陷：毛玻璃过度使用
shell+core 双层 blur 无差别应用。消息气泡渐变被外层 44px blur 柔化，可读性反降。
**Fix**: 移除 pod-core 的 backdrop-filter；聊天面板用纯色半透明替代双层 blur

### P2 — 主题选择器不一致
ChatModel `.theme-light` vs aiSettings `[data-theme='light']` — 约 130 条 `.theme-light` 规则几乎全是颜色覆盖。
**Fix**: 统一为 CSS custom properties

### P3 — 侧栏轨道发现性为0
3 个 rail 按钮默认 opacity:0/scale(0)，仅 hover 展开，无标签，hint 只播一次 2.5s 后永久消失
**Fix**: 首次打开时 rail 始终可见 + 标签，5s 后渐进消退

## Persona Red Flags

**Alex (Power User)**: 无自定义快捷键重映射、无对话内搜索、设置页打字机标题每次重播
**Jordan (First-Timer)**: 无 onboarding、侧栏 hint 只播一次、玻璃弱化了控件可点击感
**Sam (Accessibility)**: placeholder 声称 4.5:1 实际 ~3.8:1、tooltip 仅 hover 触发、缩放把手无 aria-label

## Minor Observations

1. GSAP 动画硬编码颜色值 — 主题切换后不自动适配
2. 设置页打字机每次进入都重播 — 反复访问者被浪费 2 秒
3. ChatModel:2022 `.chat-fab transition: all` — 应明确列出 composite-only 属性
4. SVG 图标内联重复 — gear 图标在 3 处完整内联
5. `strong` 标签全局覆盖 `color: var(--brand-accent)` — 语义冲突

## Questions to Consider

1. 如果去掉全部 backdrop-filter，还剩什么设计语言？
2. GIS 巡检工具的用户在户外强光下使用 — 深黑+霓虹色系是否适合？
3. Temperature 滑块用错了交互模式 — 用户真正需要的是预览同 prompt 在不同 temperature 下的输出差异
