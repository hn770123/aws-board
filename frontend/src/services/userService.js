/**
 * ユーザーサービス
 * 
 * ユーザー管理のCRUD APIを提供する。
 */

import api from './api'

/**
 * ユーザーサービスオブジェクト
 */
const userService = {
  /**
   * 全ユーザーを取得する
   * 
   * @returns {Promise<Array>} ユーザーリスト
   */
  async getUsers() {
    const response = await api.get('/users/')
    return response.data
  },

  /**
   * 特定のユーザーを取得する
   * 
   * @param {string} userId - ユーザーID
   * @returns {Promise<Object>} ユーザー情報
   */
  async getUser(userId) {
    const response = await api.get(`/users/${userId}`)
    return response.data
  },

  /**
   * 新規ユーザーを作成する
   * 
   * @param {Object} userData - ユーザー作成データ
   * @returns {Promise<Object>} 作成されたユーザー情報
   */
  async createUser(userData) {
    const response = await api.post('/users/', userData)
    return response.data
  },

  /**
   * ユーザー情報を更新する
   * 
   * @param {string} userId - ユーザーID
   * @param {Object} userData - 更新データ
   * @returns {Promise<Object>} 更新後のユーザー情報
   */
  async updateUser(userId, userData) {
    const response = await api.put(`/users/${userId}`, userData)
    return response.data
  },

  /**
   * ユーザーを削除する
   * 
   * @param {string} userId - ユーザーID
   * @returns {Promise<void>}
   */
  async deleteUser(userId) {
    await api.delete(`/users/${userId}`)
  },
}

export default userService
