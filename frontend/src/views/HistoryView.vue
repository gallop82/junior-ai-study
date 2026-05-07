<script setup lang="ts">
import { computed, inject, ref, type Ref } from 'vue'
import { ArrowLeft, Clock3, MessageSquareText, Sparkles, Trash2, X } from 'lucide-vue-next'
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

function deleteRecord(record: ConversationRecord, e?: Event) {
  e?.stopPropagation()
  if (openedRecord.value?.id === record.id) openedRecord.value = null
  deleteHistoryFn(record.id)
}
</script>

<template>
  <section class="page-section history-page">
    <!-- list view -->
    <template v-if="!openedRecord">
      <div class="history-header">
        <h2>历史对话</h2>
        <p>按技能分类保存，点击查看完整内容。</p>
      </div>

      <div v-if="!history.length" class="history-empty">
        <MessageSquareText :size="40" />
        <p>还没有历史对话</p>
        <span>先到 AI老师 里选择技能并提问</span>
      </div>

      <div v-else class="history-groups">
        <section v-for="group in groupedHistory" :key="group.skillName" class="history-group">
          <div class="history-group-head">
            <Sparkles :size="16" />
            <h3>{{ group.skillName }}</h3>
            <span class="history-group-count">{{ group.records.length }}</span>
          </div>
          <div class="history-list">
            <button
              v-for="record in group.records"
              :key="record.id"
              class="history-item"
              type="button"
              @click="openRecord(record)"
            >
              <div class="history-item-body">
                <span class="history-item-title">{{ record.title }}</span>
                <div class="history-item-meta">
                  <time>
                    <Clock3 :size="12" />
                    {{ new Date(record.createdAt).toLocaleString() }}
                  </time>
                  <button
                    class="history-delete-btn"
                    type="button"
                    aria-label="删除会话"
                    @click="deleteRecord(record, $event)"
                  >
                    <Trash2 :size="14" />
                  </button>
                </div>
              </div>
            </button>
          </div>
        </section>
      </div>
    </template>

    <!-- detail view -->
    <template v-else>
      <div class="history-detail-bar">
        <button class="round-icon-button" type="button" aria-label="返回" @click="closeRecord">
          <ArrowLeft :size="20" />
        </button>
        <div class="history-detail-info">
          <h2>{{ openedRecord.title }}</h2>
          <p>{{ openedRecord.skillName }} · {{ new Date(openedRecord.createdAt).toLocaleString() }}</p>
        </div>
        <button class="history-delete-btn detail" type="button" aria-label="删除" @click="deleteRecord(openedRecord)">
          <Trash2 :size="16" />
        </button>
      </div>

      <div class="history-detail-messages">
        <article v-for="(message, index) in openedRecord.messages" :key="index" class="message" :class="message.role">
          <MarkdownContent :content="message.content" />
        </article>
      </div>
    </template>
  </section>
</template>
