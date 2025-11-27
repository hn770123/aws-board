/**
 * ルーター設定
 * 
 * Vue Routerを使用したルーティング設定。
 * 認証ガードを含む。
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// ビューコンポーネントの遅延読み込み
const LoginView = () => import('@/views/LoginView.vue')
const BoardView = () => import('@/views/BoardView.vue')
const UsersView = () => import('@/views/UsersView.vue')

/**
 * ルート定義
 */
const routes = [
  {
    path: '/',
    redirect: '/board',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false },
  },
  {
    path: '/board',
    name: 'Board',
    component: BoardView,
    meta: { requiresAuth: true },
  },
  {
    path: '/users',
    name: 'Users',
    component: UsersView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
]

/**
 * ルーターインスタンス
 */
const router = createRouter({
  history: createWebHistory(),
  routes,
})

/**
 * ナビゲーションガード
 * 
 * 認証が必要なルートへのアクセスを制御する。
 */
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 認証が必要なルートの場合
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' })
    return
  }

  // 管理者権限が必要なルートの場合
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'Board' })
    return
  }

  // 認証済みでログインページにアクセスしようとした場合
  if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Board' })
    return
  }

  next()
})

export default router
