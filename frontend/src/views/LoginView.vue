<!--
  ログイン画面

  ユーザー名とパスワードを入力してログインを行う。
-->
<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">掲示板システム</h1>
      <h2 class="login-subtitle">ログイン</h2>

      <!-- エラーメッセージ -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <!-- ログインフォーム -->
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">ユーザー名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="ユーザー名を入力"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="password">パスワード</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="パスワードを入力"
            required
            :disabled="loading"
          />
        </div>

        <button type="submit" class="login-button" :disabled="loading">
          {{ loading ? 'ログイン中...' : 'ログイン' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
/**
 * ログインビューコンポーネント
 * 
 * ユーザー認証を行うログイン画面。
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// ルーター
const router = useRouter()

// 認証ストア
const authStore = useAuthStore()

// フォームデータ
const username = ref('')
const password = ref('')

// ローディング状態
const loading = ref(false)

// エラーメッセージ
const error = ref(null)

/**
 * ログイン処理
 */
async function handleLogin() {
  loading.value = true
  error.value = null

  const success = await authStore.login(username.value, password.value)

  if (success) {
    // ログイン成功時は掲示板画面へ
    router.push({ name: 'Board' })
  } else {
    // エラーメッセージを表示
    error.value = authStore.error
  }

  loading.value = false
}
</script>

<style scoped>
/* ログインコンテナ */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* ログインカード */
.login-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

/* タイトル */
.login-title {
  text-align: center;
  color: #333;
  margin-bottom: 0.5rem;
}

.login-subtitle {
  text-align: center;
  color: #666;
  font-weight: normal;
  margin-bottom: 1.5rem;
}

/* フォーム */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #333;
}

.form-group input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #4a90d9;
}

/* ログインボタン */
.login-button {
  padding: 0.75rem;
  background-color: #4a90d9;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.login-button:hover:not(:disabled) {
  background-color: #357abd;
}

.login-button:disabled {
  background-color: #a0c4e8;
  cursor: not-allowed;
}

/* エラーメッセージ */
.error-message {
  background-color: #ffe6e6;
  color: #cc0000;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  text-align: center;
}
</style>
