<script setup lang="ts">
import { computed, inject, nextTick, onMounted, ref, watch, type Ref } from 'vue'
import { ArrowLeft, BookOpen, LoaderCircle, Pause, Play, Send, Sparkles, Square, Volume2 } from 'lucide-vue-next'
import { fetchSkillContent, streamChat } from '../api'
import { AudioQueuePlayer } from '../utils/audioQueue'
import MarkdownContent from '../components/MarkdownContent.vue'
import type { ChatMessage, ConversationRecord, Skill, SkillSummary, Teacher } from '../types'

type UiMessage = ChatMessage & {
  isStreaming?: boolean
}

const skills = inject<Ref<SkillSummary[]>>('skills', ref([]))
const teachers = inject<Ref<Teacher[]>>('teachers', ref([]))
const addHistory = inject<(record: ConversationRecord) => void>('addHistory', () => {})
const refreshFiles = inject<() => void>('refreshFiles', () => {})

const selectedSkill = ref<SkillSummary | null>(null)
const question = ref('')
const loading = ref(false)
const connected = ref(false)
const error = ref('')
const messages = ref<UiMessage[]>([])
const messageListRef = ref<HTMLElement | null>(null)

/* tts streaming state */
const activeTtsIndex = ref<number | null>(null)
const ttsState = ref<'playing' | 'paused' | 'stopped'>('stopped')
const ttsBuffer = ref('')
let ttsPlayer: AudioQueuePlayer | null = null

/* skill preview */
const previewSkill = ref<Skill | null>(null)
const previewLoading = ref(false)

const selectedTeacher = computed(() => teachers.value[0])

const SESSION_KEY = 'junior-ai-active-session'

onMounted(() => {
  const saved = sessionStorage.getItem(SESSION_KEY)
  if (saved) {
    try {
      const data = JSON.parse(saved)
      if (data.skill && data.messages) {
        selectedSkill.value = data.skill
        messages.value = data.messages
        nextTick(scrollToBottom)
      }
    } catch (e) {
      console.error('Failed to restore session:', e)
    }
  }
})

watch([selectedSkill, messages], ([newSkill, newMessages]) => {
  if (newSkill) {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify({
      skill: newSkill,
      messages: newMessages.map(m => ({ ...m, isStreaming: false }))
    }))
  } else {
    sessionStorage.removeItem(SESSION_KEY)
  }
}, { deep: true })

function chooseSkill(skill: SkillSummary) {
  selectedSkill.value = skill
  messages.value = [
    {
      role: 'assistant',
      content: `已选择「${skill.name}」。把题目、材料或学习目标发给我，我会按这个技能来回答。`
    }
  ]
}

async function openSkillPreview(skill: SkillSummary, e: Event) {
  e.stopPropagation()
  previewLoading.value = true
  try {
    previewSkill.value = await fetchSkillContent(skill.id)
  } catch {
    previewSkill.value = { ...skill, content: '加载失败，请检查后端服务。' }
  } finally {
    previewLoading.value = false
  }
}

function closePreview() {
  previewSkill.value = null
}

function backToSkills() {
  if (loading.value) return
  
  if (ttsPlayer) {
    ttsPlayer.stop()
    ttsPlayer = null
    activeTtsIndex.value = null
  }
  
  selectedSkill.value = null
  question.value = ''
  messages.value = []
  error.value = ''
  connected.value = false
  sessionStorage.removeItem(SESSION_KEY)
}

async function scrollToBottom() {
  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (window.innerWidth <= 860) return
  if (e.isComposing) return
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    submitQuestion()
  }
}

async function submitQuestion() {
  const clean = question.value.trim()
  if (!clean || !selectedSkill.value || loading.value || !selectedTeacher.value) return

  error.value = ''
  question.value = ''
  connected.value = false
  messages.value.push({ role: 'user', content: clean })
  const assistantMessage: UiMessage = { role: 'assistant', content: '', isStreaming: true }
  const assistantMessageIndex = messages.value.length
  messages.value.push(assistantMessage)
  loading.value = true
  await scrollToBottom()

  try {
    let createdFileCount = 0
    let teacherName = selectedTeacher.value.name
    let finalAnswer = ''

    await streamChat(
      {
        question: clean,
        teacher_id: selectedTeacher.value.id,
        skill_ids: [selectedSkill.value.id],
        history: messages.value.slice(0, -1).slice(-10),
        generate_file: true
      },
      {
        onReady: () => {
          connected.value = true
        },
        onChunk: async (content) => {
          messages.value[assistantMessageIndex].content += content
          await scrollToBottom()
          
          if (activeTtsIndex.value === assistantMessageIndex) {
            ttsBuffer.value += content
            const match = ttsBuffer.value.match(/^(.*?[。！？.!?\n]+)(.*)$/s)
            if (match) {
               const chunks = match[1].match(/[^。！？.!?\n]+[。！？.!?\n]*/g) || []
               chunks.forEach(c => ttsPlayer?.enqueue(c))
               ttsBuffer.value = match[2]
            }
          }
          await new Promise((resolve) => requestAnimationFrame(resolve))
        },
        onDone: (response) => {
          messages.value[assistantMessageIndex].isStreaming = false
          messages.value[assistantMessageIndex].content = response.answer
          
          if (activeTtsIndex.value === assistantMessageIndex) {
            if (ttsBuffer.value.trim()) {
              ttsPlayer?.enqueue(ttsBuffer.value)
              ttsBuffer.value = ''
            }
            ttsPlayer?.finish()
          }
          
          finalAnswer = response.answer
          createdFileCount = response.files.length
          teacherName = response.teacher.name
        }
      }
    )

    if (finalAnswer) {
      messages.value[assistantMessageIndex].content = finalAnswer
    }
    messages.value[assistantMessageIndex].isStreaming = false
    await scrollToBottom()

    if (createdFileCount) refreshFiles()
    addHistory({
      id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      skillId: selectedSkill.value.id,
      skillName: selectedSkill.value.name,
      teacherName,
      title: clean.slice(0, 32),
      messages: messages.value.map(({ role, content }) => ({ role, content })),
      createdAt: new Date().toISOString()
    })
  } catch (caught) {
    messages.value.splice(assistantMessageIndex, 1)
    error.value = caught instanceof Error ? caught.message : '请求失败，请检查后端服务。'
  } finally {
    loading.value = false
    connected.value = false
  }
}

