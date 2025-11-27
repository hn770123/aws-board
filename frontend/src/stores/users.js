/**
 * ユーザーストア
 * 
 * Piniaを使用したユーザー管理状態。
 * ユーザーリストとCRUD操作を管理する（管理者機能）。
 */

import { defineStore } from 'pinia'
import userService from '@/services/userService'

/**
 * ユーザーストア
 */
export const useUserStore = defineStore('users', {
  state: () => ({
    // ユーザーリスト
    users: [],
    // ローディング状態
    loading: false,
    // エラーメッセージ
    error: null,
  }),

  actions: {
    /**
     * ユーザー一覧を取得する
     */
    async fetchUsers() {
      this.loading = true
      this.error = null

      try {
        this.users = await userService.getUsers()
      } catch (err) {
        this.error = err.response?.data?.detail || 'ユーザーの取得に失敗しました'
      } finally {
        this.loading = false
      }
    },

    /**
     * ユーザーを作成する
     * 
     * @param {Object} userData - ユーザーデータ
     */
    async createUser(userData) {
      this.loading = true
      this.error = null

      try {
        const user = await userService.createUser(userData)
        this.users.push(user)
        return user
      } catch (err) {
        this.error = err.response?.data?.detail || 'ユーザーの作成に失敗しました'
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * ユーザーを更新する
     * 
     * @param {string} userId - ユーザーID
     * @param {Object} userData - 更新データ
     */
    async updateUser(userId, userData) {
      this.loading = true
      this.error = null

      try {
        const updatedUser = await userService.updateUser(userId, userData)
        // リスト内の該当ユーザーを更新
        const index = this.users.findIndex((u) => u.user_id === userId)
        if (index !== -1) {
          this.users[index] = updatedUser
        }
        return updatedUser
      } catch (err) {
        this.error = err.response?.data?.detail || 'ユーザーの更新に失敗しました'
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * ユーザーを削除する
     * 
     * @param {string} userId - ユーザーID
     */
    async deleteUser(userId) {
      this.loading = true
      this.error = null

      try {
        await userService.deleteUser(userId)
        // リストから削除
        this.users = this.users.filter((u) => u.user_id !== userId)
      } catch (err) {
        this.error = err.response?.data?.detail || 'ユーザーの削除に失敗しました'
        throw err
      } finally {
        this.loading = false
      }
    },
  },
})
