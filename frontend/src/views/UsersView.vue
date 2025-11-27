<!--
  ユーザー管理画面

  管理者がユーザーの追加・変更・削除を行う画面。
-->
<template>
  <div class="users-container">
    <!-- ヘッダー -->
    <header class="users-header">
      <h1>ユーザー管理</h1>
      <div class="header-actions">
        <router-link to="/board" class="nav-link">掲示板に戻る</router-link>
        <button @click="handleLogout" class="logout-button">ログアウト</button>
      </div>
    </header>

    <!-- ユーザー作成フォーム -->
    <section class="user-form-section">
      <h2>新規ユーザー作成</h2>
      <form @submit.prevent="handleCreateUser" class="user-form">
        <div class="form-row">
          <div class="form-group">
            <label for="username">ユーザー名</label>
            <input
              id="username"
              v-model="newUser.username"
              type="text"
              placeholder="ユーザー名"
              required
              minlength="3"
              maxlength="50"
            />
          </div>
          <div class="form-group">
            <label for="password">パスワード</label>
            <input
              id="password"
              v-model="newUser.password"
              type="password"
              placeholder="パスワード"
              required
              minlength="6"
            />
          </div>
          <div class="form-group">
            <label for="role">権限</label>
            <select id="role" v-model="newUser.role">
              <option value="user">一般ユーザー</option>
              <option value="admin">管理者</option>
            </select>
          </div>
        </div>
        <button type="submit" class="submit-button" :disabled="userStore.loading">
          {{ userStore.loading ? '作成中...' : 'ユーザーを作成' }}
        </button>
      </form>
    </section>

    <!-- エラーメッセージ -->
    <div v-if="userStore.error" class="error-message">
      {{ userStore.error }}
    </div>

    <!-- 成功メッセージ -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>

    <!-- ユーザー一覧 -->
    <section class="users-section">
      <h2>ユーザー一覧</h2>

      <!-- ローディング -->
      <div v-if="userStore.loading && userStore.users.length === 0" class="loading">
        読み込み中...
      </div>

      <!-- ユーザーがない場合 -->
      <div v-else-if="userStore.users.length === 0" class="no-users">
        ユーザーがいません
      </div>

      <!-- ユーザーリスト -->
      <div v-else class="users-table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>ユーザー名</th>
              <th>権限</th>
              <th>作成日時</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in userStore.users" :key="user.user_id">
              <!-- 編集モード -->
              <template v-if="editingUserId === user.user_id">
                <td>
                  <input
                    v-model="editForm.username"
                    type="text"
                    placeholder="ユーザー名"
                    minlength="3"
                    maxlength="50"
                  />
                </td>
                <td>
                  <select v-model="editForm.role">
                    <option value="user">一般ユーザー</option>
                    <option value="admin">管理者</option>
                  </select>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>
                  <div class="action-buttons">
                    <button @click="handleUpdateUser(user.user_id)" class="save-button">
                      保存
                    </button>
                    <button @click="cancelEdit" class="cancel-button">
                      キャンセル
                    </button>
                  </div>
                </td>
              </template>

              <!-- 表示モード -->
              <template v-else>
                <td>{{ user.username }}</td>
                <td>
                  <span :class="['role-badge', user.role]">
                    {{ user.role === 'admin' ? '管理者' : '一般' }}
                  </span>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>
                  <div class="action-buttons">
                    <button @click="startEdit(user)" class="edit-button">
                      編集
                    </button>
                    <button
                      @click="handleDeleteUser(user.user_id)"
                      class="delete-button"
                      :disabled="user.user_id === authStore.currentUserId"
                    >
                      削除
                    </button>
                  </div>
                </td>
              </template>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
/**
 * ユーザー管理ビューコンポーネント
 * 
 * 管理者がユーザーを管理する画面。
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/users'

// ルーター
const router = useRouter()

// ストア
const authStore = useAuthStore()
const userStore = useUserStore()

// 新規ユーザーフォームデータ
const newUser = reactive({
  username: '',
  password: '',
  role: 'user',
})

// 編集中のユーザーID
const editingUserId = ref(null)

// 編集フォームデータ
const editForm = reactive({
  username: '',
  role: '',
})

// 成功メッセージ
const successMessage = ref(null)

/**
 * マウント時にユーザー一覧を取得
 */
onMounted(async () => {
  await userStore.fetchUsers()
})

/**
 * 成功メッセージを表示して自動的に消す
 * 
 * @param {string} message - 表示するメッセージ
 */
function showSuccess(message) {
  successMessage.value = message
  setTimeout(() => {
    successMessage.value = null
  }, 3000)
}

