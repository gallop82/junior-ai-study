<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { ArrowLeft, LoaderCircle, Send, Sparkles } from 'lucide-vue-next'
import { streamChat } from '../api'
import MarkdownContent from '../components/MarkdownContent.vue'
import type { ChatMessage, ConversationRecord, SkillSummary, Teacher } from '../types'

type UiMessage = ChatMessage & {
  isStreaming?: boolean
}

const props = defineProps<{
  skills: SkillSummary[]
  teachers: Teacher[]
}>()

const emit = defineEmits<{
  historyCreated: [record: ConversationRecord]
  filesChanged: []
}>()

const selectedSkill = ref<SkillSummary | null>(null)
const question = ref('')
const loading = ref(false)
const connected = ref(false)
const error = ref('')
const messages = ref<UiMessage[]>([])
const messageListRef = ref<HTMLElement | null>(null)

const selectedTeacher = computed(() => props.teachers[0])

function chooseSkill(skill: SkillSummary) {
  selectedSkill.value = skill
  messages.value = [
    {
      role: 'assistant',
      content: `已选择「${skill.name}」。把题目、材料或学习目标发给我，我会按这个技能来回答。`
    }
  ]
}

function backToSkills() {
  if (loading.value) return
  selectedSkill.value = null
  question.value = ''
  messages.value = []
  error.value = ''
  connected.value = false
}

async function scrollToBottom() {
  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
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
          await new Promise((resolve) => requestAnimationFrame(resolve))
        },
        onDone: (response) => {
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

    if (createdFileCount) emit('filesChanged')
    emit('historyCreated', {
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
</script>

<template>
  <section class="page-section ai-page">
    <div v-if="!selectedSkill" class="skill-page">
      <div class="page-heading skill-heading">
        <h2>选择一个学习技能</h2>
        <p>AI 老师会按照技能说明来回答，并默认保存 Markdown 文件。</p>
      </div>

      <div class="skill-grid">
        <button v-for="skill in skills" :key="skill.id" class="skill-card" type="button" @click="chooseSkill(skill)">
          <div class="skill-icon">
            <Sparkles :size="22" />
          </div>
          <strong>{{ skill.name }}</strong>
          <p>{{ skill.description || '后端自定义学习技能。' }}</p>
        </button>
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
          <span>{{ message.role === 'user' ? '我' : 'AI老师' }}</span>
          <MarkdownContent v-if="message.content" :content="message.content" />
          <p v-else class="typing-placeholder">正在生成...</p>
          <i v-if="message.isStreaming" class="stream-cursor" aria-hidden="true"></i>
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
          placeholder="输入问题，按 Ctrl + Enter 发送"
          :disabled="loading"
          @keydown.ctrl.enter.prevent="submitQuestion"
        />
        <button type="submit" :disabled="loading || !question.trim()">
          <Send :size="18" />
          发送
        </button>
      </form>
    </div>
  </section>
</template>
