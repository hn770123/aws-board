"""
投稿ルーター

投稿管理のAPIエンドポイントを提供する。
認証済みユーザーが投稿の作成・閲覧を行える。
投稿の変更・削除は投稿者本人または管理者のみ可能。
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from app.models.post import PostCreate, PostUpdate, PostResponse
from app.models.auth import TokenData
from app.models.user import UserRole
from app.services.auth import get_current_user
from app.services.post_service import post_service

# ルーターの作成
router = APIRouter(prefix="/posts", tags=["投稿管理"])


def can_modify_post(post: PostResponse, current_user: TokenData) -> bool:
    """
    投稿の変更・削除権限をチェックする
    
    投稿者本人または管理者のみが変更・削除可能。
    
    Args:
        post: 対象の投稿
        current_user: 現在のユーザー
    
    Returns:
        bool: 変更・削除権限がある場合True
    """
    # 投稿者本人の場合
    if post.user_id == current_user.user_id:
        return True
    
    # 管理者の場合
    if current_user.role == UserRole.ADMIN:
        return True
    
    return False


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED, summary="投稿作成", description="新規投稿を作成する")
async def create_post(
    post_data: PostCreate,
    current_user: TokenData = Depends(get_current_user)
) -> PostResponse:
    """
    新規投稿を作成する
    
    認証済みユーザーのみ使用可能。
    
    Args:
        post_data: 投稿作成データ
        current_user: 現在の認証済みユーザー（自動注入）
    
    Returns:
        PostResponse: 作成された投稿情報
    """
    post = post_service.create_post(
        post_data=post_data,
        user_id=current_user.user_id,
        username=current_user.username,
    )
    return post


@router.get("/", response_model=List[PostResponse], summary="投稿一覧取得", description="全投稿の一覧を取得する（新しい順）")
async def get_posts(
    limit: int = 100,
    current_user: TokenData = Depends(get_current_user)
) -> List[PostResponse]:
    """
    全投稿を取得する
    
    認証済みユーザーのみ使用可能。
    作成日時の降順（新しい順）で返す。
    
    Args:
        limit: 取得する最大件数（デフォルト100）
        current_user: 現在の認証済みユーザー（自動注入）
    
    Returns:
        List[PostResponse]: 投稿リスト
    """
    return post_service.get_all_posts(limit=limit)


@router.get("/{post_id}", response_model=PostResponse, summary="投稿詳細取得", description="指定した投稿の詳細情報を取得する")
async def get_post(
    post_id: str,
    current_user: TokenData = Depends(get_current_user)
) -> PostResponse:
    """
    特定の投稿を取得する
    
    認証済みユーザーのみ使用可能。
    
    Args:
        post_id: 取得対象の投稿ID
        current_user: 現在の認証済みユーザー（自動注入）
    
    Returns:
        PostResponse: 投稿情報
    
    Raises:
        HTTPException: 投稿が見つからない場合
    """
    post = post_service.get_post_by_id(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="投稿が見つかりません"
        )
    
    return post


@router.put("/{post_id}", response_model=PostResponse, summary="投稿更新", description="指定した投稿を更新する（投稿者または管理者のみ）")
async def update_post(
    post_id: str,
    post_data: PostUpdate,
    current_user: TokenData = Depends(get_current_user)
) -> PostResponse:
    """
    投稿を更新する
    
    投稿者本人または管理者のみ使用可能。
    
    Args:
        post_id: 更新対象の投稿ID
        post_data: 更新データ
        current_user: 現在の認証済みユーザー（自動注入）
    
    Returns:
        PostResponse: 更新後の投稿情報
    
    Raises:
        HTTPException: 投稿が見つからない場合、または権限がない場合
    """
    # 既存投稿を取得
    existing_post = post_service.get_post_by_id(post_id)
    
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="投稿が見つかりません"
        )
    
    # 権限チェック
    if not can_modify_post(existing_post, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この投稿を更新する権限がありません"
        )
    
    updated_post = post_service.update_post(post_id, post_data)
    return updated_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, summary="投稿削除", description="指定した投稿を削除する（投稿者または管理者のみ）")
async def delete_post(
    post_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    投稿を削除する
    
    投稿者本人または管理者のみ使用可能。
    
    Args:
        post_id: 削除対象の投稿ID
        current_user: 現在の認証済みユーザー（自動注入）
    
    Raises:
        HTTPException: 投稿が見つからない場合、または権限がない場合
    """
    # 既存投稿を取得
    existing_post = post_service.get_post_by_id(post_id)
    
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="投稿が見つかりません"
        )
    
    # 権限チェック
    if not can_modify_post(existing_post, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この投稿を削除する権限がありません"
        )
    
    post_service.delete_post(post_id)
