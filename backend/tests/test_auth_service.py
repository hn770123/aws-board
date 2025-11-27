"""
認証サービスのテスト

パスワードハッシュ化とJWTトークンのテスト。
"""

import pytest
from datetime import timedelta

from app.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)


class TestPasswordHashing:
    """パスワードハッシュ化のテストクラス"""
    
    def test_password_hash_and_verify(self):
        """パスワードのハッシュ化と検証が正しく動作することを確認"""
        # 平文パスワード
        password = "test_password_123"
        
        # ハッシュ化
        hashed = get_password_hash(password)
        
        # ハッシュ化されていることを確認
        assert hashed != password
        
        # 検証が成功することを確認
        assert verify_password(password, hashed) is True
    
    def test_wrong_password_verification(self):
        """間違ったパスワードの検証が失敗することを確認"""
        password = "correct_password"
        wrong_password = "wrong_password"
        
        hashed = get_password_hash(password)
        
        # 間違ったパスワードで検証
        assert verify_password(wrong_password, hashed) is False


class TestJWTToken:
    """JWTトークンのテストクラス"""
    
    def test_create_and_decode_token(self):
        """トークンの作成とデコードが正しく動作することを確認"""
        # テストデータ
        data = {
            "user_id": "test-user-id",
            "username": "testuser",
            "role": "user"
        }
        
        # トークンを作成
        token = create_access_token(data)
        
        # トークンがデコードできることを確認
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded.user_id == "test-user-id"
        assert decoded.username == "testuser"
        assert decoded.role == "user"
    
    def test_create_token_with_custom_expiration(self):
        """カスタム有効期限でトークンを作成できることを確認"""
        data = {
            "user_id": "test-user-id",
            "username": "testuser",
            "role": "admin"
        }
        
        # 1時間の有効期限
        token = create_access_token(data, expires_delta=timedelta(hours=1))
        
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded.role == "admin"
    
    def test_invalid_token_returns_none(self):
        """無効なトークンのデコードがNoneを返すことを確認"""
        # 無効なトークン
        invalid_token = "invalid.token.here"
        
        decoded = decode_access_token(invalid_token)
        
        assert decoded is None
