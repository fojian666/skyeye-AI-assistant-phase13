    <template>
    <div class="settings-root" :class="[`theme-${theme}`, { 'reduce-motion': reduceMotion }]">
        <!-- Canvas: 动态极光 + 粒子连接网 -->
        <canvas ref="auroraCanvas" class="aurora-canvas" aria-hidden="true"></canvas>

        <!-- 亮色模式背景氛围光 (纯 CSS，无动画) -->
        <div class="light-gradient-overlay" aria-hidden="true"></div>

        <!-- 滚动词条装饰 -->
        <div class="marquee-strip" :class="'marquee--' + defaultMode" aria-hidden="true">
            <div class="marquee-track">
                <span>DeepSeek-V3</span> <span class="marquee-dot">·</span>
                <span>DeepSeek-R1</span> <span class="marquee-dot">·</span>
                <span>智能推理</span> <span class="marquee-dot">·</span>
                <span>数据查询</span> <span class="marquee-dot">·</span>
                <span>AI 摘要</span> <span class="marquee-dot">·</span>
                <span>变化检测</span> <span class="marquee-dot">·</span>
                <span>图像分割</span> <span class="marquee-dot">·</span>
                <span>航线规划</span> <span class="marquee-dot">·</span>
                <!-- 第二份副本实现无缝循环 -->
                <span>DeepSeek-V3</span> <span class="marquee-dot">·</span>
                <span>DeepSeek-R1</span> <span class="marquee-dot">·</span>
                <span>智能推理</span> <span class="marquee-dot">·</span>
                <span>数据查询</span> <span class="marquee-dot">·</span>
                <span>AI 摘要</span> <span class="marquee-dot">·</span>
                <span>变化检测</span> <span class="marquee-dot">·</span>
                <span>图像分割</span> <span class="marquee-dot">·</span>
                <span>航线规划</span> <span class="marquee-dot">·</span>
            </div>
        </div>

        <!-- 两侧氛围光斑 -->
        <div class="ambient-orbs" :class="'orbs--' + defaultMode" aria-hidden="true">
            <div class="orb orb--tl"></div>
            <div class="orb orb--tr"></div>
            <div class="orb orb--br"></div>
            <div class="orb orb--ml"></div>
        </div>

        <main class="settings-main">
            <!-- 返回按钮 -->
            <button class="back-btn" @click="$router.back()" aria-label="返回">
                <svg
                    class="icon"
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round">
                    <path d="m12 19-7-7 7-7" />
                    <path d="M19 12H5" />
                </svg>
            </button>

            <!-- 头部：打字机标题 -->
            <header ref="headerEl" class="page-header">
                <span class="eyebrow"> {{ typedEyebrow }}<span v-if="typingLine === 'eyebrow'" class="typing-cursor">|</span> </span>
                <h1>{{ typedTitle }}<span v-if="typingLine === 'title'" class="typing-cursor">|</span></h1>
                <p class="subtitle">{{ typedSubtitle }}<span v-if="typingLine === 'subtitle'" class="typing-cursor">|</span></p>
            </header>

            <!-- 便当盒网格 -->
            <div class="bento-grid">
                <!-- ===== 模型与参数 (占 2 列) ===== -->
                <div ref="card1" class="card-pod col-wide curtain-item curtain-bottom">
                    <!-- 外壳 -->
                    <div class="pod-shell">
                        <!-- 内核 -->
                        <div class="pod-core">
                            <div class="pod-icon-wrap">
                                <svg
                                    class="pod-icon"
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="20"
                                    height="20"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    stroke-linecap="round"
                                    stroke-linejoin="round">
                                    <path
                                        d="M12 4.5a2.5 2.5 0 0 0-4.96-.46 2.5 2.5 0 0 0-1.98 3 2.5 2.5 0 0 0-1.32 4.24 3 3 0 0 0 .34 5.58 2.5 2.5 0 0 0 2.96 3.08A2.5 2.5 0 0 0 12 19.5a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 12 4.5Z" />
                                    <path d="m14.5 12-4.5 4.5L8 14.5" />
                                </svg>
                            </div>
                            <h3>模型与参数</h3>
                            <p class="pod-desc">控制 AI 回复的创造性与精确度</p>

                            <div class="field-group">
                                <label class="field-label">
                                    模型选择
                                    <span
                                        class="field-help"
                                        data-tip="DeepSeek-V3 适合日常对话与快速问答；R1 适合复杂分析（图斑变化、报告生成），响应稍慢但推理更深入"
                                        >?</span
                                    >
                                </label>
                                <div class="select-wrap">
                                    <select v-model="model" class="field-select">
                                        <option value="deepseek-chat">DeepSeek-V3 (通用对话)</option>
                                        <option value="deepseek-reasoner">DeepSeek-R1 (深度推理)</option>
                                    </select>
                                    <svg
                                        class="select-chevron"
                                        xmlns="http://www.w3.org/2000/svg"
                                        width="14"
                                        height="14"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                        stroke-linecap="round"
                                        stroke-linejoin="round">
                                        <path d="m6 9 6 6 6-6" />
                                    </svg>
                                </div>
                            </div>

                            <div class="field-group">
                                <div class="field-label-row">
                                    <label class="field-label">
                                        Temperature
                                        <span
                                            class="field-help"
                                            data-tip="控制回复的随机性：0 = 确定性精确，2 = 最大创造性。巡检数据分析建议 0.3-0.7，创意生成建议 0.7-1.2"
                                            >?</span
                                        >
                                    </label>
                                    <span class="field-val temp-val" :class="tempClass" :key="temperature.toFixed(1)">{{
                                        temperature.toFixed(1)
                                    }}</span>
                                </div>
                                <input type="range" class="field-slider" min="0" max="2" step="0.1" v-model.number="temperature" />
                                <div class="slider-hints">
                                    <span>精确</span>
                                    <span>平衡</span>
                                    <span>创造</span>
                                </div>
                            </div>

                            <div class="field-group">
                                <div class="field-label-row">
                                    <label class="field-label">
                                        最大输出长度
                                        <span
                                            class="field-help"
                                            data-tip="控制单次回复的最大 Token 数。512 = 简短摘要，4096 = 标准分析，8192 = 详尽报告（响应时间相应增加）"
                                            >?</span
                                        >
                                    </label>
                                    <span class="field-val">{{ maxTokens.toLocaleString() }}</span>
                                </div>
                                <input type="range" class="field-slider" min="512" max="8192" step="512" v-model.number="maxTokens" />
                                <div class="slider-hints">
                                    <span>512</span>
                                    <span>4096</span>
                                    <span>8192</span>
                                </div>
                                <div class="token-preview-bar">
                                    <span class="token-label">简短回复</span>
                                    <span class="token-track">
                                        <span class="token-fill" :style="{ width: (maxTokens / 8192) * 100 + '%' }"></span>
                                    </span>
                                    <span class="token-label">详尽分析</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ===== 外观 (占 1 列) ===== -->
                <div ref="card2" class="card-pod curtain-item curtain-left">
                    <div class="pod-shell">
                        <div class="pod-core">
                            <div class="pod-icon-wrap">
                                <svg
                                    class="pod-icon"
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="20"
                                    height="20"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    stroke-linecap="round"
                                    stroke-linejoin="round">
                                    <circle cx="13.5" cy="6.5" r="2.5" />
                                    <circle cx="17.5" cy="10.5" r="2.5" />
                                    <circle cx="8.5" cy="7.5" r="2.5" />
                                    <circle cx="6.5" cy="12.5" r="2.5" />
                                    <path
                                        d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z" />
                                </svg>
                            </div>
                            <h3>外观</h3>
                            <p class="pod-desc">视觉偏好与动效控制</p>

                            <div class="field-group">
                                <div class="toggle-row" @click="toggleTheme">
                                    <div>
                                        <label class="field-label toggle-label">深色主题</label>
                                        <span class="toggle-hint">{{ isDark ? '已启用' : '已关闭' }}</span>
                                    </div>
                                    <button class="toggle-switch" :class="{ active: isDark }" role="switch" :aria-checked="isDark">
                                        <span class="toggle-knob"></span>
                                    </button>
                                </div>
                            </div>

                            <div class="field-group">
                                <div class="toggle-row" @click="reduceMotion = !reduceMotion">
                                    <div>
                                        <label class="field-label toggle-label">
                                            减少动态效果
                                            <span class="field-help" data-tip="关闭入场动画与背景动态效果，适合低性能设备或偏好静态界面的用户"
                                                >?</span
                                            >
                                        </label>
                                        <span class="toggle-hint">{{ reduceMotion ? '已启用' : '已关闭' }}</span>
                                    </div>
                                    <button class="toggle-switch" :class="{ active: reduceMotion }" role="switch" :aria-checked="reduceMotion">
                                        <span class="toggle-knob"></span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ===== 对话默认 (占 1 列) ===== -->
                <div ref="card3" class="card-pod curtain-item curtain-right">
                    <div class="pod-shell">
                        <div class="pod-core">
                            <div class="pod-icon-wrap">
                                <svg
                                    class="pod-icon"
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="20"
                                    height="20"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    stroke-linecap="round"
                                    stroke-linejoin="round">
                                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                                </svg>
                            </div>
                            <h3>对话默认</h3>
                            <p class="pod-desc">新对话的起始模式与行为</p>

                            <div class="field-group">
                                <label class="field-label">默认模式</label>
                                <div class="mode-chips">
                                    <button
                                        v-for="m in modes"
                                        :key="m.value"
                                        class="mode-chip"
                                        :class="{ active: defaultMode === m.value }"
                                        :data-mode="m.value"
                                        :title="m.tip"
                                        @click="defaultMode = m.value">
                                        <svg
                                            class="chip-icon"
                                            xmlns="http://www.w3.org/2000/svg"
                                            width="22"
                                            height="22"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            stroke-width="2"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            v-html="m.iconSvg"></svg>
                                        <span class="chip-label">{{ m.label }}</span>
                                    </button>
                                </div>
                            </div>

                            <div class="field-group">
                                <div class="toggle-row" @click="autoSummary = !autoSummary">
                                    <div>
                                        <label class="field-label toggle-label">进入页面时自动摘要</label>
                                        <span class="toggle-hint">有选中对象时触发</span>
                                    </div>
                                    <button class="toggle-switch" :class="{ active: autoSummary }" role="switch" :aria-checked="autoSummary">
                                        <span class="toggle-knob"></span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ===== API 调用频率热力图 (占 1 列) ===== -->
                <div ref="cardHeatmap" class="card-pod col-wide curtain-item curtain-bottom">
                    <div class="pod-shell">
                        <div class="pod-core">
                            <div class="pod-icon-wrap pod-icon-wrap--amber">
                                <svg class="pod-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <rect x="3" y="3" width="7" height="7" rx="1.5" />
                                    <rect x="14" y="3" width="7" height="7" rx="1.5" />
                                    <rect x="14" y="14" width="7" height="7" rx="1.5" />
                                    <rect x="3" y="14" width="7" height="7" rx="1.5" />
                                </svg>
                            </div>
                            <h3>API 调用频率</h3>
                            <p class="pod-desc">近 7 天每小时调用分布</p>
                            <div class="heatmap-grid" aria-label="API 调用频率热力图">
                                <div class="heatmap-header">
                                    <span v-for="d in heatmapDays" :key="d" class="heatmap-day-label">{{ d }}</span>
                                </div>
                                <div class="heatmap-body">
                                    <div v-for="(row, ri) in heatmapData" :key="ri" class="heatmap-row">
                                        <span class="heatmap-hour-label">{{ heatmapHours[ri] }}</span>
                                        <div v-for="(val, ci) in row" :key="ci"
                                            class="heatmap-cell"
                                            :class="'heatmap-cell--' + heatmapLevel(val)"
                                            :title="`${heatmapDays[ci]} ${heatmapHours[ri]}: ${val} 次`">
                                        </div>
                                    </div>
                                </div>
                                <div class="heatmap-legend">
                                    <span class="heatmap-legend-label">少</span>
                                    <span class="heatmap-legend-dot heatmap-cell--low"></span>
                                    <span class="heatmap-legend-dot heatmap-cell--mid"></span>
                                    <span class="heatmap-legend-dot heatmap-cell--high"></span>
                                    <span class="heatmap-legend-dot heatmap-cell--peak"></span>
                                    <span class="heatmap-legend-label">多</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ===== 提示词模板 (占 2 列) ===== -->
                <div ref="card6" class="card-pod col-wide curtain-item curtain-bottom">
                    <div class="pod-shell">
                        <div class="pod-core">
                            <div class="pod-icon-wrap">
                                <svg
                                    class="pod-icon"
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="20"
                                    height="20"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    stroke-linecap="round"
                                    stroke-linejoin="round">
                                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                                </svg>
                            </div>
                            <h3>提示词模板</h3>
                            <p class="pod-desc">为每种对话模式预设快捷提问，最多 5 条</p>

                            <!-- 模式标签切换 -->
                            <div class="template-mode-tabs" role="tablist">
                                <button
                                    v-for="m in modes"
                                    :key="m.value"
                                    class="template-mode-tab"
                                    :class="{ active: templateTab === m.value }"
                                    :data-mode="m.value"
                                    role="tab"
                                    :aria-selected="templateTab === m.value"
                                    @click="templateTab = m.value">
                                    <svg
                                        class="tab-icon"
                                        xmlns="http://www.w3.org/2000/svg"
                                        width="16"
                                        height="16"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        v-html="m.iconSvg"></svg>
                                    <span>{{ m.label }}</span>
                                </button>
                            </div>

                            <!-- 模板列表 -->
                            <transition name="template-fade" mode="out-in">
                                <div class="template-list" :key="templateTab">
                                <div v-for="(item, idx) in currentTemplates" :key="idx" class="template-row">
                                    <span class="template-num">{{ idx + 1 }}</span>
                                    <input
                                        class="template-input"
                                        :value="item"
                                        :placeholder="placeholderForMode[templateTab][idx]"
                                        maxlength="80"
                                        :aria-label="`模板 ${idx + 1}`"
                                        @input="updateTemplate(idx, $event.target.value)" />
                                    <button
                                        v-if="currentTemplates.length > 1"
                                        class="template-del-btn"
                                        @click="removeTemplate(idx)"
                                        tabindex="-1"
                                        aria-label="删除此模板">
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            width="14"
                                            height="14"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            stroke-width="2"
                                            stroke-linecap="round"
                                            stroke-linejoin="round">
                                            <line x1="18" y1="6" x2="6" y2="18" />
                                            <line x1="6" y1="6" x2="18" y2="18" />
                                        </svg>
                                    </button>
                                </div>

                                <button v-if="currentTemplates.length < 5" class="template-add-btn" @click="addTemplate">
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        width="14"
                                        height="14"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                        stroke-linecap="round"
                                        stroke-linejoin="round">
                                        <line x1="12" y1="5" x2="12" y2="19" />
                                        <line x1="5" y1="12" x2="19" y2="12" />
                                    </svg>
                                    添加模板
                                </button>
                                <p v-else class="template-limit-hint">已达上限（5 条）</p>
                            </div>
                            </transition>
                        </div>
                    </div>
                </div>

                <!-- ===== 键盘快捷键 (占 1 列) ===== -->
                <div ref="card4" class="card-pod curtain-item curtain-left">
                    <div class="pod-shell">
                        <div class="pod-core">
                            <div class="pod-icon-wrap">
                                <svg
                                    class="pod-icon"
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="20"
                                    height="20"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    stroke-linecap="round"
                                    stroke-linejoin="round">
                                    <rect x="2" y="4" width="20" height="16" rx="2" />
                                    <path
                                        d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M18 12h.01M6 16h.01M10 16h.01M14 16h.01M18 16h.01" />
                                </svg>
                            </div>
                            <h3>键盘快捷键</h3>
                            <p class="pod-desc">高效操作参考</p>

                            <div class="kbd-list">
                                <div class="kbd-row" v-for="kb in shortcuts" :key="kb.label">
                                    <span class="kbd-label">{{ kb.label }}</span>
                                    <div class="kbd-keys">
                                        <kbd v-for="key in kb.keys" :key="key">{{ key }}</kbd>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ===== 关于 (占 1 列) ===== -->
                <div ref="card5" class="card-pod curtain-item curtain-right">
                    <div class="pod-shell">
                        <div class="pod-core">
                            <div class="pod-icon-wrap">
                                <svg
                                    class="pod-icon"
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="20"
                                    height="20"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    stroke-linecap="round"
                                    stroke-linejoin="round">
                                    <path
                                        d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
                                </svg>
                            </div>
                            <h3>关于</h3>
                            <p class="pod-desc">金陵阡陌 AI 助手</p>

                            <div class="about-meta">
                                <div class="meta-row">
                                    <span class="meta-key">版本</span>
                                    <span class="meta-val version-glow">v2.1.0</span>
                                </div>
                                <div class="meta-row">
                                    <span class="meta-key">引擎</span>
                                    <span class="meta-val">DeepSeek API</span>
                                </div>
                                <div class="meta-row">
                                    <span class="meta-key">框架</span>
                                    <span class="meta-val">Vue 2 + Element UI</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 空白区域漂浮粒子装饰 -->
                <div class="bento-particles" aria-hidden="true">
                    <span v-for="n in 8" :key="n" class="bento-particle" :style="particleStyle(n)"></span>
                </div>
            </div>
            <!-- 操作行 -->
            <div class="actions-bar">
                <button class="btn-reset btn-reset--secondary" @click="resetRailOnboard" aria-label="重新展示侧栏引导">
                    <svg
                        class="btn-reset-icon"
                        xmlns="http://www.w3.org/2000/svg"
                        width="15"
                        height="15"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10" />
                        <path d="M12 8v4l2 2" />
                    </svg>
                    重新展示侧栏引导
                </button>
                <button class="btn-reset" @click="restoreDefaults" aria-label="恢复默认设置">
                    <svg
                        class="btn-reset-icon"
                        xmlns="http://www.w3.org/2000/svg"
                        width="15"
                        height="15"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round">
                        <polyline points="1 4 1 10 7 10" />
                        <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
                    </svg>
                    恢复默认
                </button>
            </div>
        </main>

        <!-- 保存确认 Toast -->
        <transition name="toast">
            <div v-if="toastVisible" class="save-toast" :class="{ 'save-toast--error': _storageError }">
                <svg v-if="!_storageError" class="toast-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                </svg>
                <svg v-else class="toast-icon toast-icon--warn" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                <span>{{ toastMessage }}</span>
            </div>
        </transition>

        <!-- localStorage 异常警告 -->
        <div v-if="_storageError" class="storage-warning" role="alert">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            设置无法持久保存，请检查浏览器存储空间或隐私设置
        </div>
    </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
    name: 'AiSettings',

    data() {
        const saved = this._loadPrefs();
        return {
            model: saved.model || 'deepseek-chat',
            temperature: saved.temperature ?? 0.7,
            maxTokens: saved.maxTokens ?? 4096,
            reduceMotion: saved.reduceMotion ?? false,
            defaultMode: saved.defaultMode || 'chat',
            autoSummary: saved.autoSummary ?? false,
            promptTemplates: saved.promptTemplates || this._defaultTemplates(),
            templateTab: 'chat', // 当前编辑的模板模式
            modes: [
                {
                    value: 'chat',
                    iconSvg: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
                    label: '自由对话',
                    tip: '通用 AI 对话，适合日常问答与讨论'
                },
                {
                    value: 'query',
                    iconSvg: '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',
                    label: '数据查询',
                    tip: '结构化数据检索与分析，适合图斑查询、统计报表'
                },
                {
                    value: 'summary',
                    iconSvg:
                        '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
                    label: '智能摘要',
                    tip: '对当前选中要素自动生成综合摘要报告'
                }
            ],
            shortcuts: [
                { label: '唤起助手', keys: this._isMac() ? ['⌘', 'K'] : ['Ctrl', 'K'] },
                { label: '关闭面板', keys: ['Esc'] },
                { label: '发送消息', keys: ['Enter'] },
                { label: '消息中换行', keys: ['Shift', 'Enter'] }
            ],
            // 热力图
            heatmapDays: ['一', '二', '三', '四', '五', '六', '日'],
            heatmapHours: ['0h', '3h', '6h', '9h', '12h', '15h', '18h', '21h'],
            heatmapData: [], // 在 created 中生成
            _particleSeeds: [], // 粒子随机种子缓存
            // 打字机
            typedEyebrow: '',
            typedTitle: '',
            typedSubtitle: '',
            typingLine: '', // 'eyebrow' | 'title' | 'subtitle' | 'done'
            _typewriterCancelled: false,
            // Toast
            toastVisible: false,
            toastMessage: '设置已保存',
            _toastTimer: null,
            _saveTimer: null, // savePrefs 防抖定时器
            _storageError: false, // localStorage 读写异常标志
            _themeWasLight: false // 追踪主题切换，重启 WebGL
        };
    },

    computed: {
        ...mapState({ theme: (state) => state.theme }),
        isDark() {
            return this.theme !== 'light';
        },
        tempClass() {
            const t = this.temperature;
            if (t < 0.5) return 'temp-cool';
            if (t < 1.0) return 'temp-warm';
            if (t < 1.5) return 'temp-hot';
            return 'temp-blaze';
        },
        currentTemplates() {
            return this.promptTemplates[this.templateTab] || [];
        },
        placeholderForMode() {
            return {
                chat: ['例：带我去某个地点', '例：帮我打开某页面', '例：查询某类数据', '例：输入自定义提问', '例：输入自定义提问'],
                query: ['例：当前页面数据概览', '例：最近有哪些异常情况？', '例：按类型分类统计', '例：输入自定义提问', '例：输入自定义提问'],
                summary: ['例：有哪些高风险项？', '例：整体完成进度如何？', '例：下一步建议怎么做？', '例：输入自定义提问', '例：输入自定义提问']
            };
        }
    },

    created() {
        this.heatmapData = this._generateHeatmapData();
        // 预计算粒子随机种子
        this._particleSeeds = Array.from({ length: 8 }, () => ({
            x: Math.random() * 80 + 10,
            y: Math.random() * 80 + 10,
            size: Math.random() * 4 + 3,
            dur: Math.random() * 4 + 4,
            delay: Math.random() * 5
        }));
    },

    mounted() {
        this._themeWasLight = this.theme === 'light';
        this._startTypewriter();
        // 只有深色 + 非减少动效时才启 WebGL 极光
        if (!this._themeWasLight && !this.reduceMotion) this._initAuroraCanvas();
    },

    beforeDestroy() {
        this._typewriterCancelled = true;
        clearTimeout(this._toastTimer);
        clearTimeout(this._saveTimer);
        this._destroyAurora();
        this._destroyScrollReveal();
    },

    watch: {
        theme(val) {
            if (val === 'dark' && this._themeWasLight) {
                this._themeWasLight = false;
                if (!this.reduceMotion) this._initAuroraCanvas();
            }
            if (val === 'light') {
                this._themeWasLight = true;
                this._destroyAurora();
                // 清空 canvas 残留帧（浅色模式下无 WebGL）
                const canvas = this.$refs.auroraCanvas;
                if (canvas) {
                    const gl = canvas.getContext('webgl', { alpha: true });
                    if (gl) gl.clear(gl.COLOR_BUFFER_BIT);
                }
            }
        },
        model: { handler: 'savePrefs', deep: false },
        temperature: { handler: 'savePrefs', deep: false },
        maxTokens: { handler: 'savePrefs', deep: false },
        reduceMotion(v) {
            this.savePrefs();
            if (v) {
                this._destroyAurora();
            } else {
                this._initAuroraCanvas();
            }
        },
        defaultMode: { handler: 'savePrefs', deep: false },
        autoSummary: { handler: 'savePrefs', deep: false },
        promptTemplates: { handler: 'savePrefs', deep: true }
    },

    methods: {
        _isMac() {
            return /Mac|iPod|iPhone|iPad/.test(navigator.platform || '');
        },

        // ==================== 热力图 ====================

        _generateHeatmapData() {
            // 模拟 8 小时段 × 7 天的调用频率
            const rows = [];
            for (let h = 0; h < 8; h++) {
                const row = [];
                let base = h >= 2 && h <= 5 ? 8 : 3; // 9:00-18:00 繁忙
                for (let d = 0; d < 7; d++) {
                    // 周末略低 + 随机波动
                    const weekendPenalty = d >= 5 ? 0.5 : 1;
                    row.push(Math.round(Math.max(0, base + (Math.random() - 0.5) * 4) * weekendPenalty));
                }
                rows.push(row);
            }
            return rows;
        },

        heatmapLevel(val) {
            if (val === 0) return 'low';
            if (val <= 3) return 'low';
            if (val <= 7) return 'mid';
            if (val <= 10) return 'high';
            return 'peak';
        },

        // ==================== 漂浮粒子 ====================

        particleStyle(n) {
            const s = this._particleSeeds[n - 1] || { x: 50, y: 50, size: 3, dur: 5, delay: 0 };
            return {
                left: s.x + '%',
                top: s.y + '%',
                width: s.size + 'px',
                height: s.size + 'px',
                animationDuration: s.dur + 's',
                animationDelay: s.delay + 's'
            };
        },

        // ==================== 主题 ====================

        toggleTheme() {
            const next = this.theme === 'light' ? 'dark' : 'light';
            this.$store.commit('changeTheme', next);
        },

        // ==================== 打字机 + 幕布入场 ====================

        _startTypewriter() {
            // reduceMotion 关闭时跳过打字机，直接展示完整内容
            if (this.reduceMotion) {
                this.typedEyebrow = 'AI 助手';
                this.typedTitle = '设置';
                this.typedSubtitle = '个性化你的智能对话体验';
                this.typingLine = 'done';
                this.$nextTick(() => this._initScrollReveal());
                return;
            }
            const eyebrows = 'AI 助手';
            const title = '设置';
            const subtitle = '个性化你的智能对话体验';

            // 依次打字：眉题 → 标题 → 副标题
            this.typingLine = 'eyebrow';
            this._typeChars(eyebrows, 'typedEyebrow', 50, () => {
                this.typingLine = 'title';
                setTimeout(() => {
                    this._typeChars(title, 'typedTitle', 70, () => {
                        this.typingLine = 'subtitle';
                        setTimeout(() => {
                            this._typeChars(subtitle, 'typedSubtitle', 40, () => {
                                this.typingLine = 'done';
                                setTimeout(() => {
                                    this._initScrollReveal();
                                }, 200);
                            });
                        }, 200);
                    });
                }, 300);
            });
        },

        _typeChars(text, targetProp, delay, onDone) {
            let i = 0;
            const tick = () => {
                if (this._typewriterCancelled) return;
                if (i <= text.length) {
                    this[targetProp] = text.slice(0, i);
                    i++;
                    setTimeout(tick, delay);
                } else if (onDone) {
                    onDone();
                }
            };
            tick();
        },

        /* ===== 滚动触发布局入场 (IntersectionObserver, Hallmark 风格) ===== */
        _initScrollReveal() {
            this._destroyScrollReveal();

            const items = this.$el.querySelectorAll('.curtain-item');
            if (!items.length) return;

            // reduceMotion：直接全部展示
            if (this.reduceMotion) {
                items.forEach((el) => el.classList.add('curtain-revealed'));
                return;
            }

            this._revealObserver = new IntersectionObserver(
                (entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('curtain-revealed');
                            this._revealObserver.unobserve(entry.target);
                        }
                    });
                },
                {
                    threshold: 0.1,
                    rootMargin: '0px 0px -8% 0px'
                }
            );

            items.forEach((el) => this._revealObserver.observe(el));
        },

        _destroyScrollReveal() {
            if (this._revealObserver) {
                this._revealObserver.disconnect();
                this._revealObserver = null;
            }
        },

        // ==================== WebGL: Ether Shader 背景 ====================

        _initAuroraCanvas() {
            // 防止重复初始化（先销毁已有实例）
            this._destroyAurora();

            const canvas = this.$refs.auroraCanvas;
            if (!canvas) return;

            const gl = canvas.getContext('webgl', { alpha: true });
            if (!gl) {
                console.warn('WebGL not supported');
                return;
            }

            this._gl = gl;
            this._glProgram = null;
            this._glRaf = null;
            this._glUniforms = null;
            this._glStartTime = performance.now();
            this._glMouse = [0.5, 0.5];
            this._glCanvas = canvas;

            // 编译 shader program
            const prog = this._compileShaderProgram(gl, VERTEX_SHADER, ETHER_FRAGMENT_SHADER);
            if (!prog) return;
            this._glProgram = prog;

            this._glUniforms = {
                iResolution: gl.getUniformLocation(prog, 'iResolution'),
                iTime: gl.getUniformLocation(prog, 'iTime'),
                iMouse: gl.getUniformLocation(prog, 'iMouse')
            };

            // 鼠标追踪（mousemove 回调写入 ref，不触发 Vue 重渲染）
            this._onGlMouseMove = (e) => {
                const rect = canvas.getBoundingClientRect();
                this._glMouse = [
                    (e.clientX - rect.left) / rect.width,
                    1.0 - (e.clientY - rect.top) / rect.height // WebGL Y 轴反向
                ];
            };
            canvas.addEventListener('mousemove', this._onGlMouseMove);

            // resize
            this._onGlResize = () => this._resizeAurora();
            window.addEventListener('resize', this._onGlResize);

            this.$nextTick(() => {
                this._resizeAurora();
                this._tickAurora();
            });
        },

        _resizeAurora() {
            const canvas = this._glCanvas;
            if (!canvas) return;
            const rect = canvas.parentElement.getBoundingClientRect();
            const dpr = window.devicePixelRatio || 1;
            canvas.width = rect.width * dpr;
            canvas.height = rect.height * dpr;
            canvas.style.width = rect.width + 'px';
            canvas.style.height = rect.height + 'px';
            if (this._gl) {
                this._gl.viewport(0, 0, canvas.width, canvas.height);
            }
        },

        _tickAurora() {
            const gl = this._gl;
            const prog = this._glProgram;
            const canvas = this._glCanvas;
            const u = this._glUniforms;
            if (!gl || !prog || !u || !canvas) return;

            // 浅色模式不绘制 WebGL，停止 rAF 循环（主题 watcher 会在切回深色时重启）
            if (this.theme === 'light') {
                gl.clear(gl.COLOR_BUFFER_BIT);
                cancelAnimationFrame(this._glRaf);
                this._glRaf = null;
                return;
            }

            const t = (performance.now() - this._glStartTime) / 1000;

            gl.useProgram(prog);
            gl.uniform2f(u.iResolution, canvas.width, canvas.height);
            gl.uniform1f(u.iTime, t);
            gl.uniform2f(u.iMouse, this._glMouse[0], this._glMouse[1]);

            // 全屏 quad（顶点数据在 shader 编译时已绑定）
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

            this._glRaf = requestAnimationFrame(() => this._tickAurora());
        },

        _destroyAurora() {
            if (this._glRaf) cancelAnimationFrame(this._glRaf);
            if (this._glProgram && this._gl) this._gl.deleteProgram(this._glProgram);
            window.removeEventListener('resize', this._onGlResize);
            if (this._glCanvas) {
                this._glCanvas.removeEventListener('mousemove', this._onGlMouseMove);
            }
            this._glRaf = null;
            this._gl = null;
            this._glProgram = null;
            this._glCanvas = null;
            this._glUniforms = null;
        },

        _compileShaderProgram(gl, vsSource, fsSource) {
            const compile = (type, source) => {
                const shader = gl.createShader(type);
                gl.shaderSource(shader, source);
                gl.compileShader(shader);
                if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                    console.warn('Shader compile error:', gl.getShaderInfoLog(shader));
                    gl.deleteShader(shader);
                    return null;
                }
                return shader;
            };
            const vs = compile(gl.VERTEX_SHADER, vsSource);
            const fs = compile(gl.FRAGMENT_SHADER, fsSource);
            if (!vs || !fs) return null;

            const prog = gl.createProgram();
            gl.attachShader(prog, vs);
            gl.attachShader(prog, fs);
            gl.linkProgram(prog);
            if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
                console.warn('Program link error:', gl.getProgramInfoLog(prog));
                return null;
            }
            // 绑定全屏 quad 顶点（无需 VBO，用顶点 id 推导）
            gl.useProgram(prog);
            const posAttr = gl.getAttribLocation(prog, 'aVertexPosition');
            if (posAttr >= 0) {
                const buf = gl.createBuffer();
                gl.bindBuffer(gl.ARRAY_BUFFER, buf);
                gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
                gl.enableVertexAttribArray(posAttr);
                gl.vertexAttribPointer(posAttr, 2, gl.FLOAT, false, 0, 0);
            }
            return prog;
        },

        // ==================== 偏好持久化 ====================

        _prefKey() {
            return 'skyeye_ai_settings';
        },

        _loadPrefs() {
            try {
                const prefs = JSON.parse(localStorage.getItem(this._prefKey())) || {};
                this._storageError = false;
                return prefs;
            } catch (e) {
                console.warn('[aiSettings] localStorage 读取失败', e);
                this._storageError = true;
                return {};
            }
        },

        savePrefs() {
            clearTimeout(this._saveTimer);
            this._saveTimer = setTimeout(() => {
                const prefs = {
                    model: this.model,
                    temperature: this.temperature,
                    maxTokens: this.maxTokens,
                    reduceMotion: this.reduceMotion,
                    defaultMode: this.defaultMode,
                    autoSummary: this.autoSummary,
                    promptTemplates: this.promptTemplates
                };
                try {
                    localStorage.setItem(this._prefKey(), JSON.stringify(prefs));
                    this._storageError = false;
                } catch (e) {
                    console.warn('[aiSettings] localStorage 写入失败', e);
                    this._storageError = true;
                }
                this._showToast(this._storageError ? '写入存储失败，请检查浏览器空间' : '设置已保存');
            }, 300);
        },

        _showToast(msg) {
            clearTimeout(this._toastTimer);
            this.toastMessage = msg;
            this.toastVisible = true;
            this._toastTimer = setTimeout(() => {
                this.toastVisible = false;
            }, 1800);
        },

        restoreDefaults() {
            const DEFAULTS = {
                model: 'deepseek-chat',
                temperature: 0.7,
                maxTokens: 4096,
                reduceMotion: false,
                defaultMode: 'chat',
                autoSummary: false
            };
            this.model = DEFAULTS.model;
            this.temperature = DEFAULTS.temperature;
            this.maxTokens = DEFAULTS.maxTokens;
            this.reduceMotion = DEFAULTS.reduceMotion;
            this.defaultMode = DEFAULTS.defaultMode;
            this.autoSummary = DEFAULTS.autoSummary;
            this.promptTemplates = this._defaultTemplates();
            this.templateTab = 'chat';
            this.savePrefs();
            this._showToast('已恢复默认设置');
        },

        /** 重置侧栏引导计数：下次打开面板重新展示引导动画 */
        resetRailOnboard() {
            try { localStorage.setItem('skyeye_rail_onboard', '0'); } catch (_) {}
            this._showToast('下次打开 AI 助手时将重新展示侧栏引导');
        },

        // ==================== 提示词模板 ====================

        _defaultTemplates() {
            return {
                chat: ['带我去南京鼓楼区看看', '帮我打开航线规划页面', '当前有哪些检测任务？'],
                query: ['当前页面数据概览', '最近有哪些异常情况？', '按状态分类统计'],
                summary: ['有哪些高风险项？', '整体完成进度如何？', '下一步建议怎么做？']
            };
        },

        updateTemplate(idx, value) {
            const arr = [...this.promptTemplates[this.templateTab]];
            arr[idx] = value;
            this.$set(this.promptTemplates, this.templateTab, arr);
        },

        addTemplate() {
            const arr = [...this.promptTemplates[this.templateTab], ''];
            this.$set(this.promptTemplates, this.templateTab, arr);
        },

        removeTemplate(idx) {
            const arr = [...this.promptTemplates[this.templateTab]];
            arr.splice(idx, 1);
            this.$set(this.promptTemplates, this.templateTab, arr);
        }
    }
};

