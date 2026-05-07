<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Bot, BrainCircuit, Clock3, GraduationCap, Menu, X } from 'lucide-vue-next'
import { fetchGeneratedFiles, fetchSkills, fetchTeachers } from './api'
import AiTeacherView from './views/AiTeacherView.vue'
import DigitalTwinView from './views/DigitalTwinView.vue'
import HistoryView from './views/HistoryView.vue'
import type { ConversationRecord, GeneratedFile, SkillSummary, Teacher } from './types'

type ActivePage = 'ai' | 'history' | 'twin'

const activePage = ref<ActivePage>('ai')
const mobileMenuOpen = ref(false)
const skills = ref<SkillSummary[]>([])
const teachers = ref<Teacher[]>([])
const files = ref<GeneratedFile[]>([])
const history = ref<ConversationRecord[]>([])
const loading = ref(true)
const error = ref('')

const navItems = [
  { key: 'ai' as const, label: 'AI老师', icon: Bot },
  { key: 'history' as const, label: '历史对话', icon: Clock3 },
  { key: 'twin' as const, label: '数字孪生', icon: BrainCircuit }
]

const activeTitle = computed(() => navItems.find((item) => item.key === activePage.value)?.label ?? 'AI老师')

function setActivePage(page: ActivePage) {
  activePage.value = page
  mobileMenuOpen.value = false
}

function addHistory(record: ConversationRecord) {
  history.value = [record, ...history.value].slice(0, 50)
  localStorage.setItem('junior-ai-history', JSON.stringify(history.value))
}

function clearHistory() {
  history.value = []
  localStorage.removeItem('junior-ai-history')
}

function deleteHistory(recordId: string) {
  history.value = history.value.filter((record) => record.id !== recordId)
  localStorage.setItem('junior-ai-history', JSON.stringify(history.value))
}

async function refreshFiles() {
  files.value = await fetchGeneratedFiles()
}

async function loadPage() {
  loading.value = true
  error.value = ''
  try {
    const [skillData, teacherData, fileData] = await Promise.all([
      fetchSkills(),
      fetchTeachers(),
      fetchGeneratedFiles()
    ])
    skills.value = skillData
    teachers.value = teacherData
    files.value = fileData
    const stored = localStorage.getItem('junior-ai-history')
    history.value = stored ? JSON.parse(stored) : []
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : '加载失败，请确认后端已启动。'
  } finally {
    loading.value = false
  }
}

onMounted(loadPage)
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar" :class="{ open: mobileMenuOpen }">
      <div class="brand">
        <div class="brand-icon">
          <GraduationCap :size="26" />
        </div>
        <div>
          <span>Junior AI Study</span>
          <strong>初中学习智能体</strong>
        </div>
        <button class="icon-button mobile-only" type="button" aria-label="关闭菜单" @click="mobileMenuOpen = false">
          <X :size="20" />
        </button>
      </div>

      <nav class="nav-list">
        <button
          v-for="item in navItems"
          :key="item.key"
          class="nav-button"
          :class="{ active: activePage === item.key }"
          type="button"
          @click="setActivePage(item.key)"
        >
          <component :is="item.icon" :size="20" />
          <span>{{ item.label }}</span>
        </button>
      </nav>
    </aside>

    <main class="main-panel">
      <header class="topbar">
        <button class="icon-button mobile-only" type="button" aria-label="打开菜单" @click="mobileMenuOpen = true">
          <Menu :size="20" />
        </button>
        <h1>{{ activeTitle }}</h1>
      </header>

      <section v-if="loading" class="state-card">正在加载后端数据...</section>
      <section v-else-if="error" class="state-card error">{{ error }}</section>

      <AiTeacherView
        v-else-if="activePage === 'ai'"
        :skills="skills"
        :teachers="teachers"
        @history-created="addHistory"
        @files-changed="refreshFiles"
      />

      <HistoryView
        v-else-if="activePage === 'history'"
        :history="history"
        :files="files"
        @clear-history="clearHistory"
        @delete-history="deleteHistory"
      />

      <DigitalTwinView v-else />
    </main>
  </div>
</template>
