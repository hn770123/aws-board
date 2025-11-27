# 掲示板システム ドキュメント

Vue.js + FastAPI + DynamoDBで構築した掲示板システムの設計ドキュメントです。

## 目次

1. [クラス図](#クラス図)
2. [シーケンス図](#シーケンス図)
3. [アクティビティ図](#アクティビティ図)
4. [ユースケース図](#ユースケース図)

---

## クラス図

システムの主要なクラス構造を示します。

```mermaid
classDiagram
    %% ユーザー関連
    class UserRole {
        <<enumeration>>
        USER
        ADMIN
    }

    class UserBase {
        +string username
        +UserRole role
    }

    class UserCreate {
        +string username
        +UserRole role
        +string password
    }

    class UserUpdate {
        +string username
        +string password
        +UserRole role
    }

    class UserResponse {
        +string user_id
        +string username
        +UserRole role
        +datetime created_at
        +datetime updated_at
    }

    class UserInDB {
        +string user_id
        +string username
        +UserRole role
        +string hashed_password
        +datetime created_at
        +datetime updated_at
    }

    UserBase <|-- UserCreate
    UserBase <|-- UserResponse
    UserResponse <|-- UserInDB

    %% 投稿関連
    class PostBase {
        +string title
        +string message
    }

    class PostCreate {
        +string title
        +string message
    }

    class PostUpdate {
        +string title
        +string message
    }

    class PostResponse {
        +string post_id
        +string user_id
        +string username
        +string title
        +string message
        +datetime created_at
        +datetime updated_at
    }

    PostBase <|-- PostCreate
    PostBase <|-- PostResponse

    %% 認証関連
    class LoginRequest {
        +string username
        +string password
    }

    class Token {
        +string access_token
        +string token_type
    }

    class TokenData {
        +string user_id
        +string username
        +string role
    }

    %% サービス
    class UserService {
        +create_user(UserCreate) UserResponse
        +get_user_by_id(string) UserInDB
        +get_user_by_username(string) UserInDB
        +get_all_users() List~UserResponse~
        +update_user(string, UserUpdate) UserResponse
        +delete_user(string) bool
        +authenticate_user(string, string) UserInDB
    }

    class PostService {
        +create_post(PostCreate, string, string) PostResponse
        +get_post_by_id(string) PostResponse
        +get_all_posts(int) List~PostResponse~
        +get_posts_by_user(string) List~PostResponse~
        +update_post(string, PostUpdate) PostResponse
        +delete_post(string) bool
    }

    UserService ..> UserCreate
    UserService ..> UserUpdate
    UserService ..> UserResponse
    UserService ..> UserInDB

    PostService ..> PostCreate
    PostService ..> PostUpdate
    PostService ..> PostResponse
```

---

## シーケンス図

### ログイン処理

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Frontend as フロントエンド
    participant API as FastAPI
    participant Auth as 認証サービス
    participant DB as DynamoDB

    User->>Frontend: ユーザー名・パスワード入力
    Frontend->>API: POST /auth/login
    API->>Auth: authenticate_user()
    Auth->>DB: ユーザー検索
    DB-->>Auth: ユーザーデータ
    Auth->>Auth: パスワード検証
    alt 認証成功
        Auth->>Auth: JWTトークン生成
        Auth-->>API: トークン
        API-->>Frontend: {access_token, token_type}
        Frontend->>Frontend: トークン保存
        Frontend-->>User: 掲示板画面へ遷移
    else 認証失敗
        Auth-->>API: null
        API-->>Frontend: 401 Unauthorized
        Frontend-->>User: エラーメッセージ表示
    end
```

### 投稿作成処理

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Frontend as フロントエンド
    participant API as FastAPI
    participant Auth as 認証ミドルウェア
    participant Post as 投稿サービス
    participant DB as DynamoDB

    User->>Frontend: タイトル・メッセージ入力
    Frontend->>API: POST /posts/ (+ Bearer Token)
    API->>Auth: トークン検証
    Auth->>Auth: JWTデコード
    alt トークン有効
        Auth-->>API: TokenData
        API->>Post: create_post(data, user_id, username)
        Post->>DB: PutItem
        DB-->>Post: 成功
        Post-->>API: PostResponse
        API-->>Frontend: 201 Created
        Frontend->>Frontend: 投稿リスト更新
        Frontend-->>User: 新規投稿表示
    else トークン無効
        Auth-->>API: 401 Unauthorized
        API-->>Frontend: 認証エラー
        Frontend-->>User: ログイン画面へ遷移
    end
```

### 投稿削除処理

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Frontend as フロントエンド
    participant API as FastAPI
    participant Auth as 認証ミドルウェア
    participant Post as 投稿サービス
    participant DB as DynamoDB

    User->>Frontend: 削除ボタンクリック
    Frontend->>API: DELETE /posts/{post_id} (+ Bearer Token)
    API->>Auth: トークン検証
    Auth-->>API: TokenData
    API->>Post: get_post_by_id(post_id)
    Post->>DB: GetItem
    DB-->>Post: 投稿データ
    Post-->>API: PostResponse
    API->>API: 権限チェック
    alt 投稿者本人または管理者
        API->>Post: delete_post(post_id)
        Post->>DB: DeleteItem
        DB-->>Post: 成功
        API-->>Frontend: 204 No Content
        Frontend->>Frontend: 投稿リストから削除
        Frontend-->>User: 削除完了
    else 権限なし
        API-->>Frontend: 403 Forbidden
        Frontend-->>User: エラーメッセージ表示
    end
```

---

## アクティビティ図

### ユーザー認証フロー

```mermaid
flowchart TD
    A[開始] --> B{ログイン済み?}
    B -->|はい| C[掲示板画面表示]
    B -->|いいえ| D[ログイン画面表示]
    D --> E[ユーザー名・パスワード入力]
    E --> F[ログインボタンクリック]
    F --> G{認証成功?}
    G -->|はい| H[トークン保存]
    H --> I[ユーザー情報取得]
    I --> C
    G -->|いいえ| J[エラーメッセージ表示]
    J --> D
    C --> K{操作選択}
    K -->|投稿作成| L[投稿フォーム入力]
    L --> M[投稿送信]
    M --> N[投稿リスト更新]
    N --> C
    K -->|投稿編集| O{権限あり?}
    O -->|はい| P[編集フォーム表示]
    P --> Q[編集送信]
    Q --> N
    O -->|いいえ| R[操作不可]
    R --> C
    K -->|投稿削除| S{権限あり?}
    S -->|はい| T[削除確認]
    T --> U[削除実行]
    U --> N
    S -->|いいえ| R
    K -->|ログアウト| V[トークン削除]
    V --> D
    K -->|ユーザー管理| W{管理者?}
    W -->|はい| X[ユーザー管理画面]
    W -->|いいえ| C
```

### 投稿変更・削除の権限チェック

```mermaid
flowchart TD
    A[投稿変更・削除要求] --> B{認証済み?}
    B -->|いいえ| C[401 認証エラー]
    B -->|はい| D{投稿存在?}
    D -->|いいえ| E[404 Not Found]
    D -->|はい| F{投稿者本人?}
    F -->|はい| G[操作許可]
    F -->|いいえ| H{管理者?}
    H -->|はい| G
    H -->|いいえ| I[403 権限エラー]
    G --> J[操作実行]
    J --> K[成功レスポンス]
```

---

## ユースケース図

```mermaid
flowchart LR
    subgraph Actors[アクター]
        Guest[ゲスト]
        User[一般ユーザー]
        Admin[管理者]
    end

    subgraph System[掲示板システム]
        UC1[ログイン]
        UC2[ログアウト]
        UC3[投稿一覧表示]
        UC4[投稿作成]
        UC5[自分の投稿編集]
        UC6[自分の投稿削除]
        UC7[他人の投稿編集]
        UC8[他人の投稿削除]
        UC9[ユーザー一覧表示]
        UC10[ユーザー作成]
        UC11[ユーザー編集]
        UC12[ユーザー削除]
    end

    %% ゲストのユースケース
    Guest --> UC1

    %% 一般ユーザーのユースケース
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6

    %% 管理者のユースケース（一般ユーザーの機能も含む）
    Admin --> UC1
    Admin --> UC2
    Admin --> UC3
    Admin --> UC4
    Admin --> UC5
    Admin --> UC6
    Admin --> UC7
    Admin --> UC8
    Admin --> UC9
    Admin --> UC10
    Admin --> UC11
    Admin --> UC12
```

### ユースケース詳細

| ユースケース | アクター | 説明 |
|-------------|---------|------|
| ログイン | ゲスト、一般ユーザー、管理者 | ユーザー名とパスワードで認証を行い、システムにアクセスする |
| ログアウト | 一般ユーザー、管理者 | 認証状態を解除してシステムからログアウトする |
| 投稿一覧表示 | 一般ユーザー、管理者 | 全投稿を新しい順に一覧表示する |
| 投稿作成 | 一般ユーザー、管理者 | 新しい投稿を作成する |
| 自分の投稿編集 | 一般ユーザー、管理者 | 自分が作成した投稿を編集する |
| 自分の投稿削除 | 一般ユーザー、管理者 | 自分が作成した投稿を削除する |
| 他人の投稿編集 | 管理者 | 他のユーザーが作成した投稿を編集する |
| 他人の投稿削除 | 管理者 | 他のユーザーが作成した投稿を削除する |
| ユーザー一覧表示 | 管理者 | 登録されている全ユーザーを一覧表示する |
| ユーザー作成 | 管理者 | 新しいユーザーアカウントを作成する |
| ユーザー編集 | 管理者 | 既存のユーザー情報を編集する |
| ユーザー削除 | 管理者 | ユーザーアカウントを削除する |