// ==================== GLSL Shaders (WebGL Ether 背景) ====================

// Vertex shader — 全屏 quad
const VERTEX_SHADER = `
attribute vec4 aVertexPosition;
void main() {
  gl_Position = aVertexPosition;
}
`;

// Fragment shader — Ether by nimitz (Shadertoy)
// 深色主题专用（浅色模式 WebGL 不渲染）
const ETHER_FRAGMENT_SHADER = `
precision mediump float;
uniform vec2 iResolution;
uniform float iTime;
uniform vec2 iMouse;

mat2 m(float a){float c=cos(a),s=sin(a);return mat2(c,-s,s,c);}
float map(vec3 p){
    p.xz*=m(iTime*0.4);p.xy*=m(iTime*0.3);
    vec3 q=p*2.+iTime;
    return length(p+vec3(sin(iTime*0.7)))*log(length(p)+1.)+sin(q.x+sin(q.z+sin(q.y)))*0.5-1.;
}

void main(){
    vec2 uv=(gl_FragCoord.xy/iResolution.xy)*2.-1.;
    uv.x*=iResolution.x/iResolution.y;

    vec3 cl=vec3(0.);
    float d=2.5;
    for(int i=0;i<=5;i++){
        vec3 p3d=vec3(0,0,5.)+normalize(vec3(uv,-1.))*d;
        float rz=map(p3d);
        float f=clamp((rz-map(p3d+.1))*0.5,-.1,1.);
        vec3 base=vec3(0.08,0.22,0.38)+vec3(4.0,2.0,5.5)*f;
        cl=cl*base+smoothstep(2.5,.0,rz)*.7*base;
        d+=min(rz,1.);
    }

    // 鼠标微光影响
    float mx=smoothstep(0.5,0.0,length(uv-iMouse*2.+1.));
    cl+=vec3(0.15,0.3,0.6)*mx*0.2;

    gl_FragColor=vec4(cl,1.0);
}
`;
</script>

