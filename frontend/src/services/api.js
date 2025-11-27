/**
 * API通信サービス
 * 
 * バックエンドAPIとの通信を行うaxiosインスタンスを提供する。
 * 認証トークンの自動付与とエラーハンドリングを行う。
 */

import axios from 'axios'

// APIベースURL（環境変数から取得）
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * axiosインスタンス
 * 
 * 認証ヘッダーの自動付与と共通設定を持つインスタンス。
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// リクエストインターセプター（認証トークンの自動付与）
api.interceptors.request.use(
  (config) => {
    // ローカルストレージからトークンを取得
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// レスポンスインターセプター（認証エラーのハンドリング）
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401エラーの場合はログアウト処理
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
