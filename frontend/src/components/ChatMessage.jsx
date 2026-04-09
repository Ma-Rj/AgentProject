import ReactMarkdown from 'react-markdown'
import './ChatMessage.css'

export default function ChatMessage({ message, isStreaming = false }) {
  const isUser = message.role === 'user'

  return (
    <div className={`message ${isUser ? 'message-user' : 'message-assistant'} ${isStreaming ? 'streaming' : ''}`}>
      {/* 头像 */}
      <div className={`message-avatar ${isUser ? 'avatar-user' : 'avatar-bot'}`}>
        {isUser ? (
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <circle cx="9" cy="6" r="3" stroke="currentColor" strokeWidth="1.5" />
            <path d="M3 16c0-3.31 2.69-6 6-6s6 2.69 6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <circle cx="9" cy="9" r="5" stroke="currentColor" strokeWidth="1.5" />
            <circle cx="9" cy="9" r="2" fill="currentColor" />
            <path d="M9 14l-2 3M9 14l2 3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
          </svg>
        )}
      </div>

      {/* 内容 */}
      <div className="message-content">
        <div className="message-role">{isUser ? '你' : '智扫通'}</div>
        <div className="message-body">
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <ReactMarkdown>{message.content}</ReactMarkdown>
          )}
          {isStreaming && <span className="cursor-blink">▌</span>}
        </div>
      </div>
    </div>
  )
}
