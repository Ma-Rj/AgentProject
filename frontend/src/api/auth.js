/**
 * 认证相关 API
 */
import { request, setTokens } from './client'

export async function register(username, email, password, city) {
  const res = await request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, email, password, city }),
  })
  const data = await res.json()
  setTokens(data.access_token, data.refresh_token)
  return data
}

export async function login(username, password) {
  const res = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
  const data = await res.json()
  setTokens(data.access_token, data.refresh_token)
  return data
}

export async function getMe() {
  const res = await request('/auth/me')
  return res.json()
}
