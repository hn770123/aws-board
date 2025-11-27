/**
 * 認証ストア
 * 
 * Piniaを使用した認証状態管理。
 * ログイン状態、ユーザー情報、トークンを管理する。
 */

import { defineStore } from 'pinia'
import authService from '@/services/authService'

/**
 * 認証ストア
 */
export const useAuthStore = defineStore('auth', {
  state: () => ({
    // 認証トークン
    token: localStorage.getItem('token') || null,
    // ユーザー情報
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    // ローディング状態
    loading: false,
    // エラーメッセージ
    error: null,
  }),

  getters: {
    /**
     * 認証済みかどうか
     */
    isAuthenticated: (state) => !!state.token,

    /**
     * 管理者かどうか
     */
    isAdmin: (state) => state.user?.role === 'admin',

    /**
     * 現在のユーザーID
     */
    currentUserId: (state) => state.user?.user_id,
  },

  actions: {
    /**
     * ログイン処理
     * 
     * @param {string} username - ユーザー名
     * @param {string} password - パスワード
     */
    async login(username, password) {
      this.loading = true
      this.error = null

      try {
        // 認証API呼び出し
        const data = await authService.login(username, password)
        this.token = data.access_token

        // トークンをローカルストレージに保存
        localStorage.setItem('token', this.token)

        // ユーザー情報を取得
        await this.fetchUser()

        return true
      } catch (err) {
        this.error = err.response?.data?.detail || 'ログインに失敗しました'
        return false
      } finally {
        this.loading = false
      }
    },

    /**
     * ユーザー情報を取得する
     */
    async fetchUser() {
      try {
        const user = await authService.getCurrentUser()
        this.user = user
        localStorage.setItem('user', JSON.stringify(user))
      } catch (err) {
        console.error('ユーザー情報の取得に失敗しました', err)
      }
    },

    /**
     * ログアウト処理
     */
    logout() {
      this.token = null
      this.user = null
      authService.logout()
    },
  },
})
