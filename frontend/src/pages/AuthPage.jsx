import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { login, register, getMe } from '../api/auth.js'
import './AuthPage.css'

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [form, setForm] = useState({ username: '', email: '', password: '', city: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { setUser, user } = useAuth()
  const navigate = useNavigate()

  // 如果已登录，直接跳到聊天页
  if (user) {
    navigate('/', { replace: true })
    return null
  }

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        await login(form.username, form.password)
      } else {
        if (!form.email) { setError('请输入邮箱'); setLoading(false); return }
        await register(form.username, form.email, form.password, form.city || null)
      }
      const userData = await getMe()
      setUser(userData)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.message || '操作失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      {/* 背景装饰 */}
      <div className="auth-bg">
        <div className="auth-bg-orb auth-bg-orb-1" />
        <div className="auth-bg-orb auth-bg-orb-2" />
        <div className="auth-bg-orb auth-bg-orb-3" />
      </div>

      <div className="auth-container">
        {/* 品牌区 */}
        <div className="auth-brand">
          <div className="auth-logo">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
              <rect width="40" height="40" rx="12" fill="url(#logo-grad)" />
              <path d="M12 20C12 15.58 15.58 12 20 12C24.42 12 28 15.58 28 20C28 24.42 24.42 28 20 28" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
              <circle cx="20" cy="20" r="3" fill="white" />
              <path d="M20 28L16 32" stroke="white" strokeWidth="2" strokeLinecap="round" />
              <path d="M20 28L24 32" stroke="white" strokeWidth="2" strokeLinecap="round" />
              <defs>
                <linearGradient id="logo-grad" x1="0" y1="0" x2="40" y2="40">
                  <stop stopColor="#6C63FF" />
                  <stop offset="1" stopColor="#4ECDC4" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 className="auth-title">智扫通</h1>
          <p className="auth-subtitle">智能扫地机器人客服系统</p>
        </div>

        {/* 表单卡片 */}
        <div className="auth-card glass">
          {/* Tab 切换 */}
          <div className="auth-tabs">
            <button
              className={`auth-tab ${isLogin ? 'active' : ''}`}
              onClick={() => { setIsLogin(true); setError('') }}
            >
              登录
            </button>
            <button
              className={`auth-tab ${!isLogin ? 'active' : ''}`}
              onClick={() => { setIsLogin(false); setError('') }}
            >
              注册
            </button>
            <div className={`auth-tab-indicator ${isLogin ? 'left' : 'right'}`} />
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="username">用户名</label>
              <input
                id="username"
                name="username"
                type="text"
                placeholder="请输入用户名"
                value={form.username}
                onChange={handleChange}
                required
                autoComplete="username"
              />
            </div>

            {!isLogin && (
              <div className="form-group animate-fadeIn">
                <label htmlFor="email">邮箱</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="请输入邮箱"
                  value={form.email}
                  onChange={handleChange}
                  autoComplete="email"
                />
              </div>
            )}

            <div className="form-group">
              <label htmlFor="password">密码</label>
              <input
                id="password"
                name="password"
                type="password"
                placeholder="请输入密码"
                value={form.password}
                onChange={handleChange}
                required
                minLength={6}
                autoComplete={isLogin ? 'current-password' : 'new-password'}
              />
            </div>

            {!isLogin && (
              <div className="form-group animate-fadeIn">
                <label htmlFor="city">所在城市 <span className="optional">(选填)</span></label>
                <input
                  id="city"
                  name="city"
                  type="text"
                  placeholder="如：深圳"
                  value={form.city}
                  onChange={handleChange}
                />
              </div>
            )}

            {error && <div className="form-error">{error}</div>}

            <button className="auth-submit" type="submit" disabled={loading}>
              {loading ? (
                <span className="btn-loading"><span className="loading-spinner small" /> 处理中...</span>
              ) : (
                isLogin ? '登 录' : '注 册'
              )}
            </button>
          </form>
        </div>

        <p className="auth-footer">基于 ReAct Agent + RAG 构建的智能客服系统</p>
      </div>
    </div>
  )
}
