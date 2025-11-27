"""
ユーザールーター

ユーザー管理のAPIエンドポイントを提供する。
管理者のみがユーザーの追加・変更・削除を行える。
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from app.models.user import UserCreate, UserUpdate, UserResponse
from app.models.auth import TokenData
from app.services.auth import get_admin_user
from app.services.user_service import user_service

# ルーターの作成
router = APIRouter(prefix="/users", tags=["ユーザー管理"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="ユーザー作成", description="新規ユーザーを作成する（管理者のみ）")
async def create_user(
    user_data: UserCreate,
    current_user: TokenData = Depends(get_admin_user)
) -> UserResponse:
    """
    新規ユーザーを作成する
    
    管理者権限が必要。
    
    Args:
        user_data: ユーザー作成データ
        current_user: 現在の管理者ユーザー（自動注入）
    
    Returns:
        UserResponse: 作成されたユーザー情報
    
    Raises:
        HTTPException: ユーザー名が既に存在する場合
    """
    try:
        user = user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[UserResponse], summary="ユーザー一覧取得", description="全ユーザーの一覧を取得する（管理者のみ）")
async def get_users(
    current_user: TokenData = Depends(get_admin_user)
) -> List[UserResponse]:
    """
    全ユーザーを取得する
    
    管理者権限が必要。
    
    Args:
        current_user: 現在の管理者ユーザー（自動注入）
    
    Returns:
        List[UserResponse]: ユーザーリスト
    """
    return user_service.get_all_users()


@router.get("/{user_id}", response_model=UserResponse, summary="ユーザー詳細取得", description="指定したユーザーの詳細情報を取得する（管理者のみ）")
async def get_user(
    user_id: str,
    current_user: TokenData = Depends(get_admin_user)
) -> UserResponse:
    """
    特定のユーザーを取得する
    
    管理者権限が必要。
    
    Args:
        user_id: 取得対象のユーザーID
        current_user: 現在の管理者ユーザー（自動注入）
    
    Returns:
        UserResponse: ユーザー情報
    
    Raises:
        HTTPException: ユーザーが見つからない場合
    """
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )
    
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        role=user.role,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("/{user_id}", response_model=UserResponse, summary="ユーザー更新", description="指定したユーザーの情報を更新する（管理者のみ）")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: TokenData = Depends(get_admin_user)
) -> UserResponse:
    """
    ユーザー情報を更新する
    
    管理者権限が必要。
    
    Args:
        user_id: 更新対象のユーザーID
        user_data: 更新データ
        current_user: 現在の管理者ユーザー（自動注入）
    
    Returns:
        UserResponse: 更新後のユーザー情報
    
    Raises:
        HTTPException: ユーザーが見つからない場合、またはユーザー名が既に使用されている場合
    """
    try:
        user = user_service.update_user(user_id, user_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )
        
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="ユーザー削除", description="指定したユーザーを削除する（管理者のみ）")
async def delete_user(
    user_id: str,
    current_user: TokenData = Depends(get_admin_user)
):
    """
    ユーザーを削除する
    
    管理者権限が必要。
    
    Args:
        user_id: 削除対象のユーザーID
        current_user: 現在の管理者ユーザー（自動注入）
    
    Raises:
        HTTPException: ユーザーが見つからない場合
    """
    if not user_service.delete_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )
