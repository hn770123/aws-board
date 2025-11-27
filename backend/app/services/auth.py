"""
認証サービス

JWT認証とパスワードハッシュ化の機能を提供する。
ユーザー認証の核となるロジックを実装。
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import get_settings
from app.models.auth import TokenData
from app.models.user import UserRole

# パスワードハッシュ化の設定（bcryptを使用）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer認証スキーム
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワードを検証する
    
    平文パスワードとハッシュ化されたパスワードを比較する。
    
    Args:
        plain_password: 平文のパスワード
        hashed_password: ハッシュ化されたパスワード
    
    Returns:
        bool: パスワードが一致する場合True
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    パスワードをハッシュ化する
    
    Args:
        password: 平文のパスワード
    
    Returns:
        str: ハッシュ化されたパスワード
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWTアクセストークンを作成する
    
    Args:
        data: トークンに含めるデータ
        expires_delta: 有効期限（指定しない場合はデフォルト値を使用）
    
    Returns:
        str: エンコードされたJWTトークン
    """
    settings = get_settings()
    to_encode = data.copy()
    
    # 有効期限を設定
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # JWTをエンコード
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    JWTアクセストークンをデコードする
    
    Args:
        token: JWTトークン文字列
    
    Returns:
        TokenData: デコードされたトークンデータ、無効な場合はNone
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("user_id")
        username: str = payload.get("username")
        role: str = payload.get("role")
        
        if user_id is None or username is None or role is None:
            return None
            
        return TokenData(user_id=user_id, username=username, role=role)
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    現在の認証済みユーザーを取得する（依存性注入用）
    
    Args:
        credentials: HTTPAuthorizationCredentials（Bearer トークン）
    
    Returns:
        TokenData: 現在のユーザー情報
    
    Raises:
        HTTPException: 認証に失敗した場合
    """
    # 認証エラー用の例外
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    if token_data is None:
        raise credentials_exception
    
    return token_data


async def get_admin_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """
    管理者ユーザーのみを許可する（依存性注入用）
    
    Args:
        current_user: 現在の認証済みユーザー
    
    Returns:
        TokenData: 管理者ユーザー情報
    
    Raises:
        HTTPException: 管理者でない場合
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この操作には管理者権限が必要です"
        )
    return current_user