<style lang="scss" scoped>
/* ========================= 背景 ========================= */
.settings-root {
    position: relative;
    height: 100%;
    background: #05070b;
    overflow-y: auto;
    overflow-x: hidden;
    transition: background 0.5s cubic-bezier(0.32, 0.72, 0, 1);

    /* 美化滚动条 — iOS 风格：默认隐藏，hover 显现 */
    &::-webkit-scrollbar {
        width: 5px;
    }
    &::-webkit-scrollbar-track {
        background: transparent;
    }
    &::-webkit-scrollbar-thumb {
        background: transparent;
        border-radius: 3px;
        transition: background 0.3s;
    }
    &:hover::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.15);
    }
}
/* ========================= 返回按钮 ========================= */
.back-btn {
    position: absolute;
    top: 28px;
    left: -56px;
    z-index: 10;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 14px;
    border: 1px solid var(--ai-border-default);
    background: var(--ai-glass-02);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    color: var(--ai-text-tertiary);
    cursor: pointer;
    transition: background 0.25s ease, border-color 0.25s ease, color 0.25s ease, transform 0.25s cubic-bezier(0.32, 0.72, 0, 1);

    &:hover {
        background: var(--ai-glass-04);
        border-color: var(--ai-border-active);
        color: var(--ai-text-primary);
        transform: translateX(-2px);
    }

    &:active {
        transform: scale(0.95);
    }

    &:focus-visible {
        outline: 2px solid rgba(99, 102, 241, 0.6);
        outline-offset: 2px;
    }

    .icon {
        display: block;
    }
}

