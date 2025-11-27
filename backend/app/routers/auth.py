"""
認証ルーター

ログイン・認証関連のAPIエンドポイントを提供する。
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta

from app.models.auth import LoginRequest, Token, TokenData
from app.models.user import UserResponse
from app.services.auth import create_access_token, get_current_user
from app.services.user_service import user_service
from app.config import get_settings

# ルーターの作成
router = APIRouter(prefix="/auth", tags=["認証"])


@router.post("/login", response_model=Token, summary="ログイン", description="ユーザー名とパスワードで認証し、JWTトークンを取得する")
async def login(login_data: LoginRequest) -> Token:
    """
    ログイン処理
    
    ユーザー名とパスワードを検証し、JWTアクセストークンを発行する。
    
    Args:
        login_data: ログインリクエスト（ユーザー名、パスワード）
    
    Returns:
        Token: アクセストークン
    
    Raises:
        HTTPException: 認証に失敗した場合
    """
    # ユーザー認証
    user = user_service.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # トークンの有効期限を設定
    settings = get_settings()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # トークンを作成
    access_token = create_access_token(
        data={
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
        },
        expires_delta=access_token_expires,
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse, summary="現在のユーザー情報取得", description="認証済みユーザーの情報を取得する")
async def get_me(current_user: TokenData = Depends(get_current_user)) -> UserResponse:
    """
    現在のユーザー情報を取得する
    
    Args:
        current_user: 現在の認証済みユーザー（自動注入）
    
    Returns:
        UserResponse: ユーザー情報
    
    Raises:
        HTTPException: ユーザーが見つからない場合
    """
    user = user_service.get_user_by_id(current_user.user_id)
    
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
