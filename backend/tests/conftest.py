"""
テスト用設定・フィクスチャ

motoを使用してDynamoDBをモック化する。
"""

import os
import pytest
import boto3
from moto import mock_dynamodb

# テスト環境の設定
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["AWS_REGION"] = "ap-northeast-1"
os.environ["USERS_TABLE"] = "test-users"
os.environ["POSTS_TABLE"] = "test-posts"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="function")
def aws_credentials():
    """AWSクレデンシャルのモック"""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="function")
def dynamodb_tables(aws_credentials):
    """
    DynamoDBテーブルをモック化するフィクスチャ
    
    テスト用にユーザーテーブルと投稿テーブルを作成する。
    """
    with mock_dynamodb():
        # DynamoDBリソースを作成
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
        
        yield dynamodb
