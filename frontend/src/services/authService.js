/**
 * 認証サービス
 * 
 * ログイン・ログアウト・ユーザー情報取得のAPIを提供する。
 */

import api from './api'

/**
 * 認証サービスオブジェクト
 */
const authService = {
  /**
   * ログイン処理
   * 
   * @param {string} username - ユーザー名
   * @param {string} password - パスワード
   * @returns {Promise<Object>} トークン情報
   */
  async login(username, password) {
    const response = await api.post('/auth/login', { username, password })
    return response.data
  },

  /**
   * 現在のユーザー情報を取得する
   * 
   * @returns {Promise<Object>} ユーザー情報
   */
  async getCurrentUser() {
    const response = await api.get('/auth/me')
    return response.data
  },

  /**
   * ログアウト処理
   * 
   * ローカルストレージからトークンとユーザー情報を削除する。
   */
  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },
}

export default authService
