import { useState, useEffect, useRef, useCallback } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import {
  getConversations, createConversation, deleteConversation,
  getMessages, sendMessageStream
} from '../api/chat.js'
import Sidebar from '../components/Sidebar.jsx'
import ChatMessage from '../components/ChatMessage.jsx'
import ChatInput from '../components/ChatInput.jsx'
import './ChatPage.css'

export default function ChatPage() {
  const { user, logout } = useAuth()

  const [conversations, setConversations] = useState([])
  const [activeConvId, setActiveConvId] = useState(null)
  const [messages, setMessages] = useState([])
  const [streaming, setStreaming] = useState(false)
  const [thinking, setThinking] = useState(false)
  const [streamText, setStreamText] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const messagesEndRef = useRef(null)
  const abortRef = useRef(null)

  // 加载对话列表
  const loadConversations = useCallback(async () => {
    try {
      const data = await getConversations()
      setConversations(data)
    } catch (err) {
      console.error('加载对话失败:', err)
    }
  }, [])

  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  // 加载消息
  useEffect(() => {
    if (!activeConvId) {
      setMessages([])
      return
    }
    async function load() {
      try {
        const data = await getMessages(activeConvId)
        setMessages(data)
      } catch (err) {
        console.error('加载消息失败:', err)
      }
    }
    load()
  }, [activeConvId])

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamText])

  // 新建对话
  const handleNewChat = async () => {
    try {
      const conv = await createConversation('新对话')
      setConversations(prev => [conv, ...prev])
      setActiveConvId(conv.id)
      setMessages([])
    } catch (err) {
      console.error('创建对话失败:', err)
    }
  }

  // 删除对话
  const handleDeleteConversation = async (id) => {
    try {
      await deleteConversation(id)
      setConversations(prev => prev.filter(c => c.id !== id))
      if (activeConvId === id) {
        setActiveConvId(null)
        setMessages([])
      }
    } catch (err) {
      console.error('删除对话失败:', err)
    }
  }

  // 发送消息
  const handleSend = async (text) => {
    if (!text.trim() || streaming) return

    let convId = activeConvId

    // 如果没有活跃对话，先创建一个
    if (!convId) {
      try {
        const conv = await createConversation(text.slice(0, 50))
        setConversations(prev => [conv, ...prev])
        convId = conv.id
        setActiveConvId(convId)
      } catch (err) {
        console.error('创建对话失败:', err)
        return
      }
    }

    // 添加用户消息到 UI
    const userMsg = { id: Date.now(), role: 'user', content: text, created_at: new Date().toLocaleString() }
    setMessages(prev => [...prev, userMsg])
    setStreaming(true)
    setThinking(true)
    setStreamText('')

    let fullResponse = ''

    abortRef.current = sendMessageStream(
      convId,
      text,
      // onChunk
      (chunk) => {
        setThinking(false)
        fullResponse += chunk
        setStreamText(fullResponse)
      },
      // onDone
      () => {
        if (fullResponse) {
          setMessages(prev => [
            ...prev,
            { id: Date.now() + 1, role: 'assistant', content: fullResponse.trim(), created_at: new Date().toLocaleString() }
          ])
        }
        setStreamText('')
        setStreaming(false)
        setThinking(false)
        loadConversations() // 刷新对话列表（标题可能更新了）
      },
      // onError
      (errMsg) => {
        setMessages(prev => [
          ...prev,
          { id: Date.now() + 2, role: 'assistant', content: `⚠️ 请求出错: ${errMsg}`, created_at: new Date().toLocaleString() }
        ])
        setStreamText('')
        setStreaming(false)
        setThinking(false)
      }
    )
  }

  // 停止生成
  const handleStop = () => {
    abortRef.current?.abort()
    if (streamText) {
      setMessages(prev => [
        ...prev,
        { id: Date.now(), role: 'assistant', content: streamText.trim() + '\n\n*(已停止生成)*', created_at: new Date().toLocaleString() }
      ])
    }
    setStreamText('')
    setStreaming(false)
    setThinking(false)
  }

  return (
    <div className="chat-page">
      <Sidebar
        conversations={conversations}
        activeId={activeConvId}
        onSelect={setActiveConvId}
        onNew={handleNewChat}
        onDelete={handleDeleteConversation}
        user={user}
        onLogout={logout}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />

      <main className={`chat-main ${sidebarOpen ? '' : 'expanded'}`}>
        {/* 顶部栏 */}
        <header className="chat-header">
          <button className="menu-btn" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="切换侧边栏">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </button>
          <h2 className="chat-header-title">
            {activeConvId
              ? (conversations.find(c => c.id === activeConvId)?.title || '对话')
              : '智扫通 · 智能客服'
            }
          </h2>
        </header>

        {/* 消息区域 */}
        <div className="chat-messages">
          {messages.length === 0 && !streaming && (
            <div className="chat-welcome">
              <div className="welcome-icon">
                <svg width="48" height="48" viewBox="0 0 40 40" fill="none">
                  <rect width="40" height="40" rx="12" fill="url(#wg)" />
                  <path d="M12 20C12 15.58 15.58 12 20 12C24.42 12 28 15.58 28 20C28 24.42 24.42 28 20 28" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
                  <circle cx="20" cy="20" r="3" fill="white" />
                  <path d="M20 28L16 32" stroke="white" strokeWidth="2" strokeLinecap="round" />
                  <path d="M20 28L24 32" stroke="white" strokeWidth="2" strokeLinecap="round" />
                  <defs><linearGradient id="wg" x1="0" y1="0" x2="40" y2="40"><stop stopColor="#6C63FF" /><stop offset="1" stopColor="#4ECDC4" /></linearGradient></defs>
                </svg>
              </div>
              <h3>你好，{user?.username}！</h3>
              <p>我是智扫通智能客服，可以为你解答扫地机器人 & 扫拖一体机器人的各类问题。</p>
              <div className="welcome-suggestions">
                <button onClick={() => handleSend('扫地机器人回充经常失败怎么办？')}>🔧 故障排查</button>
                <button onClick={() => handleSend('小户型适合什么样的扫地机器人？')}>🏠 选购指南</button>
                <button onClick={() => handleSend('扫地机器人的滤网多久需要更换？')}>🔄 维护保养</button>
                <button onClick={() => handleSend('给我生成我的使用报告')}>📊 使用报告</button>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}

          {/* AI 思考中指示器 */}
          {thinking && (
            <div className="thinking-indicator">
              <div className="thinking-avatar">
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <circle cx="9" cy="9" r="5" stroke="currentColor" strokeWidth="1.5" />
                  <circle cx="9" cy="9" r="2" fill="currentColor" />
                  <path d="M9 14l-2 3M9 14l2 3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
                </svg>
              </div>
              <div className="thinking-content">
                <span className="thinking-label">智扫通</span>
                <div className="thinking-dots">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="thinking-text">思考中</span>
                </div>
              </div>
            </div>
          )}

          {/* 流式输出的消息 */}
          {streaming && streamText && (
            <ChatMessage
              message={{ role: 'assistant', content: streamText }}
              isStreaming
            />
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <ChatInput
          onSend={handleSend}
          onStop={handleStop}
          disabled={false}
          streaming={streaming}
        />
      </main>
    </div>
  )
}
