"""
投稿モデル

掲示板の投稿情報を定義するPydanticモデル。
投稿の作成・更新・表示に使用するデータ構造を提供する。
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PostBase(BaseModel):
    """
    投稿基本情報モデル
    
    タイトルとメッセージを含む投稿の基本情報。
    """
    # 投稿タイトル（1文字以上100文字以下）
    title: str = Field(..., min_length=1, max_length=100, description="投稿タイトル")
    # 投稿メッセージ（1文字以上2000文字以下）
    message: str = Field(..., min_length=1, max_length=2000, description="投稿メッセージ")


class PostCreate(PostBase):
    """
    投稿作成リクエストモデル
    
    新規投稿作成時に使用するモデル。基本情報のみ。
    """
    pass


class PostUpdate(BaseModel):
    """
    投稿更新リクエストモデル
    
    投稿の更新時に使用するモデル。全フィールドがオプショナル。
    """
    # 新しいタイトル（オプション）
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="投稿タイトル")
    # 新しいメッセージ（オプション）
    message: Optional[str] = Field(None, min_length=1, max_length=2000, description="投稿メッセージ")


class PostResponse(PostBase):
    """
    投稿レスポンスモデル
    
    APIレスポンスとして返す投稿情報。投稿者・日時情報を含む。
    """
    # 投稿ID
    post_id: str = Field(..., description="投稿ID")
    # 投稿者のユーザーID
    user_id: str = Field(..., description="投稿者のユーザーID")
    # 投稿者のユーザー名
    username: str = Field(..., description="投稿者のユーザー名")
    # 作成日時
    created_at: datetime = Field(..., description="作成日時")
    # 更新日時
    updated_at: datetime = Field(..., description="更新日時")


class PostInDB(PostResponse):
    """
    データベース内投稿モデル
    
    DynamoDBに保存される投稿情報。
    """
    pass
