"""
投稿サービス

投稿のCRUD操作を提供するサービス。
DynamoDBを使用して投稿データを管理する。
"""

import uuid
from datetime import datetime
from typing import Optional, List
from boto3.dynamodb.conditions import Key

from app.models.post import PostCreate, PostUpdate, PostResponse
from app.services.database import get_posts_table


class PostService:
    """
    投稿管理サービスクラス
    
    投稿の作成・取得・更新・削除の操作を提供する。
    """
    
    def __init__(self):
        """サービスの初期化"""
        pass
    
    def _get_table(self):
        """
        投稿テーブルを取得する（遅延読み込み）
        
        Returns:
            boto3.Table: 投稿テーブル
        """
        return get_posts_table()
    
    def create_post(self, post_data: PostCreate, user_id: str, username: str) -> PostResponse:
        """
        新規投稿を作成する
        
        Args:
            post_data: 投稿作成データ
            user_id: 投稿者のユーザーID
            username: 投稿者のユーザー名
        
        Returns:
            PostResponse: 作成された投稿情報
        """
        table = self._get_table()
        
        # 現在時刻
        now = datetime.utcnow().isoformat()
        
        # 投稿IDを生成
        post_id = str(uuid.uuid4())
        
        # DynamoDBに保存するアイテム
        item = {
            "post_id": post_id,
            "user_id": user_id,
            "username": username,
            "title": post_data.title,
            "message": post_data.message,
            "created_at": now,
            "updated_at": now,
            # ソート用のパーティションキー（全投稿を時系列で取得するため）
            "pk": "POST",
        }
        
        table.put_item(Item=item)
        
        return PostResponse(
            post_id=post_id,
            user_id=user_id,
            username=username,
            title=post_data.title,
            message=post_data.message,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
        )
    
    def get_post_by_id(self, post_id: str) -> Optional[PostResponse]:
        """
        投稿IDで投稿を取得する
        
        Args:
            post_id: 投稿ID
        
        Returns:
            PostResponse: 投稿情報、見つからない場合はNone
        """
        table = self._get_table()
        
        response = table.get_item(Key={"post_id": post_id})
        
        item = response.get("Item")
        if not item:
            return None
        
        return self._item_to_post_response(item)
    
    def get_all_posts(self, limit: int = 100) -> List[PostResponse]:
        """
        全投稿を取得する（作成日時の降順）
        
        Args:
            limit: 取得する最大件数
        
        Returns:
            List[PostResponse]: 投稿リスト
        """
        table = self._get_table()
        
        # GSI（グローバルセカンダリインデックス）を使用してクエリ
        response = table.query(
            IndexName="pk-created_at-index",
            KeyConditionExpression=Key("pk").eq("POST"),
            ScanIndexForward=False,  # 降順（新しい順）
            Limit=limit
        )
        
        items = response.get("Items", [])
        
        return [self._item_to_post_response(item) for item in items]
    
    def get_posts_by_user(self, user_id: str) -> List[PostResponse]:
        """
        特定ユーザーの投稿を取得する
        
        Args:
            user_id: ユーザーID
        
        Returns:
            List[PostResponse]: 投稿リスト
        """
        table = self._get_table()
        
        # GSI（グローバルセカンダリインデックス）を使用してクエリ
        response = table.query(
            IndexName="user_id-index",
            KeyConditionExpression=Key("user_id").eq(user_id)
        )
        
        items = response.get("Items", [])
        
        return [self._item_to_post_response(item) for item in items]
    
    def update_post(self, post_id: str, post_data: PostUpdate) -> Optional[PostResponse]:
        """
        投稿を更新する
        
        Args:
            post_id: 更新対象の投稿ID
            post_data: 更新データ
        
        Returns:
            PostResponse: 更新後の投稿情報、投稿が存在しない場合はNone
        """
        table = self._get_table()
        
        # 既存投稿を確認
        existing_post = self.get_post_by_id(post_id)
        if not existing_post:
            return None
        
        # 更新式を構築
        update_expression_parts = []
        expression_attribute_values = {}
        expression_attribute_names = {}
        
        if post_data.title:
            update_expression_parts.append("title = :title")
            expression_attribute_values[":title"] = post_data.title
        
        if post_data.message:
            update_expression_parts.append("message = :message")
            expression_attribute_values[":message"] = post_data.message
        
        # 更新がない場合は何もしない
        if not update_expression_parts:
            return existing_post
        
        # 更新日時を設定
        now = datetime.utcnow().isoformat()
        update_expression_parts.append("updated_at = :updated_at")
        expression_attribute_values[":updated_at"] = now
        
        update_expression = "SET " + ", ".join(update_expression_parts)
        
        # 更新実行
        update_params = {
            "Key": {"post_id": post_id},
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": expression_attribute_values,
            "ReturnValues": "ALL_NEW"
        }
        
        if expression_attribute_names:
            update_params["ExpressionAttributeNames"] = expression_attribute_names
        
        response = table.update_item(**update_params)
        
        return self._item_to_post_response(response["Attributes"])
    
    def delete_post(self, post_id: str) -> bool:
        """
        投稿を削除する
        
        Args:
            post_id: 削除対象の投稿ID
        
        Returns:
            bool: 削除に成功した場合True
        """
        table = self._get_table()
        
        # 既存投稿を確認
        if not self.get_post_by_id(post_id):
            return False
        
        table.delete_item(Key={"post_id": post_id})
        return True
    
    def _item_to_post_response(self, item: dict) -> PostResponse:
        """
        DynamoDBアイテムをPostResponseモデルに変換する
        
        Args:
            item: DynamoDBアイテム
        
        Returns:
            PostResponse: 投稿レスポンスモデル
        """
        return PostResponse(
            post_id=item["post_id"],
            user_id=item["user_id"],
            username=item["username"],
            title=item["title"],
            message=item["message"],
            created_at=datetime.fromisoformat(item["created_at"]),
            updated_at=datetime.fromisoformat(item["updated_at"]),
        )


# シングルトンインスタンス
post_service = PostService()
