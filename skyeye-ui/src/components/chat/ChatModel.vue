<template>
  <div class="chat-wrapper" :class="`theme-${theme}`" :style="wrapperStyle">
    <!-- 悬浮按钮 -->
    <div v-if="!visible" class="chat-fab" @click="open" @mousedown="startDrag" title="AI 助手">
        <span class="fab-emoji">🤖</span>
        <span class="fab-label">AI 助手</span>
      </div>

    <!-- 聊天窗口 + 拓展槽 -->
      <div v-show="visible" class="panel-row" :class="{ docked }">
        <div ref="panel" :class="['chat-panel', { docked }]" :style="panelStyle">
        <!-- 头部 -->
        <div class="chat-header" @mousedown="startDrag">
          <div class="chat-header-left">
            <span class="chat-logo-emoji">&#x1F916;</span>
            <div>
              <strong>金陵阡陌 AI 助手</strong>
              <small>Powered by DeepSeek</small>
            </div>
          </div>
          <div class="chat-header-right">
            <button class="chat-btn-icon" :title="docked ? '取消吸附' : '吸附到右侧'" @click="docked = !docked">
              <i :class="docked ? 'el-icon-d-arrow-left' : 'el-icon-d-arrow-right'"></i>
            </button>
            <button class="chat-btn-icon" title="清空对话" @click="clearMessages">
              <i class="el-icon-delete"></i>
            </button>
            <button class="chat-btn-icon" title="关闭" @click="closeChat">
              <i class="el-icon-close"></i>
            </button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div class="chat-body" ref="chatBody">
          <div v-if="messages.length === 0" class="chat-empty">
            <span class="empty-emoji">&#x1F916;</span>
            <p>你好！我是金陵阡陌 AI 助手</p>
            <span>可以问我关于无人机巡检、航线规划、全景分析等问题</span>
            <div class="quick-questions">
              <button v-for="q in quickQuestions" :key="q" @click="sendQuick(q)">{{ q }}</button>
            </div>
          </div>

          <div
            v-for="(msg, idx) in messages"
            :key="idx">
            <div
              v-show="msg.role !== 'tool'"
              class="chat-msg"
              :class="msg.role">
              <span class="msg-name">{{ msg.role === 'user' ? username : msg.role === 'tool-info' ? '系统' : modelName }}</span>
              <div class="msg-row">
                <div class="msg-avatar">
                  <i v-if="msg.role === 'user'" class="el-icon-user"></i>
                  <span v-else-if="msg.role === 'tool-info'" class="avatar-emoji">&#x1F4CD;</span>
                  <span v-else class="avatar-emoji">&#x1F916;</span>
                </div>
                <div class="msg-content" v-if="msg.role === 'tool-info'" style="background:rgba(0,243,255,0.08);font-style:italic">
                  {{ msg.content }}
                </div>
                <div class="msg-content" v-else-if="msg.role === 'tool'">
                  <!-- tool messages are hidden -->
                </div>
                <div class="msg-content" v-else v-html="renderContent(msg.content)"></div>
              </div>
            </div>
            <div v-if="msg.role === 'assistant' && msg.suggestions && msg.suggestions.length" class="msg-suggestions">
              <button
                v-for="(q, qi) in msg.suggestions"
                :key="qi"
                :style="{ transitionDelay: (0.08 * (qi + 1)) + 's' }"
                @click="sendQuick(q)">
                {{ q }}
              </button>
            </div>
          </div>

          <!-- 打字中 -->
          <div v-if="streaming" class="chat-msg assistant">
            <span class="msg-name">{{ modelName }}</span>
            <div class="msg-row">
              <div class="msg-avatar">
                <span class="avatar-emoji">&#x1F916;</span>
              </div>
              <div class="msg-content streaming-cursor">{{ streamingText || '思考中...' }}</div>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="chat-footer">
          <div class="chat-input-wrap">
            <textarea
              ref="inputArea"
              v-model="input"
              class="chat-input"
              :placeholder="streaming ? 'AI 正在回复...' : '输入消息，Enter 发送'"
              :disabled="streaming"
              rows="1"
              @keydown.enter.exact.prevent="send"
              @input="autoResize"
            ></textarea>
            <button
              class="chat-send-btn"
              :disabled="!input.trim() || streaming"
              @click="send">
              <i class="el-icon-position"></i>
            </button>
          </div>
        </div>

        <!-- 拖拽缩放把手 -->
        <div class="resize-handle" @mousedown.prevent="startResize"></div>
        </div>

        <!-- 右侧拓展槽 -->
        <div v-show="!docked" class="side-rail" :class="{ visible: sideRailVisible }">
          <div class="rail-item small spread-top-2"><i class="el-icon-star-off"></i></div>
          <div class="rail-item small spread-top-1"><i class="el-icon-search"></i></div>
          <div class="rail-item large"><i class="el-icon-plus"></i></div>
          <div class="rail-item small spread-bot-1"><i class="el-icon-s-tools"></i></div>
          <div class="rail-item small spread-bot-2"><i class="el-icon-more"></i></div>
        </div>
      </div>
  </div>
</template>

