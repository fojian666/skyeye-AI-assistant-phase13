---
target: ChatModel.vue
total_score: 27
p0_count: 0
p1_count: 2
timestamp: 2026-07-14T06-04-08Z
slug: skyeye-ui-src-components-chat-chatmodel-vue
---
# ChatModel.vue — Impeccable Critique

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Phase indicators excellent; no loading feedback between send and first phase |
| 2 | Match System / Real World | 3 | Chat metaphor solid; "Powered by DeepSeek" is jargon |
| 3 | User Control and Freedom | 3 | Clear exits; no Esc key, no draft preservation |
| 4 | Consistency and Standards | 3 | Mode colors well-executed; minor FAB/header emoji inconsistency |
| 5 | Error Prevention | 3 | ClearMessages confirm dialog good; no close-during-streaming guard |
| 6 | Recognition Rather Than Recall | 3 | Quick questions + toast; side-rail icon-only |
| 7 | Flexibility and Efficiency of Use | 2 | No keyboard shortcuts; no Shift+Enter |
| 8 | Aesthetic and Minimalist Design | 3 | Double-bezel crafted; breathe-glow adds noise |
| 9 | Error Recovery | 2 | Retry exists; errors could be more actionable |
| 10 | Help and Documentation | 2 | Friendly empty state; no mode explanation |
| **Total** | | **27/40** | **Acceptable** |

## Anti-Patterns Verdict

**LLM**: Not AI-generated at first glance. Double-bezel, dock/undock, phase indicators, side-rail scatter are deliberate. Glassmorphism overuse (7+ backdrop-filter sites), bounce easing on open (`back.out(1.7)`), and breathe-glow ring push toward AI-tell territory but remain polish-level.

**Detector**: 2 findings — 1 false positive (dot-bounce name match, actual animation is transform-based), 1 valid (`transition: height` on `.chat-panel`).

## Priority Issues

- **[P1] No keyboard accessibility**: Esc to close missing, no Cmd+K to toggle, no Shift+Enter. WCAG violation for `role="dialog"`.
- **[P1] Glassmorphism overuse**: 7+ elements with `backdrop-filter: blur()`. Quick question buttons and input wrap pseudo-element don't earn their blur.
- **[P2] Bounce easing on open**: `back.out(1.7)` should be `power3.out` or `expo.out`.
- **[P2] `transition: height` triggers layout reflow**: Minor in practice but flagged by detector.
- **[P2] No draft preservation**: Input lost on accidental close.

## Persona Red Flags

- **Alex**: No keyboard shortcuts, no Shift+Enter, no message search
- **Jordan**: Side-rail icon-only, "Powered by DeepSeek" jargon, mode purpose unclear
- **Sam**: No Esc, FAB lacks aria-label, phase changes not announced to screen readers

## Minor Observations

- FAB emoji vs header emoji inconsistency (🤖 vs &#x1F916;)
- Dead CSS: `.chat-header h3` targets non-existent element
- Inline style on tool-info should be a CSS class
- `|||` separator fragile against literal AI output
