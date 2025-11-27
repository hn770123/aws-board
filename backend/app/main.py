"""
掲示板アプリケーション メインモジュール

FastAPIアプリケーションのエントリーポイント。
AWS Lambda上でMangumを使用して実行される。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.config import get_settings
from app.routers import auth_router, users_router, posts_router

# 設定を取得
settings = get_settings()

# FastAPIアプリケーションの作成
app = FastAPI(
    title="掲示板API",
    description="Vue.js + FastAPI + DynamoDBで構築した掲示板システムのバックエンドAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(posts_router)


@app.get("/", tags=["ヘルスチェック"], summary="ヘルスチェック", description="APIの稼働状態を確認する")
async def health_check():
    """
    ヘルスチェックエンドポイント
    
    APIが正常に稼働しているかを確認するためのエンドポイント。
    
    Returns:
        dict: ステータス情報
    """
    return {"status": "healthy", "message": "掲示板APIは正常に稼働しています"}


# AWS Lambda用のハンドラー
handler = Mangum(app)
