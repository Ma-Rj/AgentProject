import { useState, useRef, useEffect } from 'react'
import './ChatInput.css'

export default function ChatInput({ onSend, onStop, disabled, streaming }) {
  const [text, setText] = useState('')
  const textareaRef = useRef(null)

  // 自动调整 textarea 高度
  useEffect(() => {
    const el = textareaRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = Math.min(el.scrollHeight, 160) + 'px'
    }
  }, [text])

  const handleSubmit = () => {
    if (streaming) {
      onStop?.()
      return
    }
    if (!text.trim()) return
    onSend(text.trim())
    setText('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="chat-input-wrapper">
      <div className="chat-input-container">
        <textarea
          ref={textareaRef}
          className="chat-textarea"
          placeholder={disabled ? '请先新建一个对话...' : '输入你的问题... (Enter 发送，Shift+Enter 换行)'}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled || streaming}
          rows={1}
        />
        <button
          className={`send-btn ${streaming ? 'stop' : ''}`}
          onClick={handleSubmit}
          disabled={disabled && !streaming}
          aria-label={streaming ? '停止生成' : '发送'}
        >
          {streaming ? (
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <rect x="4" y="4" width="10" height="10" rx="2" fill="currentColor" />
            </svg>
          ) : (
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M3 9h12M10 4l5 5-5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          )}
        </button>
      </div>
      <p className="chat-disclaimer">智扫通 AI 可能会产生不准确的信息，请以产品说明书为准</p>
    </div>
  )
}
