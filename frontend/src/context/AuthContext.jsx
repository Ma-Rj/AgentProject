import { createContext, useContext, useState, useEffect } from 'react'
import { getMe } from '../api/auth'
import { getToken, clearTokens } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function checkAuth() {
      const token = getToken()
      if (!token) {
        setLoading(false)
        return
      }
      try {
        const userData = await getMe()
        setUser(userData)
      } catch {
        clearTokens()
      } finally {
        setLoading(false)
      }
    }
    checkAuth()
  }, [])

  const logout = () => {
    clearTokens()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, setUser, loading, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