[data-theme='light'] .back-btn {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-color: rgba(0, 0, 0, 0.08);
    color: rgba(0, 0, 0, 0.35);

    &:hover {
        background: rgba(255, 255, 255, 0.7);
        border-color: rgba(0, 0, 0, 0.15);
        color: rgba(0, 0, 0, 0.6);
    }
}

/* Canvas: 动态极光 + 粒子 */
.aurora-canvas {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
}

/* 亮色模式 · 氛围光 — 方案 A(页面温度) + C(右上自然光) 组合 */
.light-gradient-overlay {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.5s ease;
    background:
        /* C: 右上自然光源 — 淡蓝白扩散，模拟窗户侧光 */
        radial-gradient(
            ellipse 60% 40% at 75% 0%,
            rgba(147, 197, 253, 0.07) 0%,
            rgba(191, 219, 254, 0.03) 35%,
            transparent 65%
        ),
        /* A: 页面温度 — 顶部微暖，底部收束为冷灰 */
        linear-gradient(
            180deg,
            rgba(248, 250, 252, 0) 0%,
            rgba(241, 245, 249, 0.35) 50%,
            rgba(226, 232, 240, 0.15) 100%
        );
}

/* 仅亮色模式可见 */
[data-theme='light'] .light-gradient-overlay {
    opacity: 1;
}

/* ========================= 滚动词条装饰 (Ft8 Marquee) ========================= */
.marquee-strip {
    position: sticky;
    top: 0;
    z-index: 3;
    width: 100%;
    overflow: hidden;
    pointer-events: none;
    user-select: none;
    border-top: 2px solid;
    border-bottom: 2px solid;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    /* 两侧淡出，中央清晰 */
    mask-image: linear-gradient(
        90deg,
        transparent 0%,
        rgba(0, 0, 0, 0.3) 8%,
        rgba(0, 0, 0, 1) 20%,
        rgba(0, 0, 0, 1) 80%,
        rgba(0, 0, 0, 0.3) 92%,
        transparent 100%
    );
    -webkit-mask-image: linear-gradient(
        90deg,
        transparent 0%,
        rgba(0, 0, 0, 0.3) 8%,
        rgba(0, 0, 0, 1) 20%,
        rgba(0, 0, 0, 1) 80%,
        rgba(0, 0, 0, 0.3) 92%,
        transparent 100%
    );
}

