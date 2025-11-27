/**
 * 投稿ストアのテスト
 * 
 * Piniaを使用した投稿状態管理のテスト。
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePostStore } from '@/stores/posts'

// モックの設定（ホイスティング問題を回避するため、変数を使用しない）
vi.mock('@/services/postService', () => ({
  default: {
    getPosts: vi.fn().mockResolvedValue([
      {
        post_id: '1',
        title: 'テスト投稿1',
        message: 'テストメッセージ1',
        user_id: 'user-1',
        username: 'testuser1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        post_id: '2',
        title: 'テスト投稿2',
        message: 'テストメッセージ2',
        user_id: 'user-2',
        username: 'testuser2',
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
      },
    ]),
    createPost: vi.fn().mockImplementation((data) =>
      Promise.resolve({
        post_id: '3',
        ...data,
        user_id: 'user-1',
        username: 'testuser1',
        created_at: '2024-01-03T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z',
      })
    ),
    updatePost: vi.fn().mockImplementation((postId, data) =>
      Promise.resolve({
        post_id: postId,
        title: data.title || 'テスト投稿1',
        message: data.message || 'テストメッセージ1',
        user_id: 'user-1',
        username: 'testuser1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z',
      })
    ),
    deletePost: vi.fn().mockResolvedValue(undefined),
  },
}))

describe('投稿ストア', () => {
  beforeEach(() => {
    // 各テスト前にPiniaを初期化
    setActivePinia(createPinia())
  })

  it('初期状態が正しいこと', () => {
    const store = usePostStore()
    
    expect(store.posts).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('投稿一覧を取得できること', async () => {
    const store = usePostStore()
    
    await store.fetchPosts()
    
    expect(store.posts).toHaveLength(2)
    expect(store.posts[0].title).toBe('テスト投稿1')
  })

  it('投稿を作成してリストの先頭に追加されること', async () => {
    const store = usePostStore()
    
    // 初期データを設定
    store.posts = [
      {
        post_id: '1',
        title: 'テスト投稿1',
        message: 'テストメッセージ1',
        user_id: 'user-1',
        username: 'testuser1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ]
    
    const newPost = {
      title: '新規投稿',
      message: '新規メッセージ',
    }
    
    await store.createPost(newPost)
    
    expect(store.posts).toHaveLength(2)
    expect(store.posts[0].title).toBe('新規投稿')
  })

  it('投稿を削除してリストから除外されること', async () => {
    const store = usePostStore()
    
    // 初期データを設定
    store.posts = [
      {
        post_id: '1',
        title: 'テスト投稿1',
        message: 'テストメッセージ1',
        user_id: 'user-1',
        username: 'testuser1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        post_id: '2',
        title: 'テスト投稿2',
        message: 'テストメッセージ2',
        user_id: 'user-2',
        username: 'testuser2',
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
      },
    ]
    
    await store.deletePost('1')
    
    expect(store.posts).toHaveLength(1)
    expect(store.posts[0].post_id).toBe('2')
  })
})
