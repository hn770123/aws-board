"""
認証モデル

ログイン・トークン関連のPydanticモデル。
JWT認証に使用するデータ構造を提供する。
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """
    ログインリクエストモデル
    
    ユーザー認証時に送信されるデータ。
    """
    # ユーザー名
    username: str = Field(..., description="ユーザー名")
    # パスワード
    password: str = Field(..., description="パスワード")


class Token(BaseModel):
    """
    トークンレスポンスモデル
    
    認証成功時に返されるJWTトークン情報。
    """
    # アクセストークン（JWT）
    access_token: str = Field(..., description="アクセストークン")
    # トークンタイプ（常に"bearer"）
    token_type: str = Field(default="bearer", description="トークンタイプ")


class TokenData(BaseModel):
    """
    トークンデータモデル
    
    JWTトークンのペイロードに含まれるデータ。
    """
    # ユーザーID
    user_id: str = Field(..., description="ユーザーID")
    # ユーザー名
    username: str = Field(..., description="ユーザー名")
    # ユーザー権限
    role: str = Field(..., description="ユーザー権限")
