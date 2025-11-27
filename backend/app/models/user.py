"""
ユーザーモデル

掲示板システムのユーザー情報を定義するPydanticモデル。
認証・認可に使用するユーザーデータの構造を提供する。
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """
    ユーザー権限の列挙型
    
    一般ユーザーとシステム管理者の2種類の権限を定義。
    """
    # 一般ユーザー（投稿の作成・自身の投稿の編集/削除が可能）
    USER = "user"
    # システム管理者（ユーザー管理・全投稿の編集/削除が可能）
    ADMIN = "admin"


class UserBase(BaseModel):
    """
    ユーザー基本情報モデル
    
    ユーザー名と権限を含む基本的なユーザー情報。
    """
    # ユーザー名（3文字以上50文字以下）
    username: str = Field(..., min_length=3, max_length=50, description="ユーザー名")
    # ユーザー権限（デフォルトは一般ユーザー）
    role: UserRole = Field(default=UserRole.USER, description="ユーザー権限")


class UserCreate(UserBase):
    """
    ユーザー作成リクエストモデル
    
    新規ユーザー作成時に使用するモデル。パスワードを含む。
    """
    # パスワード（6文字以上）
    password: str = Field(..., min_length=6, description="パスワード")


class UserUpdate(BaseModel):
    """
    ユーザー更新リクエストモデル
    
    ユーザー情報の更新時に使用するモデル。全フィールドがオプショナル。
    """
    # 新しいユーザー名（オプション）
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="ユーザー名")
    # 新しいパスワード（オプション）
    password: Optional[str] = Field(None, min_length=6, description="パスワード")
    # 新しい権限（オプション）
    role: Optional[UserRole] = Field(None, description="ユーザー権限")


class UserResponse(UserBase):
    """
    ユーザーレスポンスモデル
    
    APIレスポンスとして返すユーザー情報。パスワードは含まない。
    """
    # ユーザーID
    user_id: str = Field(..., description="ユーザーID")
    # 作成日時
    created_at: datetime = Field(..., description="作成日時")
    # 更新日時
    updated_at: datetime = Field(..., description="更新日時")


class UserInDB(UserResponse):
    """
    データベース内ユーザーモデル
    
    DynamoDBに保存されるユーザー情報。ハッシュ化されたパスワードを含む。
    """
    # ハッシュ化されたパスワード
    hashed_password: str = Field(..., description="ハッシュ化されたパスワード")
