"""
ユーザーサービスのテスト

ユーザーのCRUD操作のテスト。
"""

import pytest
from moto import mock_dynamodb
import boto3

from app.models.user import UserCreate, UserUpdate, UserRole
from app.services.user_service import UserService


def create_test_tables():
    """テスト用のDynamoDBテーブルを作成"""
    dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    
    # ユーザーテーブルを作成
    dynamodb.create_table(
        TableName="test-users",
        KeySchema=[
            {"AttributeName": "user_id", "KeyType": "HASH"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "username", "AttributeType": "S"}
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "username-index",
                "KeySchema": [
                    {"AttributeName": "username", "KeyType": "HASH"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                }
            }
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        }
    )
    return dynamodb


class TestUserService:
    """ユーザーサービスのテストクラス"""
    
    @mock_dynamodb
    def test_create_user(self):
        """ユーザーの作成が正しく動作することを確認"""
        create_test_tables()
        service = UserService()
        
        # ユーザー作成データ
        user_data = UserCreate(
            username="testuser",
            password="password123",
            role=UserRole.USER
        )
        
        # ユーザーを作成
        user = service.create_user(user_data)
        
        # 作成されたユーザーを確認
        assert user.username == "testuser"
        assert user.role == UserRole.USER
        assert user.user_id is not None
    
    @mock_dynamodb
    def test_create_admin_user(self):
        """管理者ユーザーの作成が正しく動作することを確認"""
        create_test_tables()
        service = UserService()
        
        # 管理者ユーザー作成データ
        user_data = UserCreate(
            username="adminuser",
            password="adminpass123",
            role=UserRole.ADMIN
        )
        
        # ユーザーを作成
        user = service.create_user(user_data)
        
        # 管理者権限を確認
        assert user.role == UserRole.ADMIN
    
    @mock_dynamodb
    def test_duplicate_username_raises_error(self):
        """重複するユーザー名でエラーが発生することを確認"""
        create_test_tables()
        service = UserService()
        
        # 最初のユーザーを作成
        user_data = UserCreate(
            username="duplicateuser",
            password="password123",
            role=UserRole.USER
        )
        service.create_user(user_data)
        
        # 同じユーザー名で作成しようとする
        with pytest.raises(ValueError) as exc_info:
            service.create_user(user_data)
        
        assert "既に使用されています" in str(exc_info.value)
    
    @mock_dynamodb
    def test_get_user_by_id(self):
        """ユーザーIDでの取得が正しく動作することを確認"""
        create_test_tables()
        service = UserService()
        
        # ユーザーを作成
        user_data = UserCreate(
            username="getuser",
            password="password123",
            role=UserRole.USER
        )
        created_user = service.create_user(user_data)
        
        # IDで取得
        user = service.get_user_by_id(created_user.user_id)
        
        assert user is not None
        assert user.username == "getuser"
    
    @mock_dynamodb
    def test_get_user_by_username(self):
        """ユーザー名での取得が正しく動作することを確認"""
        create_test_tables()
        service = UserService()
        
        # ユーザーを作成
        user_data = UserCreate(
            username="usernameget",
            password="password123",
            role=UserRole.USER
        )
        service.create_user(user_data)
        
        # ユーザー名で取得
        user = service.get_user_by_username("usernameget")
        
        assert user is not None
        assert user.username == "usernameget"
    
    @mock_dynamodb
    def test_update_user(self):
        """ユーザーの更新が正しく動作することを確認"""
        create_test_tables()
        service = UserService()
        
        # ユーザーを作成
        user_data = UserCreate(
            username="updateuser",
            password="password123",
            role=UserRole.USER
        )
        created_user = service.create_user(user_data)
        
        # 更新データ
        update_data = UserUpdate(
            username="updateduser",
            role=UserRole.ADMIN
        )
        
        # 更新
        updated_user = service.update_user(created_user.user_id, update_data)
        
        assert updated_user is not None
        assert updated_user.username == "updateduser"
        assert updated_user.role == UserRole.ADMIN
    
    @mock_dynamodb
    def test_delete_user(self):
        """ユーザーの削除が正しく動作することを確認"""
        create_test_tables()
        service = UserService()
        
        # ユーザーを作成
        user_data = UserCreate(
            username="deleteuser",
            password="password123",
            role=UserRole.USER
        )
        created_user = service.create_user(user_data)
        
        # 削除
        result = service.delete_user(created_user.user_id)
        
        assert result is True
        
        # 削除されていることを確認
        user = service.get_user_by_id(created_user.user_id)
        assert user is None
    
    @mock_dynamodb
    def test_authenticate_user(self):
        """ユーザー認証が正しく動作することを確認"""
        create_test_tables()
        service = UserService()
        
        # ユーザーを作成
        user_data = UserCreate(
            username="authuser",
            password="correctpassword",
            role=UserRole.USER
        )
        service.create_user(user_data)
        
        # 正しいパスワードで認証
        user = service.authenticate_user("authuser", "correctpassword")
        assert user is not None
        assert user.username == "authuser"
        
        # 間違ったパスワードで認証
        user = service.authenticate_user("authuser", "wrongpassword")
        assert user is None
    
    @mock_dynamodb
    def test_get_all_users(self):
        """全ユーザーの取得が正しく動作することを確認"""
        create_test_tables()
        service = UserService()
        
        # 複数のユーザーを作成
        for i in range(3):
            user_data = UserCreate(
                username=f"user{i}",
                password="password123",
                role=UserRole.USER
            )
            service.create_user(user_data)
        
        # 全ユーザーを取得
        users = service.get_all_users()
        
        assert len(users) == 3