.marquee-track {
    display: flex;
    gap: 2rem;
    width: max-content;
    padding: 14px 0;
    font-family: inherit;
    font-size: clamp(14px, 2.5vw, 20px);
    font-weight: 700;
    letter-spacing: 0.08em;
    white-space: nowrap;
    animation: marquee-scroll 32s linear infinite;
}

.marquee-dot {
    opacity: 0.3;
    text-shadow: none;
}

@keyframes marquee-scroll {
    from { transform: translateX(0); }
    to { transform: translateX(-50%); }
}

/* 减少动效：冻结滚动 */
.reduce-motion .marquee-track {
    animation: none;
}

/* 模式色联动 */
.marquee--chat {
    --mq-border: rgba(99, 102, 241, 0.18);
    --mq-bg-from: rgba(99, 102, 241, 0.06);
    --mq-bg-to: rgba(15, 23, 42, 0.5);
    --mq-text: rgba(165, 180, 252, 0.6);
    --mq-glow: rgba(99, 102, 241, 0.3);
    --mq-dot: rgba(99, 102, 241, 0.6);
}
.marquee--query {
    --mq-border: rgba(239, 68, 68, 0.18);
    --mq-bg-from: rgba(239, 68, 68, 0.06);
    --mq-bg-to: rgba(15, 23, 42, 0.5);
    --mq-text: rgba(252, 165, 165, 0.6);
    --mq-glow: rgba(239, 68, 68, 0.3);
    --mq-dot: rgba(239, 68, 68, 0.6);
}
.marquee--summary {
    --mq-border: rgba(245, 158, 11, 0.18);
    --mq-bg-from: rgba(245, 158, 11, 0.06);
    --mq-bg-to: rgba(15, 23, 42, 0.5);
    --mq-text: rgba(252, 211, 77, 0.6);
    --mq-glow: rgba(245, 158, 11, 0.3);
    --mq-dot: rgba(245, 158, 11, 0.6);
}

.marquee-strip {
    border-top-color: var(--mq-border);
    border-bottom-color: var(--mq-border);
    background: linear-gradient(180deg, var(--mq-bg-from) 0%, var(--mq-bg-to) 100%);
    transition: border-color 0.5s ease, background 0.5s ease;
}
.marquee-track {
    color: var(--mq-text);
    text-shadow: 0 0 16px var(--mq-glow);
    transition: color 0.5s ease, text-shadow 0.5s ease;
}
.marquee-dot {
    color: var(--mq-dot);
    transition: color 0.5s ease;
}

/* 亮色 — 模式色联动 */
[data-theme='light'] .marquee--chat {
    --mq-border: rgba(99, 102, 241, 0.1);
    --mq-bg-from: rgba(99, 102, 241, 0.04);
    --mq-bg-to: rgba(255, 255, 255, 0.4);
    --mq-text: rgba(37, 99, 235, 0.45);
    --mq-glow: rgba(37, 99, 235, 0.15);
    --mq-dot: rgba(37, 99, 235, 0.4);
}
[data-theme='light'] .marquee--query {
    --mq-border: rgba(239, 68, 68, 0.1);
    --mq-bg-from: rgba(239, 68, 68, 0.04);
    --mq-bg-to: rgba(255, 255, 255, 0.4);
    --mq-text: rgba(220, 38, 38, 0.45);
    --mq-glow: rgba(220, 38, 38, 0.15);
    --mq-dot: rgba(220, 38, 38, 0.4);
}
[data-theme='light'] .marquee--summary {
    --mq-border: rgba(245, 158, 11, 0.1);
    --mq-bg-from: rgba(245, 158, 11, 0.04);
    --mq-bg-to: rgba(255, 255, 255, 0.4);
    --mq-text: rgba(217, 119, 6, 0.45);
    --mq-glow: rgba(217, 119, 6, 0.15);
    --mq-dot: rgba(217, 119, 6, 0.4);
}

@media (prefers-reduced-motion: reduce) {
    .marquee-track {
        animation: none;
    }
}

/* ========================= 两侧氛围光斑 ========================= */
.ambient-orbs {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
}

.orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(100px);
    opacity: 0.12;
    transition: background 1.2s cubic-bezier(0.32, 0.72, 0, 1),
        opacity 1.2s cubic-bezier(0.32, 0.72, 0, 1);
}

.orb--tl {
    top: -8%;
    left: -5%;
    width: 320px;
    height: 320px;
    background: rgb(99, 102, 241);
    /* indigo */
}

.orb--tr {
    top: 12%;
    right: -3%;
    width: 260px;
    height: 260px;
    background: rgb(56, 189, 248);
    /* cyan */
    opacity: 0.09;
}

.orb--br {
    bottom: -10%;
    right: -6%;
    width: 380px;
    height: 380px;
    background: rgb(139, 92, 246);
    /* violet */
    opacity: 0.1;
}

.orb--ml {
    top: 55%;
    left: -4%;
    width: 220px;
    height: 220px;
    background: rgb(99, 102, 241);
    /* indigo */
    opacity: 0.08;
}

/* --- 红色通道 (数据查询) --- */
.orbs--query .orb--tl {
    background: rgb(239, 68, 68);
    /* red */
}

.orbs--query .orb--tr {
    background: rgb(251, 146, 60);
    /* orange */
}

.orbs--query .orb--br {
    background: rgb(239, 68, 68);
    /* red */
}

.orbs--query .orb--ml {
    background: rgb(239, 68, 68);
    /* red */
}

/* --- 琥珀通道 (智能摘要) --- */
.orbs--summary .orb--tl {
    background: rgb(245, 158, 11);
    /* amber */
}

.orbs--summary .orb--tr {
    background: rgb(250, 204, 21);
    /* yellow */
}

.orbs--summary .orb--br {
    background: rgb(245, 158, 11);
    /* amber */
}

.orbs--summary .orb--ml {
    background: rgb(245, 158, 11);
    /* amber */
}

/* 亮色主题适配 */
[data-theme='light'] .orb {
    opacity: 0.06;
}

[data-theme='light'] .orb--tr {
    opacity: 0.04;
}

[data-theme='light'] .orb--ml {
    opacity: 0.04;
}

/* 减动效时隐藏光斑 */
.reduce-motion .ambient-orbs {
    display: none;
}

/* ========================= 主容器 ========================= */
.settings-main {
    position: relative;
    z-index: 2;
    max-width: 880px;
    margin: 0 auto;
    padding: 72px 32px 96px;
}

/* ========================= 头部 ========================= */
.page-header {
    margin-bottom: 56px;

    .eyebrow {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.2);
        color: rgba(165, 180, 252, 0.9);
        font-size: 12px;
        font-weight: 500;
        letter-spacing: 0.04em;
        margin-bottom: 18px;
    }

    h1 {
        font-size: clamp(36px, 5vw, 54px);
        font-weight: 700;
        color: var(--ai-text-strong);
        margin: 0 0 12px;
        line-height: 1.1;
        letter-spacing: -0.025em;
    }

    .subtitle {
        color: var(--ai-text-secondary);
        font-size: 16px;
        margin: 0;
    }
}

/* ========================= 便当盒网格 ========================= */
.bento-grid {
    position: relative;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;

    .col-wide {
        grid-column: span 2;
    }
}

/* ========================= 操作行 ========================= */
.actions-bar {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-top: 28px;
}

.btn-reset {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 10px 20px;
    border-radius: 14px;
    border: 1px solid var(--ai-border-default);
    background: var(--ai-glass-02);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    color: var(--ai-text-tertiary);
    font-size: 13px;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.25s ease, border-color 0.25s ease, color 0.25s ease;

    &:hover {
        background: var(--ai-glass-04);
        border-color: var(--ai-border-active);
        color: rgba(255, 255, 255, 0.8);
    }

    &:active {
        background: var(--ai-glass-03);
    }

    &:focus-visible {
        outline: 2px solid rgba(99, 102, 241, 0.6);
        outline-offset: 2px;
    }
}

.btn-reset-icon {
    display: block;
}

/* ========================= Save Toast ========================= */
.save-toast {
    position: fixed;
    bottom: 32px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 50;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 22px;
    border-radius: 14px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(32px);
    -webkit-backdrop-filter: blur(32px);
    color: var(--ai-text-primary);
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.02em;
    pointer-events: none;
    white-space: nowrap;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 2px 8px rgba(0, 0, 0, 0.2);
}

.toast-icon {
    flex-shrink: 0;
    color: #34d399;
    filter: drop-shadow(0 0 6px rgba(52, 211, 153, 0.4));
}

.toast-icon--warn {
    color: #fbbf24;
    filter: drop-shadow(0 0 6px rgba(251, 191, 36, 0.4));
}

/* 错误状态 */
.save-toast--error {
    border-color: rgba(251, 191, 36, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(251, 191, 36, 0.15);
}

/* Toast transition — spring 弹入 */
.toast-enter-active {
    transition: opacity 0.3s cubic-bezier(0.25, 1.1, 0.4, 1), transform 0.35s cubic-bezier(0.25, 1.1, 0.4, 1);
}
.toast-leave-active {
    transition: opacity 0.25s ease, transform 0.25s cubic-bezier(0.32, 0.72, 0, 1);
}
.toast-enter,
.toast-leave-to {
    opacity: 0;
    transform: translateX(-50%) translateY(12px) scale(0.92);
}

/* ========================= 卡片 Pod — Liquid Glass ========================= */
.card-pod {
    position: relative;
    z-index: 1;
    /* 外壳 — 半透明玻璃托盘 */
    .pod-shell {
        padding: 4px;
        border-radius: 24px;
        background: var(--ai-glass-02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06), 0 4px 24px rgba(0, 0, 0, 0.3);
        transition: transform 0.4s cubic-bezier(0.32, 0.72, 0, 1), box-shadow 0.4s cubic-bezier(0.32, 0.72, 0, 1);

        &:hover {
            border-color: var(--ai-border-hover);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 12px 40px rgba(0, 0, 0, 0.45);
        }
    }

    /* 内核 — 深层玻璃面板 */
    .pod-core {
        position: relative;
        padding: 28px 28px 32px;
        border-radius: 21px;
        background: var(--ai-glass-01);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(40px);
        -webkit-backdrop-filter: blur(40px);
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.06);
        /* overflow: visible — 确保 field-help tooltip 不被裁剪 */

        /* 双层玻璃深度：伪元素叠加高光渐变 */
        &::before {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: 21px;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }

        > * {
            position: relative;
            z-index: 1;
        }
    }

    .pod-icon-wrap {
        width: 44px;
        height: 44px;
        border-radius: 14px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.2);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 16px;

        .pod-icon {
            display: block;
            color: rgba(165, 180, 252, 0.9);
        }
    }

    h3 {
        font-size: 17px;
        font-weight: 650;
        color: rgba(255, 255, 255, 0.9);
        margin: 0 0 4px;
    }

    .pod-desc {
        font-size: 13px;
        color: var(--ai-text-secondary);
        margin: 0 0 24px;
        line-height: 1.5;
    }
}

