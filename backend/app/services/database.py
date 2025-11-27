"""
データベースサービス

DynamoDBとの接続・操作を提供するサービス。
テーブルの初期化と接続管理を行う。
"""

import boto3
from botocore.config import Config
from app.config import get_settings


def get_dynamodb_resource():
    """
    DynamoDBリソースを取得する
    
    設定に基づいてDynamoDBリソースを作成し返す。
    ローカル開発時はエンドポイントURLを指定可能。
    
    Returns:
        boto3.resource: DynamoDBリソースオブジェクト
    """
    settings = get_settings()
    # リトライ設定
    config = Config(
        retries={
            'max_attempts': 3,
            'mode': 'standard'
        }
    )
    
    # エンドポイントURLが指定されている場合（ローカル開発用）
    if settings.DYNAMODB_ENDPOINT:
        return boto3.resource(
            'dynamodb',
            endpoint_url=settings.DYNAMODB_ENDPOINT,
            region_name=settings.AWS_REGION,
            config=config
        )
    
    # 本番環境用
    return boto3.resource(
        'dynamodb',
        region_name=settings.AWS_REGION,
        config=config
    )


def get_users_table():
    """
    ユーザーテーブルを取得する
    
    Returns:
        boto3.Table: ユーザーテーブルオブジェクト
    """
    settings = get_settings()
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(settings.USERS_TABLE)


def get_posts_table():
    """
    投稿テーブルを取得する
    
    Returns:
        boto3.Table: 投稿テーブルオブジェクト
    """
    settings = get_settings()
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(settings.POSTS_TABLE)