<script>
import axios from 'axios';
import router from '@/router'
import { mapState } from 'vuex';
import gsap from 'gsap';

const ROUTES = [
  { path: '/task-mgmt/verify-clue',                              title: '项目管理' },
  { path: '/data-management/one-map',                             title: '一张图' },
  { path: '/data-management/table',                               title: '影像管理' },
  { path: '/route-planning/panoramicpoint-planning',              title: '全景规划' },
  { path: '/route-planning/algorithm-planning',                   title: '算法规划' },
  { path: '/route-planning/manual-planning',                      title: '人工选点' },
  { path: '/panoramic-detection/map-view',                        title: '地图总览' },
  { path: '/panoramic-detection/grid-management',                 title: '范围管理' },
  { path: '/panoramic-detection/task-management',                 title: '批次管理' },
  { path: '/panoramic-detection/main-detection',                  title: '全景检测' },
  { path: '/panoramic-detection/frame-area',                      title: '不检测区域' },
  { path: '/panoramic-detection/panorama-change-detection',       title: '全景变化' },
  { path: '/panoramic-detection/scene',                           title: '场景管理' },
  { path: '/panoramic-detection/clue-view',                       title: '线索总览' },
  { path: '/panoramic-detection/main-detection-temp',             title: '临时批次' },
  { path: '/panoramic-detection/report',                          title: '报告管理' },
  { path: '/pattern-verifiy/task_management',                     title: '任务管理' },
];