/* ========================= 表单项 ========================= */
.field-group {
    margin-bottom: 22px;

    &:last-child {
        margin-bottom: 0;
    }
}

.field-label {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 12px;
    font-weight: 600;
    color: var(--ai-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
}

/* 帮助提示 ? 徽标 */
.field-help {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--ai-glass-03);
    border: 1px solid var(--ai-border-default);
    color: var(--ai-text-tertiary);
    font-size: 10px;
    font-weight: 600;
    font-family: inherit;
    line-height: 1;
    cursor: help;
    text-transform: none;
    letter-spacing: 0;
    transition: background 0.25s ease, border-color 0.25s ease, color 0.25s ease;

    &:hover {
        background: rgba(99, 102, 241, 0.2);
        border-color: rgba(99, 102, 241, 0.35);
        color: rgba(165, 180, 252, 0.9);
    }

    /* 自定义 tooltip 气泡 */
    &::after {
        content: attr(data-tip);
        position: absolute;
        bottom: calc(100% + 8px);
        left: 50%;
        right: auto;
        transform: translateX(-50%);
        padding: 10px 14px;
        border-radius: 8px;
        background: rgba(15, 23, 42, 0.92);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(99, 102, 241, 0.18);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.40), 0 1px 0 rgba(255, 255, 255, 0.04) inset;
        color: rgba(220, 225, 240, 0.92);
        font-size: 12px;
        font-weight: 400;
        line-height: 1.55;
        white-space: normal;
        width: 260px;
        max-width: min(260px, calc(100vw - 32px));
        text-align: left;
        letter-spacing: 0;
        text-transform: none;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.12s ease, transform 0.12s cubic-bezier(0.32, 0.72, 0, 1);
        z-index: 100;
    }

    /* 右侧问号：tooltip 右对齐防止出界 */
    &.right &::after {
        left: auto;
        right: 0;
        transform: translateY(0);
    }

    /* 气泡三角箭头 —— 简化版 */
    &::before {
        content: '';
        position: absolute;
        left: 50%;
        bottom: calc(100% + 2px);
        transform: translateX(-50%);
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid rgba(15, 23, 42, 0.88);
        opacity: 0;
        transition: opacity 0.12s ease, transform 0.12s cubic-bezier(0.32, 0.72, 0, 1);
        z-index: 100;
        pointer-events: none;
    }

    &:hover::after,
    &:hover::before {
        opacity: 1;
        transform: translateX(-50%) translateY(-2px);
    }
    &.right:hover::after {
        transform: translateY(-2px);
    }
}

/* 亮色模式 — tooltip */
.theme-light .field-help {
    background: rgba(0, 0, 0, 0.05);
    border-color: rgba(0, 0, 0, 0.10);
    color: rgba(0, 0, 0, 0.30);

    &:hover {
        background: rgba(99, 102, 241, 0.12);
        border-color: rgba(99, 102, 241, 0.25);
        color: rgba(37, 99, 235, 0.7);
    }

    &::after {
        background: rgba(255, 255, 255, 0.90);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border-color: rgba(0, 0, 0, 0.10);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12), 0 1px 0 rgba(255, 255, 255, 0.5) inset;
        color: #334155;
    }

    &::before {
        border-top-color: rgba(255, 255, 255, 0.85);
    }
}

.field-label-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    .field-label {
        margin-bottom: 0;
    }

    .field-val {
        font-size: 13px;
        font-weight: 650;
        color: rgba(165, 180, 252, 0.9);
        font-variant-numeric: tabular-nums;
    }
}

/* ---- 下拉选择 ---- */
.select-wrap {
    position: relative;

    .field-select {
        width: 100%;
        padding: 11px 36px 11px 14px;
        border-radius: 14px;
        background: var(--ai-glass-02);
        border: 1px solid var(--ai-border-default);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        color: var(--ai-text-primary);
        font-size: 14px;
        font-family: inherit;
        appearance: none;
        cursor: pointer;
        outline: none;
        transition: border-color 0.35s cubic-bezier(0.32, 0.72, 0, 1), background 0.35s cubic-bezier(0.32, 0.72, 0, 1),
            box-shadow 0.35s cubic-bezier(0.32, 0.72, 0, 1);

        &:focus {
            border-color: rgba(99, 102, 241, 0.45);
            background: rgba(255, 255, 255, 0.1);
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        }
    }

    .select-chevron {
        position: absolute;
        right: 14px;
        top: 50%;
        transform: translateY(-50%);
        color: var(--ai-text-placeholder);
        pointer-events: none;
        transition: transform 0.35s cubic-bezier(0.32, 0.72, 0, 1), color 0.35s cubic-bezier(0.32, 0.72, 0, 1);
    }

    &:focus-within .select-chevron {
        transform: translateY(-50%) rotate(180deg);
        color: rgba(165, 180, 252, 0.7);
    }
}

/* ---- 滑块 ---- */
.field-slider {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 6px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.1);
    outline: none;
    margin: 0 0 4px;
    cursor: pointer;

    &::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: #fff;
        border: 2px solid rgba(99, 102, 241, 0.5);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3), 0 0 12px rgba(99, 102, 241, 0.25);
        cursor: pointer;
        transition: transform 0.25s cubic-bezier(0.32, 0.72, 0, 1), box-shadow 0.25s cubic-bezier(0.32, 0.72, 0, 1);
    }

    &::-webkit-slider-thumb:hover {
        transform: scale(1.15);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4), 0 0 20px rgba(99, 102, 241, 0.4);
    }

    &::-webkit-slider-thumb:active {
        transform: scale(0.95);
        cursor: grabbing;
    }

    &::-moz-range-thumb {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: #fff;
        border: 2px solid rgba(99, 102, 241, 0.5);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        cursor: pointer;
    }
}

.slider-hints {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: var(--ai-text-tertiary);
    padding-top: 2px;
}

/* ---- 切换开关 ---- */
.toggle-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    padding: 6px 0;
    user-select: none;
}

.toggle-label {
    margin-bottom: 1px !important;
}

.toggle-hint {
    font-size: 11px;
    color: var(--ai-text-tertiary);
}

.toggle-switch {
    position: relative;
    width: 48px;
    height: 28px;
    border-radius: 28px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: var(--ai-glass-03);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    cursor: pointer;
    outline: none;
    flex-shrink: 0;

    &:focus-visible {
        outline: 2px solid rgba(99, 102, 241, 0.6);
        outline-offset: 2px;
    }

    transition: background 0.45s cubic-bezier(0.32, 0.72, 0, 1), border-color 0.45s cubic-bezier(0.32, 0.72, 0, 1),
        box-shadow 0.45s cubic-bezier(0.32, 0.72, 0, 1);

    &.active {
        background: rgba(99, 102, 241, 0.4);
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    .toggle-knob {
        position: absolute;
        top: 3px;
        left: 3px;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: #fff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.25);
        transition: transform 0.4s cubic-bezier(0.32, 0.72, 0, 1);
    }

    &.active .toggle-knob {
        transform: translateX(20px);
    }

    &:active .toggle-knob {
        width: 24px;
    }
}

/* ---- 模式芯片 ---- */
.mode-chips {
    display: flex;
    gap: 8px;
}

.mode-chip {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 12px 8px;
    border-radius: 16px;
    border: 1px solid var(--ai-border-default);
    background: var(--ai-glass-01);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: var(--ai-text-tertiary);
    cursor: pointer;
    outline: none;
    font-family: inherit;
    position: relative;
    isolation: isolate;
    overflow: hidden;

    &:focus-visible {
        outline: 2px solid rgba(99, 102, 241, 0.6);
        outline-offset: 2px;
    }

    transition: border-color 0.3s ease, color 0.3s ease, transform 0.14s cubic-bezier(0.2, 0.7, 0.3, 1);

    /* 水面自下而上灌满 */
    &::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 16px;
        background: var(--chip-fill, rgba(99, 102, 241, 0.35));
        clip-path: inset(100% 0 0 0);
        transition: clip-path 0.3s cubic-bezier(0.2, 0.7, 0.3, 1);
        z-index: -1;
        pointer-events: none;
    }

    .chip-icon {
        display: block;
        transition: transform 0.3s cubic-bezier(0.2, 0.7, 0.3, 1);
    }

    .chip-label {
        font-size: 12px;
        font-weight: 550;
    }

    @media (hover: hover) {
        &:hover {
            border-color: var(--ai-border-active);
            color: rgba(255, 255, 255, 0.85);

            .chip-icon {
                transform: scale(1.15);
            }
        }

        &:hover::before {
            clip-path: inset(0 0 0 0);
        }
    }

    &.active {
        border-color: rgba(99, 102, 241, 0.5);
        background: rgba(99, 102, 241, 0.15);
        color: #fff;
        box-shadow: 0 0 24px rgba(99, 102, 241, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.08);

        .chip-icon {
            transform: scale(1.1);
        }
    }

    &:active {
        transform: scale(0.97);
    }

    &:active::before {
        clip-path: inset(0 0 0 0);
        transition-duration: 0.1s;
    }
}

/* 模式色水位 */
.mode-chip[data-mode='chat']    { --chip-fill: rgba(99, 102, 241, 0.35); }
.mode-chip[data-mode='query']   { --chip-fill: rgba(239, 68, 68, 0.35); }
.mode-chip[data-mode='summary'] { --chip-fill: rgba(245, 158, 11, 0.35); }

.pod-shell:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 44px rgba(0, 0, 0, 0.5);
}

/* ---- 快捷键列表 ---- */
.kbd-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.kbd-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.kbd-label {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.7);
}

.kbd-keys {
    display: flex;
    gap: 4px;
    align-items: center;

    kbd {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 26px;
        height: 26px;
        padding: 0 8px;
        border-radius: 7px;
        background: var(--ai-glass-03);
        border: 1px solid rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06), 0 2px 0 rgba(0, 0, 0, 0.3);
        color: var(--ai-text-secondary);
        font-size: 11px;
        font-weight: 600;
        font-family: inherit;
    }
}

