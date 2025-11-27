"""
投稿サービスのテスト

投稿のCRUD操作のテスト。
"""

import pytest
from moto import mock_dynamodb
import boto3

from app.models.post import PostCreate, PostUpdate
from app.services.post_service import PostService


def create_test_tables():
    """テスト用のDynamoDBテーブルを作成"""
    dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    
    # 投稿テーブルを作成
    dynamodb.create_table(
        TableName="test-posts",
        KeySchema=[
            {"AttributeName": "post_id", "KeyType": "HASH"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "post_id", "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "created_at", "AttributeType": "S"}
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "user_id-index",
                "KeySchema": [
                    {"AttributeName": "user_id", "KeyType": "HASH"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                }
            },
            {
                "IndexName": "pk-created_at-index",
                "KeySchema": [
                    {"AttributeName": "pk", "KeyType": "HASH"},
                    {"AttributeName": "created_at", "KeyType": "RANGE"}
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


class TestPostService:
    """投稿サービスのテストクラス"""
    
    @mock_dynamodb
    def test_create_post(self):
        """投稿の作成が正しく動作することを確認"""
        create_test_tables()
        service = PostService()
        
        # 投稿作成データ
        post_data = PostCreate(
            title="テスト投稿",
            message="これはテストメッセージです。"
        )
        
        # 投稿を作成
        post = service.create_post(
            post_data=post_data,
            user_id="test-user-id",
            username="testuser"
        )
        
        # 作成された投稿を確認
        assert post.title == "テスト投稿"
        assert post.message == "これはテストメッセージです。"
        assert post.user_id == "test-user-id"
        assert post.username == "testuser"
        assert post.post_id is not None
    
    @mock_dynamodb
    def test_get_post_by_id(self):
        """投稿IDでの取得が正しく動作することを確認"""
        create_test_tables()
        service = PostService()
        
        # 投稿を作成
        post_data = PostCreate(
            title="取得テスト",
            message="取得テストのメッセージ"
        )
        created_post = service.create_post(
            post_data=post_data,
            user_id="test-user-id",
            username="testuser"
        )
        
        # IDで取得
        post = service.get_post_by_id(created_post.post_id)
        
        assert post is not None
        assert post.title == "取得テスト"
    
    @mock_dynamodb
    def test_get_nonexistent_post_returns_none(self):
        """存在しない投稿の取得がNoneを返すことを確認"""
        create_test_tables()
        service = PostService()
        
        post = service.get_post_by_id("nonexistent-id")
        
        assert post is None
    
    @mock_dynamodb
    def test_update_post(self):
        """投稿の更新が正しく動作することを確認"""
        create_test_tables()
        service = PostService()
        
        # 投稿を作成
        post_data = PostCreate(
            title="更新前タイトル",
            message="更新前メッセージ"
        )
        created_post = service.create_post(
            post_data=post_data,
            user_id="test-user-id",
            username="testuser"
        )
        
        # 更新データ
        update_data = PostUpdate(
            title="更新後タイトル",
            message="更新後メッセージ"
        )
        
        # 更新
        updated_post = service.update_post(created_post.post_id, update_data)
        
        assert updated_post is not None
        assert updated_post.title == "更新後タイトル"
        assert updated_post.message == "更新後メッセージ"
    
    @mock_dynamodb
    def test_update_partial(self):
        """部分的な更新が正しく動作することを確認"""
        create_test_tables()
        service = PostService()
        
        # 投稿を作成
        post_data = PostCreate(
            title="元のタイトル",
            message="元のメッセージ"
        )
        created_post = service.create_post(
            post_data=post_data,
            user_id="test-user-id",
            username="testuser"
        )
        
        # タイトルのみ更新
        update_data = PostUpdate(title="新しいタイトル")
        updated_post = service.update_post(created_post.post_id, update_data)
        
        assert updated_post.title == "新しいタイトル"
        assert updated_post.message == "元のメッセージ"
    
    @mock_dynamodb
    def test_delete_post(self):
        """投稿の削除が正しく動作することを確認"""
        create_test_tables()
        service = PostService()
        
        # 投稿を作成
        post_data = PostCreate(
            title="削除テスト",
            message="削除テストのメッセージ"
        )
        created_post = service.create_post(
            post_data=post_data,
            user_id="test-user-id",
            username="testuser"
        )
        
        # 削除
        result = service.delete_post(created_post.post_id)
        
        assert result is True
        
        # 削除されていることを確認
        post = service.get_post_by_id(created_post.post_id)
        assert post is None
    
    @mock_dynamodb
    def test_delete_nonexistent_post(self):
        """存在しない投稿の削除がFalseを返すことを確認"""
        create_test_tables()
        service = PostService()
        
        result = service.delete_post("nonexistent-id")
        
        assert result is False
    
    @mock_dynamodb
    def test_get_all_posts(self):
        """全投稿の取得が正しく動作することを確認"""
        create_test_tables()
        service = PostService()
        
        # 複数の投稿を作成
        for i in range(5):
            post_data = PostCreate(
                title=f"投稿{i}",
                message=f"メッセージ{i}"
            )
            service.create_post(
                post_data=post_data,
                user_id="test-user-id",
                username="testuser"
            )
        
        # 全投稿を取得
        posts = service.get_all_posts()
        
        assert len(posts) == 5
    
    @mock_dynamodb
    def test_get_all_posts_with_limit(self):
        """制限付きの全投稿取得が正しく動作することを確認"""
        create_test_tables()
        service = PostService()
        
        # 複数の投稿を作成
        for i in range(10):
            post_data = PostCreate(
                title=f"投稿{i}",
                message=f"メッセージ{i}"
            )
            service.create_post(
                post_data=post_data,
                user_id="test-user-id",
                username="testuser"
            )
        
        # 制限付きで取得
        posts = service.get_all_posts(limit=5)
        
        assert len(posts) == 5
    
    @mock_dynamodb
    def test_get_posts_by_user(self):
        """ユーザー別投稿の取得が正しく動作することを確認"""
        create_test_tables()
        service = PostService()
        
        # ユーザー1の投稿
        for i in range(3):
            post_data = PostCreate(
                title=f"ユーザー1の投稿{i}",
                message=f"メッセージ{i}"
            )
            service.create_post(
                post_data=post_data,
                user_id="user-1",
                username="user1"
            )
        
        # ユーザー2の投稿
        for i in range(2):
            post_data = PostCreate(
                title=f"ユーザー2の投稿{i}",
                message=f"メッセージ{i}"
            )
            service.create_post(
                post_data=post_data,
                user_id="user-2",
                username="user2"
            )
        
        # ユーザー1の投稿を取得
        posts = service.get_posts_by_user("user-1")
        
        assert len(posts) == 3
        for post in posts:
            assert post.user_id == "user-1"