/**
 * 新規ユーザーを作成
 */
async function handleCreateUser() {
  try {
    await userStore.createUser({
      username: newUser.username,
      password: newUser.password,
      role: newUser.role,
    })
    // フォームをリセット
    newUser.username = ''
    newUser.password = ''
    newUser.role = 'user'
    showSuccess('ユーザーを作成しました')
  } catch (err) {
    console.error('ユーザーの作成に失敗しました', err)
  }
}

/**
 * 編集モードを開始
 * 
 * @param {Object} user - 編集対象のユーザー
 */
function startEdit(user) {
  editingUserId.value = user.user_id
  editForm.username = user.username
  editForm.role = user.role
}

/**
 * 編集をキャンセル
 */
function cancelEdit() {
  editingUserId.value = null
  editForm.username = ''
  editForm.role = ''
}

/**
 * ユーザーを更新
 * 
 * @param {string} userId - ユーザーID
 */
async function handleUpdateUser(userId) {
  try {
    await userStore.updateUser(userId, {
      username: editForm.username,
      role: editForm.role,
    })
    cancelEdit()
    showSuccess('ユーザーを更新しました')
  } catch (err) {
    console.error('ユーザーの更新に失敗しました', err)
  }
}

/**
 * ユーザーを削除
 * 
 * @param {string} userId - ユーザーID
 */
async function handleDeleteUser(userId) {
  if (!confirm('このユーザーを削除してもよろしいですか？')) {
    return
  }
  try {
    await userStore.deleteUser(userId)
    showSuccess('ユーザーを削除しました')
  } catch (err) {
    console.error('ユーザーの削除に失敗しました', err)
  }
}

/**
 * ログアウト処理
 */
function handleLogout() {
  authStore.logout()
  router.push({ name: 'Login' })
}

/**
 * 日付をフォーマット
 * 
 * @param {string} dateString - ISO形式の日付文字列
 * @returns {string} フォーマット済み日付
 */
function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
/* コンテナ */
.users-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1rem;
}

/* ヘッダー */
.users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 2px solid #4a90d9;
  margin-bottom: 1.5rem;
}

.users-header h1 {
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-link {
  color: #4a90d9;
  text-decoration: none;
}

.nav-link:hover {
  text-decoration: underline;
}

.logout-button {
  padding: 0.5rem 1rem;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.logout-button:hover {
  background-color: #e8e8e8;
}

/* ユーザーフォームセクション */
.user-form-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.user-form-section h2 {
  margin-top: 0;
  color: #333;
}

.user-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  min-width: 150px;
}

.form-group label {
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #4a90d9;
}

.submit-button {
  padding: 0.75rem;
  background-color: #4a90d9;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  max-width: 200px;
}

.submit-button:hover:not(:disabled) {
  background-color: #357abd;
}

.submit-button:disabled {
  background-color: #a0c4e8;
  cursor: not-allowed;
}

/* メッセージ */
.error-message {
  background-color: #ffe6e6;
  color: #cc0000;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.success-message {
  background-color: #e6ffe6;
  color: #00cc00;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

/* ユーザー一覧セクション */
.users-section {
  margin-top: 1.5rem;
}

.users-section h2 {
  color: #333;
}

.loading,
.no-users {
  text-align: center;
  color: #666;
  padding: 2rem;
}

/* ユーザーテーブル */
.users-table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.users-table th,
.users-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.users-table th {
  background-color: #f9f9f9;
  font-weight: 600;
  color: #333;
}

.users-table tr:last-child td {
  border-bottom: none;
}

/* 権限バッジ */
.role-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.role-badge.admin {
  background-color: #4a90d9;
  color: white;
}

.role-badge.user {
  background-color: #f0f0f0;
  color: #666;
}

/* 操作ボタン */
.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.edit-button,
.delete-button,
.save-button,
.cancel-button {
  padding: 0.25rem 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.edit-button {
  background-color: #f0f0f0;
  color: #333;
}

.edit-button:hover {
  background-color: #e0e0e0;
}

.delete-button {
  background-color: #ffe6e6;
  color: #cc0000;
}

.delete-button:hover:not(:disabled) {
  background-color: #ffcccc;
}

.delete-button:disabled {
  background-color: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.save-button {
  background-color: #4a90d9;
  color: white;
}

.save-button:hover {
  background-color: #357abd;
}

.cancel-button {
  background-color: #f0f0f0;
  color: #333;
}

.cancel-button:hover {
  background-color: #e0e0e0;
}

/* テーブル内のフォーム要素 */
.users-table input,
.users-table select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.875rem;
  width: 100%;
}
</style>
