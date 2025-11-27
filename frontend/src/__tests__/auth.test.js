/**
 * 認証ストアのテスト
 * 
 * Piniaを使用した認証状態管理のテスト。
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

// モックの設定
vi.mock('@/services/authService', () => ({
  default: {
    login: vi.fn(),
    getCurrentUser: vi.fn(),
    logout: vi.fn(() => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }),
  },
}))

describe('認証ストア', () => {
  beforeEach(() => {
    // 各テスト前にPiniaを初期化
    setActivePinia(createPinia())
    // localStorageをクリア
    localStorage.clear()
  })

  it('初期状態が正しいこと', () => {
    const store = useAuthStore()
    
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(store.isAdmin).toBe(false)
  })

  it('トークンがある場合は認証済みと判定されること', () => {
    localStorage.setItem('token', 'test-token')
    const store = useAuthStore()
    
    expect(store.isAuthenticated).toBe(true)
  })

  it('管理者ユーザーの場合はisAdminがtrueになること', () => {
    const adminUser = { user_id: '1', username: 'admin', role: 'admin' }
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', JSON.stringify(adminUser))
    
    const store = useAuthStore()
    
    expect(store.isAdmin).toBe(true)
  })

  it('一般ユーザーの場合はisAdminがfalseになること', () => {
    const normalUser = { user_id: '2', username: 'user', role: 'user' }
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', JSON.stringify(normalUser))
    
    const store = useAuthStore()
    
    expect(store.isAdmin).toBe(false)
  })

  it('ログアウトでストアの状態がクリアされること', () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', JSON.stringify({ user_id: '1' }))
    
    const store = useAuthStore()
    store.logout()
    
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
  })
})