function startTts(index: number, message: UiMessage) {
  if (ttsPlayer) {
    ttsPlayer.stop()
  }

  activeTtsIndex.value = index
  ttsState.value = 'playing'
  ttsBuffer.value = ''

  ttsPlayer = new AudioQueuePlayer((state) => {
    ttsState.value = state
    if (state === 'stopped' && activeTtsIndex.value === index) {
      activeTtsIndex.value = null
    }
  })

  const text = message.content || ''
  if (!message.isStreaming) {
    const chunks = text.match(/[^。！？.!?\n]+[。！？.!?\n]*/g) || [text]
    chunks.forEach(c => ttsPlayer!.enqueue(c))
    ttsPlayer!.finish()
  } else {
    const match = text.match(/^(.*?[。！？.!?\n]+)(.*)$/s)
    if (match) {
      const chunks = match[1].match(/[^。！？.!?\n]+[。！？.!?\n]*/g) || []
      chunks.forEach(c => ttsPlayer!.enqueue(c))
      ttsBuffer.value = match[2]
    } else {
      ttsBuffer.value = text
    }
  }
}

function togglePauseTts() {
  if (ttsState.value === 'playing') ttsPlayer?.pause()
  else if (ttsState.value === 'paused') ttsPlayer?.resume()
}

function stopTts() {
  ttsPlayer?.stop()
  activeTtsIndex.value = null
}
</script>

<template>
  <section class="page-section ai-page">
    <div v-if="!selectedSkill" class="skill-page">
      <div class="page-heading skill-heading">
        <h2>选择一个学习技能</h2>
        <p>AI 老师会按照技能说明来回答，并默认保存 Markdown 文件。</p>
      </div>

      <div class="skill-grid">
        <div v-for="skill in skills" :key="skill.id" class="skill-card" @click="chooseSkill(skill)">
          <div class="skill-card-top">
            <div class="skill-icon">
              <Sparkles :size="22" />
            </div>
            <button
              class="skill-preview-btn"
              type="button"
              title="查看技能说明"
              :disabled="previewLoading"
              @click="openSkillPreview(skill, $event)"
            >
              <BookOpen :size="15" />
            </button>
          </div>
          <strong>{{ skill.name }}</strong>
          <p>{{ skill.description || '后端自定义学习技能。' }}</p>
        </div>
      </div>
    </div>

    <div v-else class="chat-layout">
      <div class="chat-head clean">
        <button class="round-icon-button" type="button" aria-label="返回技能" :disabled="loading" @click="backToSkills">
          <ArrowLeft :size="20" />
        </button>
        <div>
          <h2>{{ selectedSkill.name }}</h2>
          <p>{{ selectedSkill.description || '后端自定义学习技能。' }}</p>
        </div>
      </div>

      <div ref="messageListRef" class="message-list">
        <article v-for="(message, index) in messages" :key="index" class="message" :class="message.role">
          <MarkdownContent v-if="message.content" :content="message.content" />
          <p v-else class="typing-placeholder">正在生成...</p>
          <i v-if="message.isStreaming" class="stream-cursor" aria-hidden="true"></i>

          <div v-if="message.role === 'assistant' && message.content" class="tts-controls">
            <template v-if="activeTtsIndex === index">
              <button class="tts-button" type="button" @click="togglePauseTts" :title="ttsState === 'paused' ? '继续朗读' : '暂停朗读'">
                <Play v-if="ttsState === 'paused'" :size="14" />
                <Pause v-else :size="14" />
              </button>
              <button class="tts-button" type="button" @click="stopTts" title="停止朗读">
                <Square :size="14" />
              </button>
            </template>
            <template v-else>
              <button class="tts-button" type="button" @click="startTts(index, message)" title="朗读">
                <Volume2 :size="14" />
              </button>
            </template>
          </div>
        </article>
        <article v-if="loading" class="stream-status">
          <LoaderCircle class="spin" :size="16" />
          <span>{{ connected ? '正在逐字生成，回答结束后会保存会话' : '正在连接模型' }}</span>
        </article>
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>

      <form class="composer clean" @submit.prevent="submitQuestion">
        <textarea
          v-model="question"
          rows="3"
          placeholder="输入问题，Enter 发送，Shift + Enter 换行"
          :disabled="loading"
          @keydown="handleKeydown"
        />
        <button class="send-button" type="submit" :disabled="loading || !question.trim()">
          <span class="send-icon"><Send :size="18" /></span>
          发送
        </button>
      </form>
    </div>

    <!-- skill preview modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="previewSkill" class="skill-preview-overlay" @click.self="closePreview">
          <div class="skill-preview-modal">
            <div class="skill-preview-head">
              <div class="skill-preview-title">
                <div class="skill-icon small">
                  <Sparkles :size="16" />
                </div>
                <h3>{{ previewSkill.name }}</h3>
              </div>
              <button class="round-icon-button small" type="button" aria-label="关闭" @click="closePreview">✕</button>
            </div>
            <div class="skill-preview-body">
              <MarkdownContent :content="previewSkill.content" />
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>
