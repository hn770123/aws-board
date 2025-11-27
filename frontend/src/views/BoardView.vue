<!--
  掲示板画面

  投稿の一覧表示と新規投稿フォームを同じ画面に配置する。
  投稿の編集・削除は投稿者本人または管理者のみ可能。
-->
<template>
  <div class="board-container">
    <!-- ヘッダー -->
    <header class="board-header">
      <h1>掲示板</h1>
      <div class="header-actions">
        <span class="user-info">
          {{ authStore.user?.username }}
          <span v-if="authStore.isAdmin" class="admin-badge">管理者</span>
        </span>
        <router-link v-if="authStore.isAdmin" to="/users" class="nav-link">
          ユーザー管理
        </router-link>
        <button @click="handleLogout" class="logout-button">ログアウト</button>
      </div>
    </header>

    <!-- 投稿フォーム -->
    <section class="post-form-section">
      <h2>新規投稿</h2>
      <form @submit.prevent="handleCreatePost" class="post-form">
        <div class="form-group">
          <label for="title">タイトル</label>
          <input
            id="title"
            v-model="newPost.title"
            type="text"
            placeholder="タイトルを入力"
            required
            maxlength="100"
          />
        </div>
        <div class="form-group">
          <label for="message">メッセージ</label>
          <textarea
            id="message"
            v-model="newPost.message"
            placeholder="メッセージを入力"
            required
            maxlength="2000"
            rows="4"
          ></textarea>
        </div>
        <button type="submit" class="submit-button" :disabled="postStore.loading">
          {{ postStore.loading ? '投稿中...' : '投稿する' }}
        </button>
      </form>
    </section>

    <!-- エラーメッセージ -->
    <div v-if="postStore.error" class="error-message">
      {{ postStore.error }}
    </div>

    <!-- 投稿一覧 -->
    <section class="posts-section">
      <h2>投稿一覧</h2>
      
      <!-- ローディング -->
      <div v-if="postStore.loading && postStore.posts.length === 0" class="loading">
        読み込み中...
      </div>

      <!-- 投稿がない場合 -->
      <div v-else-if="postStore.posts.length === 0" class="no-posts">
        まだ投稿がありません
      </div>

      <!-- 投稿リスト -->
      <div v-else class="posts-list">
        <article
          v-for="post in postStore.posts"
          :key="post.post_id"
          class="post-card"
        >
          <!-- 編集モード -->
          <div v-if="editingPostId === post.post_id" class="edit-form">
            <input
              v-model="editForm.title"
              type="text"
              placeholder="タイトル"
              required
            />
            <textarea
              v-model="editForm.message"
              placeholder="メッセージ"
              required
              rows="3"
            ></textarea>
            <div class="edit-actions">
              <button @click="handleUpdatePost(post.post_id)" class="save-button">
                保存
              </button>
              <button @click="cancelEdit" class="cancel-button">
                キャンセル
              </button>
            </div>
          </div>

          <!-- 表示モード -->
          <div v-else>
            <div class="post-header">
              <h3 class="post-title">{{ post.title }}</h3>
              <div v-if="canModifyPost(post)" class="post-actions">
                <button @click="startEdit(post)" class="edit-button">編集</button>
                <button @click="handleDeletePost(post.post_id)" class="delete-button">
                  削除
                </button>
              </div>
            </div>
            <p class="post-message">{{ post.message }}</p>
            <div class="post-meta">
              <span class="post-author">{{ post.username }}</span>
              <span class="post-date">{{ formatDate(post.created_at) }}</span>
              <span v-if="post.updated_at !== post.created_at" class="post-updated">
                （編集済み）
              </span>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
/**
 * 掲示板ビューコンポーネント
 * 
 * 投稿一覧と投稿フォームを表示する。
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePostStore } from '@/stores/posts'

// ルーター
const router = useRouter()

// ストア
const authStore = useAuthStore()
const postStore = usePostStore()

// 新規投稿フォームデータ
const newPost = reactive({
  title: '',
  message: '',
})

// 編集中の投稿ID
const editingPostId = ref(null)

// 編集フォームデータ
const editForm = reactive({
  title: '',
  message: '',
})

/**
 * マウント時に投稿一覧を取得
 */
onMounted(async () => {
  await postStore.fetchPosts()
})

/**
 * 投稿の変更・削除権限をチェック
 * 
 * @param {Object} post - 投稿オブジェクト
 * @returns {boolean} 権限がある場合true
 */
function canModifyPost(post) {
  // 投稿者本人
  if (post.user_id === authStore.currentUserId) {
    return true
  }
  // 管理者
  if (authStore.isAdmin) {
    return true
  }
  return false
}

/**
 * 新規投稿の作成
 */
async function handleCreatePost() {
  try {
    await postStore.createPost({
      title: newPost.title,
      message: newPost.message,
    })
    // フォームをリセット
    newPost.title = ''
    newPost.message = ''
  } catch (err) {
    console.error('投稿の作成に失敗しました', err)
  }
}

/**
 * 編集モードを開始
 * 
 * @param {Object} post - 編集対象の投稿
 */
function startEdit(post) {
  editingPostId.value = post.post_id
  editForm.title = post.title
  editForm.message = post.message
}

/**
 * 編集をキャンセル
 */
function cancelEdit() {
  editingPostId.value = null
  editForm.title = ''
  editForm.message = ''
}

/**
 * 投稿を更新
 * 
 * @param {string} postId - 投稿ID
 */
async function handleUpdatePost(postId) {
  try {
    await postStore.updatePost(postId, {
      title: editForm.title,
      message: editForm.message,
    })
    cancelEdit()
  } catch (err) {
    console.error('投稿の更新に失敗しました', err)
  }
}

/**
 * 投稿を削除
 * 
 * @param {string} postId - 投稿ID
 */
async function handleDeletePost(postId) {
  if (!confirm('この投稿を削除してもよろしいですか？')) {
    return
  }
  try {
    await postStore.deletePost(postId)
  } catch (err) {
    console.error('投稿の削除に失敗しました', err)
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
.board-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}

/* ヘッダー */
.board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 2px solid #4a90d9;
  margin-bottom: 1.5rem;
}

.board-header h1 {
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  color: #666;
}

.admin-badge {
  background-color: #4a90d9;
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  margin-left: 0.5rem;
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
  transition: background-color 0.2s;
}

.logout-button:hover {
  background-color: #e8e8e8;
}

/* 投稿フォームセクション */
.post-form-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.post-form-section h2 {
  margin-top: 0;
  color: #333;
}

.post-form {
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

.form-group input,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
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
  transition: background-color 0.2s;
}

.submit-button:hover:not(:disabled) {
  background-color: #357abd;
}

.submit-button:disabled {
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
}

/* 投稿一覧セクション */
.posts-section {
  margin-top: 1.5rem;
}

.posts-section h2 {
  color: #333;
}

.loading,
.no-posts {
  text-align: center;
  color: #666;
  padding: 2rem;
}

/* 投稿リスト */
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 投稿カード */
.post-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.post-title {
  margin: 0;
  color: #333;
  font-size: 1.25rem;
}

.post-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-button,
.delete-button {
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

.delete-button:hover {
  background-color: #ffcccc;
}

.post-message {
  color: #333;
  line-height: 1.6;
  white-space: pre-wrap;
  margin: 0 0 1rem 0;
}

.post-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #666;
}

.post-author {
  font-weight: 500;
}

.post-updated {
  color: #999;
}

/* 編集フォーム */
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.edit-form input,
.edit-form textarea {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
}

.save-button,
.cancel-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
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
</style>
