"""
設定モジュール

アプリケーションの設定値を管理する。
環境変数から設定を読み込み、デフォルト値を提供する。
"""

import os
from functools import lru_cache


class Settings:
    """
    アプリケーション設定クラス
    
    環境変数から各種設定値を読み込む。
    """
    
    def __init__(self):
        # JWT設定
        # JWT署名に使用する秘密鍵
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        # JWTで使用するアルゴリズム
        self.ALGORITHM: str = "HS256"
        # アクセストークンの有効期限（分）
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        
        # DynamoDB設定
        # DynamoDBのエンドポイントURL（ローカル開発用）
        self.DYNAMODB_ENDPOINT: str = os.getenv("DYNAMODB_ENDPOINT", None)
        # ユーザーテーブル名
        self.USERS_TABLE: str = os.getenv("USERS_TABLE", "bulletin-board-users")
        # 投稿テーブル名
        self.POSTS_TABLE: str = os.getenv("POSTS_TABLE", "bulletin-board-posts")
        # AWSリージョン
        self.AWS_REGION: str = os.getenv("AWS_REGION", "ap-northeast-1")
        
        # CORS設定
        # 許可するオリジン
        self.CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")


@lru_cache()
def get_settings() -> Settings:
    """
    設定のシングルトンインスタンスを取得する
    
    キャッシュを使用して、複数回呼び出しても同じインスタンスを返す。
    
    Returns:
        Settings: 設定インスタンス
    """
    return Settings()
