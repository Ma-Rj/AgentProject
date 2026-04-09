/**
 * 聊天 & 对话管理 API
 */
import { request, getToken } from './client'

/* ========== 对话管理 ========== */

export async function getConversations() {
  const res = await request('/conversations')
  return res.json()
}

export async function createConversation(title = '新对话') {
  const res = await request('/conversations', {
    method: 'POST',
    body: JSON.stringify({ title }),
  })
  return res.json()
}

export async function deleteConversation(id) {
  await request(`/conversations/${id}`, { method: 'DELETE' })
}

export async function renameConversation(id, title) {
  const res = await request(`/conversations/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ title }),
  })
  return res.json()
}

export async function getMessages(conversationId) {
  const res = await request(`/conversations/${conversationId}/messages`)
  return res.json()
}

/* ========== 聊天（SSE 流式） ========== */

/**
 * 发送消息并以 SSE 形式读取流式回复
 * @param {number} conversationId
 * @param {string} message
 * @param {function} onChunk  每收到一个 chunk 调用 (text)
 * @param {function} onDone   流结束时调用
 * @param {function} onError  出错时调用 (errMsg)
 * @returns {AbortController} 可用于取消请求
 */
export function sendMessageStream(conversationId, message, onChunk, onDone, onError) {
  const controller = new AbortController()
  const token = getToken()

  fetch(`/api/chat/${conversationId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ message }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: '请求失败' }))
        onError?.(err.detail || `HTTP ${res.status}`)
        return
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data:')) {
            const dataStr = line.slice(5).trim()
            if (!dataStr) continue
            try {
              const data = JSON.parse(dataStr)
              if (data.content) {
                onChunk?.(data.content)
              }
              if (data.status === 'completed') {
                onDone?.()
              }
              if (data.error) {
                onError?.(data.error)
              }
            } catch {
              // 非 JSON 行，忽略
            }
          }
        }
      }
      onDone?.()
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        onError?.(err.message)
      }
    })

  return controller
}
