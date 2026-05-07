import { createRouter, createWebHistory } from 'vue-router'
import AiTeacherView from './views/AiTeacherView.vue'
import HistoryView from './views/HistoryView.vue'
import DigitalTwinView from './views/DigitalTwinView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'ai', component: AiTeacherView },
    { path: '/history', name: 'history', component: HistoryView },
    { path: '/twin', name: 'twin', component: DigitalTwinView },
  ],
})
