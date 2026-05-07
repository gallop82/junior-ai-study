<script setup lang="ts">
import { computed, inject, ref, type Ref } from 'vue'
import { ArrowLeft, Trash2 } from 'lucide-vue-next'
import MarkdownContent from '../components/MarkdownContent.vue'
import type { ConversationRecord, GeneratedFile } from '../types'

const history = inject<Ref<ConversationRecord[]>>('history', ref([]))
const files = inject<Ref<GeneratedFile[]>>('files', ref([]))
const deleteHistoryFn = inject<(id: string) => void>('deleteHistory', () => {})

const openedRecord = ref<ConversationRecord | null>(null)

const groupedHistory = computed(() => {
  const groups = new Map<string, ConversationRecord[]>()
  for (const record of history.value) {
    const list = groups.get(record.skillName) ?? []
    list.push(record)
    groups.set(record.skillName, list)
  }
  return [...groups.entries()].map(([skillName, records]) => ({ skillName, records }))
})

function openRecord(record: ConversationRecord) {
  openedRecord.value = record
}

function closeRecord() {
  openedRecord.value = null
}

function deleteRecord(record: ConversationRecord) {
  if (openedRecord.value?.id === record.id) openedRecord.value = null
  deleteHistoryFn(record.id)
}
</script>

<template>
  <section class="page-section history-layout">
    <template v-if="!openedRecord">
      <div class="page-heading inline">
        <div>
          <h2>历史对话</h2>
          <p>按技能分类保存，点击开始文字查看完整内容；每条会话都可以单独删除。</p>
        </div>
      </div>

      <div class="history-groups">
        <section v-for="group in groupedHistory" :key="group.skillName" class="history-group">
          <h3>{{ group.skillName }}</h3>
          <div class="history-list">
            <div v-for="record in group.records" :key="record.id" class="history-row-wrap">
              <button class="history-row" type="button" @click="openRecord(record)">
                <span>{{ record.title }}</span>
                <time>{{ new Date(record.createdAt).toLocaleString() }}</time>
              </button>
              <button class="delete-row-button" type="button" aria-label="删除会话" @click="deleteRecord(record)">
                <Trash2 :size="16" />
              </button>
            </div>
          </div>
        </section>
        <article v-if="!history.length" class="empty-card">还没有历史对话。先到 AI老师 里选择技能并提问。</article>
      </div>
    </template>

    <template v-else>
      <div class="history-detail-head">
        <button class="round-icon-button" type="button" aria-label="返回历史列表" @click="closeRecord">
          <ArrowLeft :size="20" />
        </button>
        <div>
          <h2>{{ openedRecord.title }}</h2>
          <p>{{ openedRecord.skillName }} · {{ new Date(openedRecord.createdAt).toLocaleString() }}</p>
        </div>
        <button class="delete-detail-button" type="button" @click="deleteRecord(openedRecord)">
          <Trash2 :size="16" />
          删除
        </button>
      </div>

      <div class="history-detail">
        <article v-for="(message, index) in openedRecord.messages" :key="index" class="message" :class="message.role">
          <MarkdownContent :content="message.content" />
        </article>
      </div>
    </template>
  </section>
</template>