/* ---- 关于元信息 ---- */
.about-meta {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.meta-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 14px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--ai-border-subtle);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    transition: border-color 0.4s cubic-bezier(0.32, 0.72, 0, 1), background 0.4s cubic-bezier(0.32, 0.72, 0, 1);

    &:hover {
        border-color: var(--ai-border-hover);
        background: var(--ai-glass-02);
    }

    .meta-key {
        font-size: 13px;
        color: var(--ai-text-tertiary);
    }

    .meta-val {
        font-size: 13px;
        font-weight: 550;
        color: rgba(255, 255, 255, 0.7);
    }
}

/* ========================= 打字机光标 ========================= */
.typing-cursor {
    display: inline-block;
    color: rgba(99, 102, 241, 0.7);
    font-weight: 300;
    animation: cursor-blink 0.8s step-end infinite;
    margin-left: 2px;
}

@keyframes cursor-blink {
    0%,
    100% {
        opacity: 1;
    }
    50% {
        opacity: 0;
    }
}

/* ========================= 垂直幕布入场 (iOS 26 style) ========================= */
.curtain-item {
    opacity: 0;
    transform: scale(0.97);
    filter: blur(8px);
    transition: opacity 0.5s cubic-bezier(0.32, 0.72, 0, 1), transform 0.5s cubic-bezier(0.32, 0.72, 0, 1), filter 0.5s cubic-bezier(0.32, 0.72, 0, 1);

    &.curtain-revealed {
        opacity: 1;
        transform: translate(0, 0) scale(1) !important;
        filter: blur(0);
    }
}

/* 方向偏移量（更克制） */
.curtain-top {
    transform: translateY(-20px) scale(0.97);
}
.curtain-left {
    transform: translateX(-40px) scale(0.97);
}
.curtain-right {
    transform: translateX(40px) scale(0.97);
}
.curtain-bottom {
    transform: translateY(30px) scale(0.97);
}

/* 交错过场延迟 */
.bento-grid .curtain-item:nth-child(1) {
    transition-delay: 0s;
}
.bento-grid .curtain-item:nth-child(2) {
    transition-delay: 0.08s;
}
.bento-grid .curtain-item:nth-child(3) {
    transition-delay: 0.14s;
}
.bento-grid .curtain-item:nth-child(4) {
    transition-delay: 0.2s;
}
.bento-grid .curtain-item:nth-child(5) {
    transition-delay: 0.26s;
}
.bento-grid .curtain-item:nth-child(6) {
    transition-delay: 0.32s;
}
.bento-grid .curtain-item:nth-child(7) {
    transition-delay: 0.38s;
}

/* ========================= 亮色主题覆盖 ========================= */
[data-theme='light'] .settings-root {
    background: #f4f5f9;
    transition: background 0.5s cubic-bezier(0.32, 0.72, 0, 1);

    &::-webkit-scrollbar-thumb {
        background: transparent;
    }
    &:hover::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.12);
    }
}

[data-theme='light'] .typing-cursor {
    color: rgba(99, 102, 241, 0.6);
}

[data-theme='light'] .field-help {
    background: rgba(99, 102, 241, 0.06);
    border-color: rgba(99, 102, 241, 0.12);
    color: rgba(99, 102, 241, 0.35);

    &:hover {
        background: rgba(99, 102, 241, 0.15);
        border-color: rgba(99, 102, 241, 0.3);
        color: rgba(99, 102, 241, 0.75);
    }

    &::after {
        background: rgba(255, 255, 255, 0.96);
        border-color: rgba(99, 102, 241, 0.2);
        color: #1e293b;
    }

    &::before {
        border-top-color: rgba(255, 255, 255, 0.96);
    }
}

[data-theme='light'] .page-header {
    h1 {
        color: #0f172a;
    }
    .subtitle {
        color: #64748b;
    }
    .eyebrow {
        background: rgba(99, 102, 241, 0.1);
        border-color: rgba(99, 102, 241, 0.15);
        color: #4f46e5;
    }
}

[data-theme='light'] .card-pod {
    .pod-shell {
        background: rgba(0, 0, 0, 0.03);
        border-color: rgba(0, 0, 0, 0.06);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5), 0 4px 20px rgba(0, 0, 0, 0.06);
    }

    &:hover .pod-shell {
        border-color: rgba(0, 0, 0, 0.1);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6), 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    .pod-core {
        background: rgba(255, 255, 255, 0.45);
        border-color: rgba(0, 0, 0, 0.06);
        backdrop-filter: blur(40px);
        -webkit-backdrop-filter: blur(40px);
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.7);

        &::before {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, transparent 50%);
        }
    }

    h3 {
        color: #1e293b;
    }
    .pod-desc {
        color: #94a3b8;
    }
    .pod-icon-wrap {
        background: rgba(99, 102, 241, 0.08);
        border-color: rgba(99, 102, 241, 0.12);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);

        .pod-icon {
            color: rgba(99, 102, 241, 0.7);
        }
    }
}

[data-theme='light'] .field-label {
    color: #64748b;
}
[data-theme='light'] .field-val {
    color: #4f46e5;
}

[data-theme='light'] .field-slider {
    background: rgba(0, 0, 0, 0.08);
    &::-webkit-slider-thumb {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
}

[data-theme='light'] .select-wrap .field-select {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-color: rgba(0, 0, 0, 0.1);
    color: #334155;
    &:focus {
        border-color: rgba(99, 102, 241, 0.4);
        background: rgba(255, 255, 255, 0.7);
    }
}

[data-theme='light'] .select-chevron {
    color: #94a3b8;
}

[data-theme='light'] .toggle-switch {
    background: rgba(0, 0, 0, 0.08);
    border-color: rgba(0, 0, 0, 0.12);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);

    &.active {
        background: rgba(99, 102, 241, 0.55);
        border-color: rgba(99, 102, 241, 0.6);
        box-shadow: 0 0 16px rgba(99, 102, 241, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }
}

[data-theme='light'] .mode-chip {
    background: rgba(0, 0, 0, 0.03);
    border-color: rgba(0, 0, 0, 0.08);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: #64748b;
    &:hover {
        background: rgba(0, 0, 0, 0.06);
        color: #334155;
    }
    &.active {
        color: #1e293b;
    }
}

[data-theme='light'] .mode-chip[data-mode='chat']    { --chip-fill: rgba(99, 102, 241, 0.25); }
[data-theme='light'] .mode-chip[data-mode='query']   { --chip-fill: rgba(239, 68, 68, 0.25); }
[data-theme='light'] .mode-chip[data-mode='summary'] { --chip-fill: rgba(245, 158, 11, 0.25); }

[data-theme='light'] .kbd-row kbd {
    background: rgba(0, 0, 0, 0.04);
    border-color: rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8), 0 1px 0 rgba(0, 0, 0, 0.08);
    color: #475569;
}

[data-theme='light'] .kbd-label {
    color: #475569;
}
[data-theme='light'] .toggle-hint {
    color: #94a3b8;
}
[data-theme='light'] .slider-hints {
    color: rgba(0, 0, 0, 0.2);
}

[data-theme='light'] .meta-row {
    background: rgba(0, 0, 0, 0.02);
    border-color: rgba(0, 0, 0, 0.05);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    .meta-key {
        color: #94a3b8;
    }
    .meta-val {
        color: #475569;
    }
}

[data-theme='light'] .btn-reset {
    background: rgba(0, 0, 0, 0.03);
    border-color: rgba(0, 0, 0, 0.08);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    color: rgba(0, 0, 0, 0.3);

    &:hover {
        background: rgba(0, 0, 0, 0.06);
        border-color: rgba(0, 0, 0, 0.14);
        color: rgba(0, 0, 0, 0.55);
    }
}

/* ========================= Token 预览条 ========================= */
.token-preview-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 10px;
}

.token-label {
    font-size: 10px;
    color: var(--ai-text-placeholder);
    white-space: nowrap;
}

.token-track {
    flex: 1;
    height: 4px;
    border-radius: 4px;
    background: var(--ai-glass-03);
    overflow: hidden;
}

.token-fill {
    display: block;
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, rgba(99, 102, 241, 0.5), rgba(129, 140, 248, 0.7));
    transition: width 0.4s cubic-bezier(0.32, 0.72, 0, 1);
}

[data-theme='light'] .token-label {
    color: rgba(0, 0, 0, 0.25);
}

[data-theme='light'] .token-track {
    background: rgba(0, 0, 0, 0.06);
}

/* ========================= Temperature 颜色 ========================= */
.temp-cool {
    color: #60a5fa !important;
}
.temp-warm {
    color: #facc15 !important;
}
.temp-hot {
    color: #f97316 !important;
}
.temp-blaze {
    color: #ef4444 !important;
}

[data-theme='light'] .temp-cool {
    color: #3b82f6 !important;
}
[data-theme='light'] .temp-warm {
    color: #eab308 !important;
}
[data-theme='light'] .temp-hot {
    color: #ea580c !important;
}
[data-theme='light'] .temp-blaze {
    color: #dc2626 !important;
}

/* ========================= 响应式 ========================= */
@media (max-width: 768px) {
    .settings-main {
        padding: 40px 16px 64px;
    }

    .back-btn {
        top: 12px;
        left: 8px;
    }

    .bento-grid {
        grid-template-columns: 1fr;
        gap: 14px;

        .col-wide {
            grid-column: span 1;
        }
    }

    .pod-core {
        padding: 20px 18px 24px;
    }
}

/* ========================= localStorage 异常警告 ========================= */
.storage-warning {
    margin: 16px auto 0;
    max-width: 520px;
    padding: 10px 16px;
    border-radius: var(--radius-md, 12px);
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.2);
    color: rgba(252, 165, 165, 0.9);
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    justify-content: center;
}

[data-theme='light'] .storage-warning {
    background: rgba(239, 68, 68, 0.06);
    border-color: rgba(239, 68, 68, 0.25);
    color: #b91c1c;
}

/* ========================= prefers-reduced-motion ========================= */
@media (prefers-reduced-motion: reduce) {
    .settings-root * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* ======================== 提示词模板卡片 ======================== */

.template-mode-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
}

