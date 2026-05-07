import type { ChatMessage, ChatResponse, GeneratedFile, SkillSummary, Teacher } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? defaultApiBaseUrl()

function defaultApiBaseUrl(): string {
  return ''
}

function apiUrl(path: string): string {
  return `${API_BASE_URL}${path}`
}

async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(apiUrl(url), options)
  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `请求失败：${response.status}`)
  }
  return response.json() as Promise<T>
}

export function fetchSkills(): Promise<SkillSummary[]> {
  return requestJson<SkillSummary[]>('/api/skills')
}

export function fetchTeachers(): Promise<Teacher[]> {
  return requestJson<Teacher[]>('/api/teachers')
}

export function fetchGeneratedFiles(): Promise<GeneratedFile[]> {
  return requestJson<GeneratedFile[]>('/api/generated-files')
}

export async function streamChat(
  payload: {
    question: string
    teacher_id: string
    skill_ids: string[]
    history: ChatMessage[]
    generate_file?: boolean
  },
  handlers: {
    onReady?: () => void
    onChunk: (content: string) => void | Promise<void>
    onDone: (response: ChatResponse) => void
  }
): Promise<void> {
  const response = await fetch(apiUrl('/api/chat/stream'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
      'Cache-Control': 'no-cache'
    },
    body: JSON.stringify({ ...payload, generate_file: payload.generate_file ?? true })
  })

  if (!response.ok || !response.body) {
    const message = await response.text()
    throw new Error(message || `请求失败：${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const frames = buffer.split('\n\n')
    buffer = frames.pop() ?? ''

    for (const frame of frames) {
      if (!frame.startsWith('data: ')) continue
      const data = JSON.parse(frame.slice(6))

      if (data.ready) {
        handlers.onReady?.()
        continue
      }

      if (data.done) {
        handlers.onDone(data as ChatResponse)
        continue
      }

      if (data.content) {
        await handlers.onChunk(data.content)
      }
    }
  }
}

export function generatedFileUrl(fileId: string): string {
  return apiUrl(`/api/generated-files/${encodeURIComponent(fileId)}`)
}
