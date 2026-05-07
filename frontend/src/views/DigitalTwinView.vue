<script setup lang="ts">
import { BrainCircuit, Database, Radio } from 'lucide-vue-next'
</script>

<template>
  <section class="page-section twin-page">
    <div class="page-heading">
      <span>数字孪生</span>
      <h2>微信公众号内容接入后，在这里管理老师孪生体</h2>
      <p>这一部分暂不开发功能，只保留产品入口和状态说明。</p>
    </div>

    <div class="twin-board">
      <article>
        <BrainCircuit :size="28" />
        <strong>老师画像</strong>
        <p>后续读取公众号文章、讲义和蒸馏结果，形成可选择的老师身份。</p>
      </article>
      <article>
        <Database :size="28" />
        <strong>内容来源</strong>
        <p>当前后端已经预留 SQLite 微信文章表和检索入口。</p>
      </article>
      <article>
        <Radio :size="28" />
        <strong>当前状态</strong>
        <p>待接入微信公众号真实内容后启用。</p>
      </article>
    </div>
  </section>
</template>

