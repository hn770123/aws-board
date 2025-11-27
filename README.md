# 掲示板システム

Vue.js + FastAPI + DynamoDBで構築したサーバーレス掲示板システムです。

## 技術スタック

- **フロントエンド**: Vue.js 3 + Pinia + Vue Router
- **バックエンド**: Python (FastAPI) + AWS Lambda
- **データベース**: Amazon DynamoDB
- **インフラ**: AWS / Serverless Framework
- **認証**: JWT (JSON Web Token)

## 機能

### ユーザー権限

| 機能 | 一般ユーザー | 管理者 |
|------|:----------:|:------:|
| ログイン/ログアウト | ✓ | ✓ |
| 投稿の閲覧 | ✓ | ✓ |
| 投稿の作成 | ✓ | ✓ |
| 自分の投稿の編集/削除 | ✓ | ✓ |
| 他人の投稿の編集/削除 | ✗ | ✓ |
| ユーザー管理 | ✗ | ✓ |

### 主要機能

- **ログイン認証**: ユーザー名とパスワードによるJWT認証
- **投稿機能**: タイトルとメッセージの投稿、ユーザー名と日時の表示
- **投稿の編集/削除**: 投稿者本人または管理者のみ可能
- **ユーザー管理**: 管理者によるユーザーの追加・変更・削除

## プロジェクト構成

```
aws-board/
├── backend/                 # バックエンド（FastAPI）
│   ├── app/
│   │   ├── main.py         # アプリケーションエントリーポイント
│   │   ├── config.py       # 設定管理
│   │   ├── models/         # Pydanticモデル
│   │   ├── routers/        # APIルーター
│   │   └── services/       # ビジネスロジック
│   ├── tests/              # バックエンドテスト
│   ├── requirements.txt    # Python依存パッケージ
│   └── serverless.yml      # Serverless Framework設定
├── frontend/               # フロントエンド（Vue.js）
│   ├── src/
│   │   ├── views/          # ビューコンポーネント
│   │   ├── stores/         # Piniaストア
│   │   ├── services/       # API通信サービス
│   │   └── router/         # Vue Routerの設定
│   ├── package.json
│   └── vite.config.js
└── docs/                   # ドキュメント
    └── DESIGN.md           # 設計ドキュメント
```

## セットアップ

### 前提条件

- Node.js 20.x以上
- Python 3.11以上
- AWS CLI（デプロイ時）
- Serverless Framework（デプロイ時）

### バックエンド

```bash
cd backend

# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# 開発サーバーの起動（ローカル）
uvicorn app.main:app --reload --port 8000
```

### フロントエンド

```bash
cd frontend

# 依存パッケージのインストール
npm install

# 開発サーバーの起動
npm run dev
```

### 環境変数

バックエンド（`.env`または環境変数）:

```
SECRET_KEY=your-secret-key-change-in-production
DYNAMODB_ENDPOINT=http://localhost:8001  # ローカル開発用
USERS_TABLE=bulletin-board-users
POSTS_TABLE=bulletin-board-posts
AWS_REGION=ap-northeast-1
CORS_ORIGINS=http://localhost:5173
```

フロントエンド（`.env`）:

```
VITE_API_URL=http://localhost:8000
```

## テスト

### バックエンドテスト

```bash
cd backend
pytest
```

### フロントエンドテスト

```bash
cd frontend
npm test
```

## デプロイ

### AWSへのデプロイ

```bash
cd backend

# Serverless Frameworkでデプロイ
serverless deploy --stage prod
```

デプロイ後、APIのURLをフロントエンドの`VITE_API_URL`に設定してビルドします。

```bash
cd frontend
npm run build
```

ビルド成果物（`dist/`ディレクトリ）をS3 + CloudFrontなどでホスティングします。

## API仕様

### 認証

| メソッド | パス | 説明 |
|---------|------|------|
| POST | /auth/login | ログイン |
| GET | /auth/me | 現在のユーザー情報取得 |

### ユーザー管理（管理者のみ）

| メソッド | パス | 説明 |
|---------|------|------|
| GET | /users/ | ユーザー一覧取得 |
| POST | /users/ | ユーザー作成 |
| GET | /users/{user_id} | ユーザー詳細取得 |
| PUT | /users/{user_id} | ユーザー更新 |
| DELETE | /users/{user_id} | ユーザー削除 |

### 投稿管理

| メソッド | パス | 説明 |
|---------|------|------|
| GET | /posts/ | 投稿一覧取得 |
| POST | /posts/ | 投稿作成 |
| GET | /posts/{post_id} | 投稿詳細取得 |
| PUT | /posts/{post_id} | 投稿更新（投稿者/管理者のみ） |
| DELETE | /posts/{post_id} | 投稿削除（投稿者/管理者のみ） |

## ドキュメント

詳細な設計ドキュメントは[docs/DESIGN.md](docs/DESIGN.md)を参照してください。

- クラス図
- シーケンス図
- アクティビティ図
- ユースケース図

## ライセンス

MIT License
