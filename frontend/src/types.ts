export interface SkillSummary {
  id: string
  name: string
  subject: string | null
  description: string
}

export interface Teacher {
  id: string
  name: string
  description: string
  wechat_account_id: string | null
  is_connected: boolean
}

export interface WechatArticle {
  id: number
  account_id: string | null
  title: string
  url: string | null
  summary: string | null
  content: string | null
  published_at: string | null
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface GeneratedFile {
  id: string
  name: string
  path: string
  created_at: string
}

export interface ChatResponse {
  answer: string
  teacher: Teacher
  used_skills: SkillSummary[]
  articles: WechatArticle[]
  files: GeneratedFile[]
}

export interface ConversationRecord {
  id: string
  skillId: string
  skillName: string
  teacherName: string
  title: string
  messages: ChatMessage[]
  createdAt: string
}
