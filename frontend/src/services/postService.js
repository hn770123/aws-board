/**
 * 投稿サービス
 * 
 * 投稿管理のCRUD APIを提供する。
 */

import api from './api'

/**
 * 投稿サービスオブジェクト
 */
const postService = {
  /**
   * 全投稿を取得する
   * 
   * @param {number} limit - 取得件数上限
   * @returns {Promise<Array>} 投稿リスト
   */
  async getPosts(limit = 100) {
    const response = await api.get('/posts/', { params: { limit } })
    return response.data
  },

  /**
   * 特定の投稿を取得する
   * 
   * @param {string} postId - 投稿ID
   * @returns {Promise<Object>} 投稿情報
   */
  async getPost(postId) {
    const response = await api.get(`/posts/${postId}`)
    return response.data
  },

  /**
   * 新規投稿を作成する
   * 
   * @param {Object} postData - 投稿作成データ
   * @returns {Promise<Object>} 作成された投稿情報
   */
  async createPost(postData) {
    const response = await api.post('/posts/', postData)
    return response.data
  },

  /**
   * 投稿を更新する
   * 
   * @param {string} postId - 投稿ID
   * @param {Object} postData - 更新データ
   * @returns {Promise<Object>} 更新後の投稿情報
   */
  async updatePost(postId, postData) {
    const response = await api.put(`/posts/${postId}`, postData)
    return response.data
  },

  /**
   * 投稿を削除する
   * 
   * @param {string} postId - 投稿ID
   * @returns {Promise<void>}
   */
  async deletePost(postId) {
    await api.delete(`/posts/${postId}`)
  },
}

export default postService
