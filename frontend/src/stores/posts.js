/**
 * 投稿ストア
 * 
 * Piniaを使用した投稿状態管理。
 * 投稿リストとCRUD操作を管理する。
 */

import { defineStore } from 'pinia'
import postService from '@/services/postService'

/**
 * 投稿ストア
 */
export const usePostStore = defineStore('posts', {
  state: () => ({
    // 投稿リスト
    posts: [],
    // ローディング状態
    loading: false,
    // エラーメッセージ
    error: null,
  }),

  actions: {
    /**
     * 投稿一覧を取得する
     */
    async fetchPosts() {
      this.loading = true
      this.error = null

      try {
        this.posts = await postService.getPosts()
      } catch (err) {
        this.error = err.response?.data?.detail || '投稿の取得に失敗しました'
      } finally {
        this.loading = false
      }
    },

    /**
     * 投稿を作成する
     * 
     * @param {Object} postData - 投稿データ
     */
    async createPost(postData) {
      this.loading = true
      this.error = null

      try {
        const post = await postService.createPost(postData)
        // リストの先頭に追加（新しい投稿が上に来るように）
        this.posts.unshift(post)
        return post
      } catch (err) {
        this.error = err.response?.data?.detail || '投稿の作成に失敗しました'
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * 投稿を更新する
     * 
     * @param {string} postId - 投稿ID
     * @param {Object} postData - 更新データ
     */
    async updatePost(postId, postData) {
      this.loading = true
      this.error = null

      try {
        const updatedPost = await postService.updatePost(postId, postData)
        // リスト内の該当投稿を更新
        const index = this.posts.findIndex((p) => p.post_id === postId)
        if (index !== -1) {
          this.posts[index] = updatedPost
        }
        return updatedPost
      } catch (err) {
        this.error = err.response?.data?.detail || '投稿の更新に失敗しました'
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * 投稿を削除する
     * 
     * @param {string} postId - 投稿ID
     */
    async deletePost(postId) {
      this.loading = true
      this.error = null

      try {
        await postService.deletePost(postId)
        // リストから削除
        this.posts = this.posts.filter((p) => p.post_id !== postId)
      } catch (err) {
        this.error = err.response?.data?.detail || '投稿の削除に失敗しました'
        throw err
      } finally {
        this.loading = false
      }
    },
  },
})
