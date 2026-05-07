<script setup lang="ts">
import { computed } from 'vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'

const props = defineProps<{
  content: string
}>()

const previewId = computed(() => `md-preview-${Math.random().toString(16).slice(2)}`)
</script>

<template>
  <MdPreview
    class="markdown-content"
    :id="previewId"
    :model-value="content"
    preview-theme="github"
    code-theme="github"
    language="zh-CN"
    :show-code-row-number="false"
    :no-katex="false"
    :no-mermaid="false"
  />
</template>
