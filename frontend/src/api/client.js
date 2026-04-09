/**
 * API 请求基础封装
 */
const BASE_URL = '/api'

/**
 * 从 localStorage 获取 token
 */
export function getToken() {
  return localStorage.getItem('access_token')
}

export function getRefreshToken() {
  return localStorage.getItem('refresh_token')
}

export function setTokens(access, refresh) {
  localStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)
}

export function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

/**
 * 通用 fetch 封装（自带 auth header + JSON 处理）
 */
export async function request(url, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const res = await fetch(`${BASE_URL}${url}`, { ...options, headers })

  // 401 -> token 过期，尝试刷新
  if (res.status === 401 && getRefreshToken()) {
    const refreshed = await tryRefreshToken()
    if (refreshed) {
      // 用新 token 重试
      headers.Authorization = `Bearer ${getToken()}`
      const retryRes = await fetch(`${BASE_URL}${url}`, { ...options, headers })
      if (!retryRes.ok) {
        const err = await retryRes.json().catch(() => ({ detail: '请求失败' }))
        throw new Error(err.detail || '请求失败')
      }
      return retryRes
    } else {
      clearTokens()
      window.location.href = '/auth'
      throw new Error('登录已过期，请重新登录')
    }
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: '请求失败' }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }

  return res
}

/**
 * 尝试刷新 Token
 */
async function tryRefreshToken() {
  try {
    const res = await fetch(`${BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: getRefreshToken() }),
    })
    if (res.ok) {
      const data = await res.json()
      setTokens(data.access_token, data.refresh_token)
      return true
    }
    return false
  } catch {
    return false
  }
}