.template-mode-tab {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: var(--radius-lg, 12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: var(--ai-glass-01);
    color: var(--ai-text-secondary);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: border-color 0.25s ease, color 0.25s ease, transform 0.14s cubic-bezier(0.2, 0.7, 0.3, 1);
    outline-offset: 2px;
    position: relative;
    isolation: isolate;
    overflow: hidden;

    /* 水面自下而上灌满 */
    &::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: var(--radius-lg, 12px);
        background: var(--chip-fill, rgba(99, 102, 241, 0.35));
        clip-path: inset(100% 0 0 0);
        transition: clip-path 0.3s cubic-bezier(0.2, 0.7, 0.3, 1);
        z-index: -1;
        pointer-events: none;
    }

    .tab-icon {
        flex-shrink: 0;
        opacity: 0.7;
        transition: opacity 0.25s ease;
    }

    @media (hover: hover) {
        &:hover {
            color: rgba(255, 255, 255, 0.8);

            .tab-icon {
                opacity: 1;
            }
        }

        &:hover::before {
            clip-path: inset(0 0 0 0);
        }
    }

    &.active {
        background: rgba(99, 102, 241, 0.15);
        border-color: rgba(99, 102, 241, 0.35);
        color: rgba(165, 180, 252, 0.95);

        .tab-icon {
            opacity: 1;
        }
    }

    &:active {
        transform: scale(0.97);
    }

    &:active::before {
        clip-path: inset(0 0 0 0);
        transition-duration: 0.1s;
    }

    &:focus-visible {
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.5);
    }
}

/* 提示词标签水位色 */
.template-mode-tab[data-mode='chat']    { --chip-fill: rgba(99, 102, 241, 0.35); }
.template-mode-tab[data-mode='query']   { --chip-fill: rgba(239, 68, 68, 0.35); }
.template-mode-tab[data-mode='summary'] { --chip-fill: rgba(245, 158, 11, 0.35); }

/* 亮色主题 */
.theme-light .template-mode-tab {
    border-color: rgba(0, 0, 0, 0.08);
    background: rgba(0, 0, 0, 0.02);
    color: rgba(0, 0, 0, 0.45);

    @media (hover: hover) {
        &:hover {
            color: rgba(0, 0, 0, 0.7);
        }
    }

    &.active {
        background: rgba(37, 99, 235, 0.08);
        border-color: rgba(37, 99, 235, 0.3);
        color: #2563eb;
    }
}

.theme-light .template-mode-tab[data-mode='chat']    { --chip-fill: rgba(99, 102, 241, 0.25); }
.theme-light .template-mode-tab[data-mode='query']   { --chip-fill: rgba(239, 68, 68, 0.25); }
.theme-light .template-mode-tab[data-mode='summary'] { --chip-fill: rgba(245, 158, 11, 0.25); }

/* 模板列表 */
.template-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.template-row {
    display: flex;
    align-items: center;
    gap: 10px;
    animation: templateFadeIn 0.3s ease both;
}

@keyframes templateFadeIn {
    from {
        opacity: 0;
        transform: translateY(-4px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.template-row:nth-child(1) {
    animation-delay: 0s;
}
.template-row:nth-child(2) {
    animation-delay: 0.04s;
}
.template-row:nth-child(3) {
    animation-delay: 0.08s;
}
.template-row:nth-child(4) {
    animation-delay: 0.12s;
}
.template-row:nth-child(5) {
    animation-delay: 0.16s;
}

.template-num {
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    border-radius: 6px;
    background: rgba(99, 102, 241, 0.12);
    color: rgba(165, 180, 252, 0.8);
    font-size: 11px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
}

.theme-light .template-num {
    background: rgba(37, 99, 235, 0.08);
    color: #2563eb;
}

.template-input {
    flex: 1;
    padding: 10px 14px;
    border-radius: var(--radius-md, 10px);
    border: 1px solid var(--ai-border-default);
    background: var(--ai-glass-01);
    color: #e0e6f0;
    font-size: 13px;
    font-family: inherit;
    outline: none;
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
}

.template-input::placeholder {
    color: var(--ai-text-placeholder);
    font-style: italic;
}

.template-input:focus {
    border-color: rgba(99, 102, 241, 0.45);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.theme-light .template-input {
    border-color: rgba(0, 0, 0, 0.1);
    background: rgba(0, 0, 0, 0.02);
    color: #1a1a2e;
}

.theme-light .template-input::placeholder {
    color: rgba(0, 0, 0, 0.25);
}

.theme-light .template-input:focus {
    border-color: rgba(37, 99, 235, 0.4);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08);
}

.template-del-btn {
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 1px solid transparent;
    background: transparent;
    color: var(--ai-text-placeholder);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.template-del-btn:hover {
    background: rgba(239, 68, 68, 0.12);
    border-color: rgba(239, 68, 68, 0.25);
    color: #f87171;
}

.theme-light .template-del-btn {
    color: rgba(0, 0, 0, 0.25);
}

.theme-light .template-del-btn:hover {
    background: rgba(239, 68, 68, 0.08);
    color: #dc2626;
}

.template-add-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    width: 100%;
    padding: 10px 0;
    border-radius: var(--radius-md, 10px);
    border: 1px dashed rgba(99, 102, 241, 0.2);
    background: transparent;
    color: rgba(165, 180, 252, 0.5);
    font-size: 13px;
    cursor: pointer;
    transition: all 0.25s ease;
    margin-top: 4px;
}

.template-add-btn:hover {
    border-color: rgba(99, 102, 241, 0.4);
    background: rgba(99, 102, 241, 0.06);
    color: rgba(165, 180, 252, 0.8);
}

.theme-light .template-add-btn {
    border-color: rgba(37, 99, 235, 0.15);
    color: rgba(37, 99, 235, 0.4);
}

.theme-light .template-add-btn:hover {
    border-color: rgba(37, 99, 235, 0.35);
    background: rgba(37, 99, 235, 0.04);
    color: #2563eb;
}

.template-limit-hint {
    text-align: center;
    color: var(--ai-text-placeholder);
    font-size: 12px;
    margin-top: 4px;
}

.theme-light .template-limit-hint {
    color: rgba(0, 0, 0, 0.2);
}

/* ========================= Template 切换过渡 ========================= */
.template-fade-enter-active {
    transition: opacity 0.25s cubic-bezier(0.25, 1.1, 0.4, 1), transform 0.3s cubic-bezier(0.25, 1.1, 0.4, 1), filter 0.25s ease;
}
.template-fade-leave-active {
    transition: opacity 0.15s ease, transform 0.2s ease, filter 0.15s ease;
}
.template-fade-enter {
    opacity: 0;
    transform: translateY(6px) scale(0.97);
    filter: blur(4px);
}
.template-fade-leave-to {
    opacity: 0;
    transform: translateY(-6px) scale(0.97);
    filter: blur(4px);
}

/* ========================= API 调用频率热力图 ========================= */
.pod-icon-wrap--amber {
    background: rgba(251, 191, 36, 0.15);
    color: #fbbf24;
}

.heatmap-grid {
    margin-top: 12px;
}

.heatmap-header {
    display: flex;
    gap: 2px;
    margin-left: 32px; /* align with cells after hour label */
    margin-bottom: 2px;
}

.heatmap-day-label {
    flex: 1;
    text-align: center;
    font-size: 10px;
    font-weight: 600;
    color: var(--ai-text-placeholder);
    text-transform: uppercase;
}

.heatmap-body {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.heatmap-row {
    display: flex;
    align-items: center;
    gap: 2px;
}

.heatmap-hour-label {
    width: 28px;
    font-size: 10px;
    font-weight: 500;
    color: var(--ai-text-placeholder);
    text-align: right;
    flex-shrink: 0;
}

.heatmap-cell {
    flex: 1;
    aspect-ratio: 1;
    border-radius: 3px;
    transition: transform 0.15s ease;
    cursor: default;
}

.heatmap-cell:hover {
    transform: scale(1.3);
    z-index: 1;
}

/* 强度色阶 — 从几乎透明到琥珀色 */
.heatmap-cell--low { background: rgba(251, 191, 36, 0.08); }
.heatmap-cell--mid { background: rgba(251, 191, 36, 0.28); }
.heatmap-cell--high { background: rgba(251, 191, 36, 0.55); }
.heatmap-cell--peak { background: rgba(251, 191, 36, 0.85); box-shadow: 0 0 4px rgba(251, 191, 36, 0.3); }

.heatmap-legend {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 8px;
    justify-content: flex-end;
}

.heatmap-legend-label {
    font-size: 10px;
    color: var(--ai-text-placeholder);
}

.heatmap-legend-dot {
    width: 10px;
    height: 10px;
    border-radius: 2px;
}

/* ========================= 空白区域漂浮粒子 ========================= */
.bento-particles {
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.bento-particle {
    position: absolute;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.3), transparent);
    animation: particle-drift ease-in-out infinite alternate;
    opacity: 0;
}

@keyframes particle-drift {
    0% { opacity: 0; transform: translate(0, 0); }
    30% { opacity: 0.25; }
    70% { opacity: 0.2; }
    100% { opacity: 0; transform: translate(var(--particle-drift-x, 8px), var(--particle-drift-y, -6px)); }
}

/* 每个粒子不同的漂移方向 */
.bento-particle:nth-child(1) { --particle-drift-x: 10px; --particle-drift-y: -8px; }
.bento-particle:nth-child(2) { --particle-drift-x: -6px; --particle-drift-y: -12px; }
.bento-particle:nth-child(3) { --particle-drift-x: 15px; --particle-drift-y: 5px; }
.bento-particle:nth-child(4) { --particle-drift-x: -10px; --particle-drift-y: 10px; }
.bento-particle:nth-child(5) { --particle-drift-x: 8px; --particle-drift-y: 14px; }
.bento-particle:nth-child(6) { --particle-drift-x: -14px; --particle-drift-y: -4px; }
.bento-particle:nth-child(7) { --particle-drift-x: 4px; --particle-drift-y: -16px; }
.bento-particle:nth-child(8) { --particle-drift-x: -8px; --particle-drift-y: 8px; }

/* 减少动效：冻结粒子 */
.reduce-motion .bento-particle {
    animation: none;
    opacity: 0;
}

/* ========================= 亮色主题 Toast ========================= */
[data-theme='light'] .save-toast {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(0, 0, 0, 0.1);
    color: rgba(0, 0, 0, 0.85);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.05);
}

[data-theme='light'] .toast-icon {
    color: #059669;
    filter: none;
}

[data-theme='light'] .toast-icon--warn {
    color: #d97706;
    filter: none;
}

[data-theme='light'] .save-toast--error {
    border-color: rgba(217, 119, 6, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(217, 119, 6, 0.2);
}
</style>