const TOOLS = [
  {
    type: 'function',
    function: {
      name: 'navigate_page',
      description:
        '跳转到系统的页面。根据用户意图从下面列表中选择最匹配的路由：\n' +
        ROUTES.map(r => `  ${r.path} → ${r.title}`).join('\n'),
      parameters: {
        type: 'object',
        properties: {
          path: { type: 'string', description: '目标页面路由路径，必须从上面的路由列表中选择' },
          reason: { type: 'string', description: '简短说明跳转原因' },
        },
        required: ['path', 'reason'],
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'map_action',
      description: '地图相关操作。用户提到任何地点/区域/行政区时必须调用此工具，不要反问。系统会自动定位并绘制边界。',
      parameters: {
        type: 'object',
        properties: {
          location: { type: 'string', description: '目标地点/区域名称，如城市名、区名、街道名、地标名' },
          city: { type: 'string', description: '所在城市，默认南京' },
        },
        required: ['location'],
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'lookup_task',
      description: '根据用户输入的任务编号（batch_id）查询任务是否存在。编号格式通常类似 LS32020000120260701 或 32011300500120250715。如果任务存在则跳转到任务详情页。',
      parameters: {
        type: 'object',
        properties: {
          task_id: { type: 'string', description: '用户提供的任务编号（batch_id）' },
        },
        required: ['task_id'],
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'query_data',
      description: '查询系统数据，如资源数量、任务状态、航线信息等',
      parameters: {
        type: 'object',
        properties: {
          query: { type: 'string', description: '用户想问的问题或要查询的内容' },
        },
        required: ['query'],
      },
    },
  },
];

export default {
  name: 'ChatModel',
  data() {
    return {
      visible: false,
      input: '',
      messages: [],
      streaming: false,
      streamingText: '',
      dragging: false,
      hasMoved: false,
      dragPos: { x: null, y: null },
      dragStart: { x: 0, y: 0, elX: 0, elY: 0 },
      docked: false,
      sideRailVisible: false,
      panelW: 400,
      panelH: 560,
      resizing: false,
      resizeStart: { x: 0, y: 0, w: 0, h: 0 },
      quickQuestions: [
        '带我去南京鼓楼区看看',
        '带我去航线规划页面',
        '打开全景检测',
      ],
      username: '用户',
      modelName: 'DeepSeek',
    }
  },
  computed: {
    ...mapState({ theme: state => state.theme }),
    panelStyle() {
      if (this.docked) return {}
      return { width: this.panelW + 'px', height: this.panelH + 'px' }
    },
    wrapperStyle() {
      if (this.docked) {
        return { right: '0', top: '0', bottom: '0', left: 'auto', width: '400px', height: '100%' }
      }
      if (this.dragPos.x != null) {
        return {
          right: 'auto',
          bottom: 'auto',
          left: this.dragPos.x + 'px',
          top: this.dragPos.y + 'px',
        }
      }
      return { right: '32px', bottom: '32px' }
    },
  },
  mounted() {
    this._onDragMove = this.onDragMove.bind(this)
    this._onDragEnd = this.onDragEnd.bind(this)
    this._onGlobalMouse = this.onGlobalMouse.bind(this)
    this._onResizeMove = this.onResizeMove.bind(this)
    this._onResizeEnd = this.onResizeEnd.bind(this)
    document.addEventListener('mousemove', this._onDragMove)
    document.addEventListener('mouseup', this._onDragEnd)
    document.addEventListener('mousemove', this._onGlobalMouse)
    document.addEventListener('mousemove', this._onResizeMove)
    document.addEventListener('mouseup', this._onResizeEnd)
  },
  beforeDestroy() {
    document.removeEventListener('mousemove', this._onDragMove)
    document.removeEventListener('mouseup', this._onDragEnd)
    document.removeEventListener('mousemove', this._onGlobalMouse)
    document.removeEventListener('mousemove', this._onResizeMove)
    document.removeEventListener('mouseup', this._onResizeEnd)
  },
  methods: {
    startDrag(e) {
      // 不干扰按钮点击
      if (e.target.closest('.chat-btn-icon') || e.target.closest('.chat-send-btn')) return
      e.preventDefault()
      const rect = this.$el.getBoundingClientRect()
      this.dragging = true
      this.hasMoved = false
      this.dragStart = {
        x: e.clientX,
        y: e.clientY,
        elX: rect.left,
        elY: rect.top,
      }
    },
    onDragMove(e) {
      if (!this.dragging) return
      const dx = e.clientX - this.dragStart.x
      const dy = e.clientY - this.dragStart.y
      // 超过 4px 才算拖拽，防止误判
      if (Math.abs(dx) < 4 && Math.abs(dy) < 4) return
      this.hasMoved = true
      // 用 panelW/panelH 作为参考尺寸
      const w = this.panelW
      const h = this.panelH
      let nx = this.dragStart.elX + (e.clientX - this.dragStart.x)
      let ny = this.dragStart.elY + (e.clientY - this.dragStart.y)

      // 触碰边界时重置参考点，防止粘连
      if (nx < 0)          { nx = 0;           this.dragStart.x = e.clientX; this.dragStart.elX = 0 }
      if (nx > innerWidth  - w) { nx = innerWidth  - w; this.dragStart.x = e.clientX; this.dragStart.elX = nx }
      if (ny < 0)          { ny = 0;           this.dragStart.y = e.clientY; this.dragStart.elY = 0 }
      if (ny > innerHeight - h) { ny = innerHeight - h; this.dragStart.y = e.clientY; this.dragStart.elY = ny }

      this.dragPos = { x: nx, y: ny }
    },
    onDragEnd() {
      this.dragging = false
    },
    startResize(e) {
      this.resizing = true
      this.resizeStart = { x: e.clientX, y: e.clientY, w: this.panelW, h: this.panelH }
    },
    onResizeMove(e) {
      if (!this.resizing) return
      const dx = e.clientX - this.resizeStart.x
      const dy = e.clientY - this.resizeStart.y
      this.panelW = Math.min(700, Math.max(320, this.resizeStart.w + dx))
      this.panelH = Math.min(window.innerHeight * 0.85, Math.max(400, this.resizeStart.h + dy))
    },
    onResizeEnd() {
      this.resizing = false
    },
    onGlobalMouse(e) {
      // 面板打开时，鼠标靠近面板右侧边缘浮现拓展槽
      if (!this.visible || this.docked) {
        this.sideRailVisible = false
        return
      }
      const panel = this.$refs.panel
      if (!panel) { this.sideRailVisible = false; return }
      const rect = panel.getBoundingClientRect()
      // 鼠标在面板右侧 100px 范围内触发
      const nearRight = e.clientX > rect.right && e.clientX < rect.right + 100
      // 鼠标垂直方向也要在面板范围内
      const inVert = e.clientY > rect.top && e.clientY < rect.bottom
      this.sideRailVisible = nearRight && inVert
    },
    open() {
      // 拖拽后不触发点击打开
      if (this.hasMoved) return
      // 跳转后的残留消息，重置为欢迎界面
      if (this.messages.length === 1 && this.messages[0].content.startsWith('已为您跳转到')) {
        this.messages = []
      }
      // 展开面板前，确保面板不超出屏幕
      let x = this.dragPos.x != null ? this.dragPos.x : window.innerWidth - 24 - 56
      let y = this.dragPos.y != null ? this.dragPos.y : window.innerHeight - 24 - 56
      this.visible = true
      this.$nextTick(() => {
        // 用实际渲染尺寸做边界修正（含 border）
        const rect = this.$el.getBoundingClientRect()
        const pw = rect.width || 400
        const ph = rect.height || 560
        if (x + pw > window.innerWidth) x = window.innerWidth - pw - 12
        if (y + ph > window.innerHeight) y = window.innerHeight - ph - 12
        this.dragPos = { x: Math.max(0, x), y: Math.max(0, y) }

        const panel = this.$refs.panel
        if (panel) {
          gsap.fromTo(panel,
            {
              scale: 0.1, opacity: 0,
              boxShadow: '0 0 20px rgba(100,180,255,0.3), 0 0 40px rgba(100,180,255,0.1), 0 0 0 1px rgba(255,255,255,0.05) inset',
              borderColor: 'rgba(100,180,255,0.35)',
            },
            {
              scale: 1, opacity: 1,
              boxShadow: '0 24px 64px rgba(0,0,0,0.45), 0 0 0 1px rgba(255,255,255,0.05) inset, 0 1px 0 rgba(255,255,255,0.06) inset',
              borderColor: 'rgba(255,255,255,0.1)',
              duration: 0.5,
              ease: 'back.out(1.7)',
            }
          )
        }
        this.$refs.inputArea?.focus()
        this.scrollToBottom()
      })
    },

    resolveRoute(path) {
      return path
    },

    closeChat() {
      const panel = this.$refs.panel
      if (panel && this.visible) {
        gsap.to(panel, {
          scale: 0.1, opacity: 0,
          boxShadow: '0 0 16px rgba(100,180,255,0.25), 0 0 32px rgba(100,180,255,0.08), 0 0 0 1px rgba(255,255,255,0.05) inset',
          borderColor: 'rgba(100,180,255,0.3)',
          duration: 0.3,
          ease: 'power2.in',
          onComplete: () => {
            this.visible = false
            this.docked = false
            this.dragPos = { x: null, y: null }
            this.messages = []
          },
        })
      } else {
        this.visible = false
        this.docked = false
        this.dragPos = { x: null, y: null }
        this.messages = []
      }
    },

    sendQuick(question) {
      this.input = question
      this.send()
    },

    async send() {
      const text = this.input.trim()
      if (!text || this.streaming) return

      this.messages.push({ role: 'user', content: text })
      this.input = ''
      this.$nextTick(() => this.autoResize())
      this.streaming = true

      await this.chatLoop()
    },

    async chatLoop() {
      const allMessages = this.messages
          .filter(m => m.role !== 'tool-info' && m.role !== 'tool' && !m.tool_calls)
          .map(m => ({ role: m.role, content: m.content }))

      try {
        const { data } = await axios({
          method: 'POST',
          url: 'http://127.0.0.1:8009/api/system/chat/completions',
          data: { messages: allMessages, tools: TOOLS },
          withCredentials: false,
        })
        const result = data.result || data.data || {}
        const finishReason = result.finish_reason

        // 提取用户名和模型名
        if (result.username) this.username = result.username
        if (result.model) this.modelName = result.model

        // 处理工具调用
        if (result.tool_calls && finishReason === 'tool_calls') {
          const assistantMsg = { role: 'assistant', content: '', tool_calls: result.tool_calls }
          if (result.content) assistantMsg.content = result.content
          this.messages.push(assistantMsg)

          // 执行每个工具
          for (const tc of result.tool_calls) {
            const fn = tc.function
            const args = JSON.parse(fn.arguments)
            const toolResult = await this.executeTool(fn.name, args)
            // 导航类工具执行后直接结束，清空消息历史
            if (toolResult._navigate) {
              this.messages = []
              this.dragPos = { x: null, y: null }
              let label
              if (fn.name === 'map_action') {
                label = args.name || args.location
              } else if (fn.name === 'lookup_task') {
                label = `任务 ${toolResult.batch_name || args.task_id}`
              } else {
                label = args.reason || args.path
              }
              this.messages.push({ role: 'assistant', content: `已为您跳转到 ${label}` })
              this.streaming = false
              return
            }
            if (toolResult._stop) {
              // 非导航类 stop：错误消息已由 executeTool 直接推入 messages，直接退出
              this.streaming = false
              return
            }
            this.messages.push({
              role: 'tool',
              tool_call_id: tc.id,
              content: JSON.stringify(toolResult),
            })
          }
          // 继续对话循环（非导航类工具）
          await this.chatLoop()
          return
        }

        // 普通文本回复
        const content = result.content || ''
        await this.typewriter(content)
      } catch (err) {
        const msg = err.response?.data?.msg || err.message
        this.messages.push({ role: 'assistant', content: `抱歉，请求失败：${msg}` })
        this.streaming = false
      }
    },

    async executeTool(name, args) {
      if (name === 'navigate_page') {
        const path = this.resolveRoute(args.path)
        this.messages.push({ role: 'tool-info', content: `正在跳转到：${args.reason}` })
        this.$nextTick(() => {
          this.visible = false
          router.push(path).catch(() => {})
        })
        return { _navigate: true, path, reason: args.reason }
      }
      if (name === 'map_action') {
        const detail = {
          name: args.name || args.location,
          location: args.location,
          polygon: args.polygon || [],
          subRegions: args.sub_regions || [],
          lat: args.lat,
          lng: args.lng,
          city: args.city || '南京',
        }
        const hasPolygon = detail.polygon && detail.polygon.length > 0
        this.messages.push({ role: 'tool-info', content: hasPolygon
          ? `正在定位并圈定 ${detail.name}...`
          : `正在定位到 ${detail.name}...` })
        const dispatch = () => {
          if (hasPolygon) window.dispatchEvent(new CustomEvent('draw-region', { detail }))
          if (detail.lat != null) window.dispatchEvent(new CustomEvent('navigate-map', { detail }))
        }
        if (this.$route.path !== '/data-management/one-map') {
          router.push('/data-management/one-map')
          setTimeout(dispatch, 1500)
        } else {
          dispatch()
        }
        return { _navigate: true, success: true, ...detail }
      }
      if (name === 'lookup_task') {
        const taskId = args.task_id
        // 结果已由后端后处理注入 _lookup_found，无需二次请求
        if (args._lookup_found) {
          this.messages.push({ role: 'tool-info', content: `找到任务：${args._batch_name}` })
          this.$nextTick(() => {
            this.visible = false
            router.push(`/panoramic-detection/verifyClue?id=${taskId}`).catch(() => {})
          })
          return { _navigate: true, task_id: taskId, batch_name: args._batch_name }
        } else {
          const msg = args._msg || `未查询到任务编号为 ${taskId} 的任务`
          this.messages.push({ role: 'assistant', content: msg })
          return { _stop: true, message: msg }
        }
      }
      if (name === 'query_data') {
        return { message: `关于"${args.query}"的查询已收到，具体数据需要通过系统界面查看。` }
      }
      return { error: `未知工具: ${name}` }
    },

    async typewriter(text) {
      // 解析 ||| 分隔符：前半是正文，后半是 3 个建议问题
      let body = text
      let suggestions = []
      const m = text.match(/[\s\S]*?\n\|\|\|\n([\s\S]*)$/)
      if (m) {
        body = text.substring(0, m.index + m[0].indexOf('\n|||')).trimEnd()
        suggestions = m[1].split('\n').map(s => s.replace(/^[\d.\-•\s]+/, '').trim()).filter(Boolean).slice(0, 3)
      } else if (text.includes('|||')) {
        // 降级：||| 前可能没换行
        const idx = text.indexOf('|||')
        body = text.substring(0, idx).trimEnd()
        suggestions = text.substring(idx + 3).split('\n').map(s => s.replace(/^[\d.\-•\s]+/, '').trim()).filter(Boolean).slice(0, 3)
      }
      this.streamingText = ''
      const chars = [...body]
      const renderInline = (raw) => {
        let t = raw
          .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
          .replace(/\*\*[^*]*$/, m => m.slice(2))
          .replace(/\*([^*]+)\*/g, '<em>$1</em>')
          .replace(/\*([^*]*)$/, '')
          .replace(/`([^`]+)`/g, '<code>$1</code>')
          .replace(/`([^`]*)$/, '')
          .replace(/```\w*\n?([\s\S]*)$/, (_, c) => c ? `<pre><code>${c}</code></pre>` : '')
        return t
      }
      for (let i = 0; i < chars.length; i++) {
        this.streamingText = renderInline(this.streamingText.replace(/<[^>]*>/g, '') + chars[i])
        await new Promise(r => setTimeout(r, 25))
        this.scrollToBottom()
      }
      this.messages.push({ role: 'assistant', content: body, suggestions })
      this.streamingText = ''
      this.streaming = false
    },

    clearMessages() {
      this.messages = []
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const el = this.$refs.chatBody
        if (el) el.scrollTop = el.scrollHeight
      })
    },

    autoResize() {
      this.$nextTick(() => {
        const el = this.$refs.inputArea
        if (el) {
          el.style.height = 'auto'
          el.style.height = Math.min(el.scrollHeight, 120) + 'px'
        }
      })
    },

    renderContent(text) {
      if (!text) return ''
      const codeBlocks = []
      let processed = text
        .replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
          codeBlocks.push(`<pre><code>${this.esc(code.trim())}</code></pre>`)
          return `%%CODEBLOCK_${codeBlocks.length - 1}%%`
        })
        .replace(/`([^`]+)`/g, (_, code) => {
          codeBlocks.push(`<code>${this.esc(code)}</code>`)
          return `%%CODEBLOCK_${codeBlocks.length - 1}%%`
        })
      processed = this.esc(processed)
      processed = processed.replace(/\n/g, '<br>')
      processed = processed
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')
      processed = processed.replace(/%%CODEBLOCK_(\d+)%%/g, (_, i) => codeBlocks[+i])
      return processed
    },
    esc(s) {
      return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    },
  },
}
</script>

<style lang="scss" scoped>
.chat-wrapper {
  position: fixed;
  z-index: 9999;
}

/* 悬浮按钮 — 灵动岛胶囊形 */
.chat-fab {
  height: 48px;
  min-width: 48px;
  padding: 0 18px;
  border-radius: 28px;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.06) inset;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  cursor: pointer;
  color: #fff;
  user-select: none;
  transition:
    all 0.55s cubic-bezier(0.16, 1, 0.3, 1),
    gap 0.45s 0.08s,
    padding 0.45s 0.08s;

  &:hover {
    transform: scale(1.05);
    min-width: auto;
    padding: 0 22px 0 20px;
    gap: 7px;
    background: rgba(0, 0, 0, 0.7);
    border-color: rgba(255, 255, 255, 0.28);
    box-shadow:
      0 16px 48px rgba(0, 0, 0, 0.4),
      0 0 20px rgba(59, 130, 246, 0.2),
      0 0 0 1px rgba(255, 255, 255, 0.12) inset;
  }

  .fab-emoji {
    font-size: 22px;
    line-height: 1;
    transition: transform 0.55s cubic-bezier(0.16, 1, 0.3, 1);
  }

  &:hover .fab-emoji {
    transform: rotate(-12deg) scale(1.15);
  }

  .fab-label {
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
    max-width: 0;
    overflow: hidden;
    opacity: 0;
    transition:
      max-width 0.5s cubic-bezier(0.16, 1, 0.3, 1),
      opacity 0.35s 0.1s;
  }

  &:hover .fab-label {
    max-width: 80px;
    opacity: 1;
  }
}

/* 面板行 — flex 并排聊天面板 + 拓展槽 */
.panel-row {
  position: relative;
  display: flex;
  align-items: center;

  &.docked {
    height: 100%;
    align-items: flex-start;
  }
}

/* ======================== 右侧拓展槽 — 透明半圆弧 ======================== */
.side-rail {
  position: absolute;
  left: 100%;
  margin-left: 4px;
  top: 50%;
  width: 90px;
  height: 160px;
  z-index: 9998;
  opacity: 0;
  transform: translate(16px, -50%);
  pointer-events: none;
  transition: opacity 0.35s ease, transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);

  &.visible {
    opacity: 1;
    transform: translate(0, -50%);
    pointer-events: auto;
  }
}

.rail-item {
  position: absolute;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s ease;

  /* 大圆：左中，始终可见 */
  &.large {
    width: 44px;
    height: 44px;
    left: 2px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 20px;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(37, 99, 235, 0.15));
    border: 1px solid rgba(59, 130, 246, 0.35);
    color: rgba(200, 220, 255, 0.9);
    box-shadow: 0 0 16px rgba(59, 130, 246, 0.15);
    z-index: 2;

    &:hover {
      background: linear-gradient(135deg, rgba(59, 130, 246, 0.5), rgba(37, 99, 235, 0.3));
      border-color: rgba(59, 130, 246, 0.6);
      box-shadow: 0 0 24px rgba(59, 130, 246, 0.35);
    }
  }

  /* 小圆：默认隐藏，hover 时从大圆向外散开成弧 */
  &.small {
    width: 28px;
    height: 28px;
    font-size: 12px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: rgba(255, 255, 255, 0.55);
    opacity: 0;
    transform: scale(0);
    transition:
      opacity 0.3s ease,
      transform 0.4s cubic-bezier(0.16, 1, 0.3, 1),
      background 0.25s ease,
      border-color 0.25s ease,
      color 0.25s ease,
      box-shadow 0.25s ease;

    &:hover {
      background: rgba(255, 255, 255, 0.16);
      border-color: rgba(255, 255, 255, 0.25);
      color: #fff;
      box-shadow: 0 0 14px rgba(100, 180, 255, 0.25);
    }
  }
}

/* 小圆半圆弧位置 */
.spread-top-2 { left: 36px; top: 6px; }
.spread-top-1 { left: 56px; top: 42px; }
.spread-bot-1 { left: 56px; top: 90px; }
.spread-bot-2 { left: 36px; top: 126px; }

/* hover 时小圆散开 — 交错延迟 */
.side-rail:hover .rail-item.small {
  opacity: 1;
  transform: scale(1);
}
.side-rail:hover .spread-top-2 { transition-delay: 0s; }
.side-rail:hover .spread-top-1 { transition-delay: 0.06s; }
.side-rail:hover .spread-bot-1 { transition-delay: 0.06s; }
.side-rail:hover .spread-bot-2 { transition-delay: 0.12s; }

/* 亮色主题适配 */
.theme-light .rail-item.large {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.45), rgba(59, 130, 246, 0.25));
  border-color: rgba(37, 99, 235, 0.4);
  color: #fff;
  box-shadow: 0 0 18px rgba(37, 99, 235, 0.2);

  &:hover {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.6), rgba(59, 130, 246, 0.4));
    box-shadow: 0 0 28px rgba(37, 99, 235, 0.4);
  }
}
.theme-light .rail-item.small {
  background: rgba(0, 0, 0, 0.1);
  border-color: rgba(0, 0, 0, 0.2);
  color: #374151;

  &:hover {
    background: rgba(37, 99, 235, 0.18);
    border-color: rgba(37, 99, 235, 0.4);
    color: #1e40af;
    box-shadow: 0 0 14px rgba(37, 99, 235, 0.2);
  }
}

/* 聊天面板 — 毛玻璃 */
.chat-panel {
  box-sizing: border-box;
  border-radius: 20px;
  background: rgba(12, 20, 40, 0.72);
  backdrop-filter: blur(24px) saturate(1.2);
  -webkit-backdrop-filter: blur(24px) saturate(1.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow:
    0 24px 64px rgba(0, 0, 0, 0.45),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset,
    0 1px 0 rgba(255, 255, 255, 0.06) inset;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transform-origin: bottom right;
  will-change: transform, opacity;
  transition: height 0.3s ease, border-radius 0.3s ease;
}

.chat-panel.docked {
  width: 100%;
  height: calc(100% - 48px);
  border-radius: 12px 0 0 12px;
  border-right: none;
  margin-top: 48px;
}

/* 头部 — 毛玻璃顶栏 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.03);
  user-select: none;

  &:active {
    cursor: grabbing;
  }
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 10px;

  .chat-logo-emoji {
    font-size: 24px;
  }

  strong {
    display: block;
    font-size: 14px;
    color: var(--text-primary, #fff);
  }

  small {
    font-size: 11px;
    color: var(--text-muted, rgba(140, 182, 214, 0.78));
  }
}

.chat-header-right {
  display: flex;
  gap: 4px;
}

.chat-btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.4);
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;

  &:hover {
    background: rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.9);
  }
}

/* 消息区 */
.chat-body {
  flex: 1;
  overflow-y: overlay;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;

  &::-webkit-scrollbar { width: 5px; }
  &::-webkit-scrollbar-thumb {
    background: transparent;
    border-radius: 3px;
    transition: background 0.3s;
  }
  &::-webkit-scrollbar-track { background: transparent; }

  &:hover::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
  }
}

/* 空状态 */
.chat-empty {
  text-align: center;
  padding: 32px 10px;

  .empty-emoji {
    font-size: 52px;
    opacity: 0.4;
  }

  p {
    margin: 14px 0 4px;
    color: rgba(255, 255, 255, 0.9);
    font-size: 16px;
    font-weight: 600;
  }

  span {
    color: rgba(255, 255, 255, 0.45);
    font-size: 12px;
  }

  .quick-questions {
    margin-top: 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;

    button {
      padding: 8px 16px;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.06);
      color: rgba(255, 255, 255, 0.75);
      font-size: 12px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s;
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);

      &:hover {
        background: rgba(255, 255, 255, 0.12);
        border-color: rgba(255, 255, 255, 0.25);
        color: #fff;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
    }
  }
}

/* 消息气泡 */
.chat-msg {
  display: flex;
  flex-direction: column;
  gap: 3px;
  max-width: 100%;

  &.user {
    align-items: flex-end;

    .msg-name {
      text-align: right;
      padding-right: 2px;
      color: #60a5fa;
    }

    .msg-row {
      flex-direction: row-reverse;
    }

    .msg-avatar {
      background: linear-gradient(135deg, #3b82f6, #2563eb);
      color: #fff;
      border-radius: 50%;
    }

    .msg-content {
      background: linear-gradient(135deg, #3b82f6, #2563eb);
      border: none;
      border-radius: 18px 4px 18px 18px;
      color: #fff;
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
    }
  }

  &.assistant {
    .msg-name {
      padding-left: 2px;
      color: rgba(200, 220, 255, 0.6);
    }

    .msg-avatar {
      background: rgba(255, 255, 255, 0.1);
      color: rgba(255, 255, 255, 0.7);
      border-radius: 50%;
    }

    .msg-content {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 4px 18px 18px 18px;
      color: rgba(255, 255, 255, 0.9);
    }
  }
}

.msg-name {
  font-size: 11px;
  font-weight: 500;
  user-select: none;
}

.msg-row {
  display: flex;
  gap: 8px;
}

.msg-avatar {
  width: 34px;
  height: 34px;
  min-width: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;

  .avatar-emoji {
    font-size: 16px;
    line-height: 1;
  }
}

.msg-content {
  padding: 12px 16px;
  font-size: 13px;
  line-height: 1.6;
  word-break: break-word;

  :deep(pre) {
    background: rgba(0, 0, 0, 0.25);
    border-radius: 10px;
    padding: 10px;
    margin: 8px 0;
    overflow-x: auto;
    font-size: 12px;

    code {
      background: none;
      padding: 0;
    }
  }

  :deep(code) {
    background: rgba(0, 0, 0, 0.2);
    padding: 2px 5px;
    border-radius: 4px;
    font-size: 12px;
  }

  :deep(strong) {
    color: var(--brand-accent, #60a5fa);
  }
}

.msg-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-left: 42px;
  margin-bottom: 8px;
  margin-top: 4px;

  button {
    all: unset;
    cursor: pointer;
    padding: 6px 14px;
    font-size: 12px;
    line-height: 1.4;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.75);
    transition: all 0.25s ease;
    white-space: nowrap;

    &:hover {
      background: rgba(37, 99, 235, 0.15);
      border-color: rgba(37, 99, 235, 0.35);
      color: #fff;
      transform: translateY(-1px);
    }
  }
}

.theme-light .msg-suggestions button {
  background: rgba(0, 0, 0, 0.04);
  border-color: rgba(0, 0, 0, 0.08);
  color: #475569;

  &:hover {
    background: rgba(37, 99, 235, 0.08);
    border-color: rgba(37, 99, 235, 0.25);
    color: #2563eb;
    transform: translateY(-1px);
  }
}

.streaming-cursor::after {
  content: '|';
  animation: blink 0.8s infinite;
  color: var(--brand-accent, #00f3ff);
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 输入区 */
.chat-footer {
  padding: 14px 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.02);
}

.chat-input-wrap {
  display: flex;
  align-items: flex-end;
  border: 1.5px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.04);
  padding: 3px 3px 3px 14px;
  transition: all 0.3s ease;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);

  &:focus-within {
    border-color: rgba(59, 130, 246, 0.45);
    box-shadow:
      inset 0 1px 3px rgba(0, 0, 0, 0.2),
      0 0 0 4px rgba(59, 130, 246, 0.12);
  }
}

.chat-input {
  flex: 1;
  resize: none;
  border: none;
  padding: 7px 0;
  background: transparent;
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  line-height: 1.5;
  font-family: inherit;
  outline: none;
  max-height: 120px;

  &::placeholder {
    color: rgba(255, 255, 255, 0.3);
  }

  &:disabled {
    opacity: 0.4;
  }
}

.chat-send-btn {
  width: 34px;
  height: 34px;
  min-width: 34px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #fff;
  font-size: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s ease;
  flex-shrink: 0;

  &:hover:not(:disabled) {
    transform: scale(1.1);
    background: linear-gradient(135deg, #4f8bf9, #3070f0);
  }

  &:active:not(:disabled) {
    transform: scale(0.95);
  }

  &:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
}

/* 拖拽缩放把手 */
.resize-handle {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 24px;
  height: 24px;
  cursor: nwse-resize;
  z-index: 10;
  background:
    linear-gradient(135deg, transparent 50%, rgba(255,255,255,0.15) 50%),
    linear-gradient(135deg, transparent 50%, rgba(255,255,255,0.15) 50%);
  background-size: 6px 6px, 10px 10px;
  background-position: 100% 100%, calc(100% - 8px) calc(100% - 8px);
  background-repeat: no-repeat;
  opacity: 0.4;
  transition: opacity 0.2s;

  &:hover {
    opacity: 0.9;
  }
}

.theme-light .resize-handle {
  background:
    linear-gradient(135deg, transparent 50%, rgba(0,0,0,0.12) 50%),
    linear-gradient(135deg, transparent 50%, rgba(0,0,0,0.12) 50%);
  background-size: 6px 6px, 10px 10px;
  background-position: 100% 100%, calc(100% - 8px) calc(100% - 8px);
  background-repeat: no-repeat;
}

/* 过渡动画 — 由 GSAP JS 钩子驱动 */

/* ======================== 亮色主题 ======================== */
.theme-light .chat-fab {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-color: rgba(0, 0, 0, 0.08);
  color: #475569;
  box-shadow: 0 8px 32px rgba(0,0,0,0.08), 0 0 0 1px rgba(255,255,255,0.5) inset;
}
.theme-light .chat-fab:hover {
  background: rgba(255, 255, 255, 0.85);
  border-color: rgba(37, 99, 235, 0.3);
  color: #2563eb;
  box-shadow: 0 12px 40px rgba(0,0,0,0.12), 0 0 0 1px rgba(255,255,255,0.6) inset;
}
.theme-light .chat-panel {
  background: rgba(255, 255, 255, 0.62);
  backdrop-filter: blur(28px) saturate(1.4);
  -webkit-backdrop-filter: blur(28px) saturate(1.4);
  border-color: rgba(0, 0, 0, 0.06);
  box-shadow: 0 24px 64px rgba(0,0,0,0.12), 0 0 0 1px rgba(255,255,255,0.4) inset;
}
.theme-light .chat-header {
  border-bottom-color: rgba(0, 0, 0, 0.05);
}
.theme-light .chat-header h3 {
  color: #1e293b;
}
.theme-light .chat-header-left strong {
  color: #1e293b !important;
}
.theme-light .chat-header-left small {
  color: #94a3b8 !important;
}
.theme-light .chat-btn-icon {
  color: #94a3b8;
}
.theme-light .chat-btn-icon:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #475569;
}
.theme-light .chat-body {
  background: transparent;
}
.theme-light .chat-body:hover::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.12);
}
.theme-light .chat-empty p {
  color: #1e293b;
}
.theme-light .chat-empty span {
  color: #94a3b8;
}
.theme-light .quick-questions button {
  background: rgba(0, 0, 0, 0.04);
  border-color: rgba(0, 0, 0, 0.08);
  color: #475569;
}
.theme-light .quick-questions button:hover {
  background: rgba(37, 99, 235, 0.08);
  border-color: rgba(37, 99, 235, 0.25);
  color: #2563eb;
}
.theme-light .chat-msg.user .msg-content {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
}
.theme-light .chat-msg.assistant .msg-content {
  background: rgba(0, 0, 0, 0.04);
  border-color: rgba(0, 0, 0, 0.06);
  color: #334155;
}
.theme-light .chat-msg.assistant .msg-avatar {
  background: rgba(0, 0, 0, 0.06);
  color: #64748b;
}
.theme-light .chat-msg.user .msg-name {
  color: #2563eb;
}
.theme-light .chat-msg.assistant .msg-name {
  color: #94a3b8;
}
.theme-light .chat-msg .msg-content :deep(strong) {
  color: #2563eb;
}
.theme-light .chat-footer {
  border-top-color: rgba(0, 0, 0, 0.05);
}
.theme-light .chat-input-wrap {
  border-color: rgba(0, 0, 0, 0.1);
  background: rgba(0, 0, 0, 0.03);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);

  &:focus-within {
    border-color: rgba(37, 99, 235, 0.4);
    background: rgba(0, 0, 0, 0.04);
    box-shadow:
      inset 0 1px 3px rgba(0, 0, 0, 0.05),
      0 0 0 4px rgba(37, 99, 235, 0.1);
  }
}
.theme-light .chat-input {
  color: #1e293b;
  background: transparent;
}
.theme-light .chat-input::placeholder {
  color: #94a3b8;
}
.theme-light .chat-send-btn {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
}
.theme-light .streaming-cursor::after {
  color: #2563eb;
}
</style>
