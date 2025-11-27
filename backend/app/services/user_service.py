"""
ユーザーサービス

ユーザーのCRUD操作を提供するサービス。
DynamoDBを使用してユーザーデータを管理する。
"""

import uuid
from datetime import datetime
from typing import Optional, List
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from app.models.user import UserCreate, UserUpdate, UserResponse, UserInDB, UserRole
from app.services.database import get_users_table
from app.services.auth import get_password_hash, verify_password


class UserService:
    """
    ユーザー管理サービスクラス
    
    ユーザーの作成・取得・更新・削除の操作を提供する。
    """
    
    def __init__(self):
        """サービスの初期化"""
        pass
    
    def _get_table(self):
        """
        ユーザーテーブルを取得する（遅延読み込み）
        
        Returns:
            boto3.Table: ユーザーテーブル
        """
        return get_users_table()
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        新規ユーザーを作成する
        
        Args:
            user_data: ユーザー作成データ
        
        Returns:
            UserResponse: 作成されたユーザー情報
        
        Raises:
            ValueError: ユーザー名が既に存在する場合
        """
        table = self._get_table()
        
        # ユーザー名の重複チェック
        if self.get_user_by_username(user_data.username):
            raise ValueError("このユーザー名は既に使用されています")
        
        # 現在時刻
        now = datetime.utcnow().isoformat()
        
        # ユーザーIDを生成
        user_id = str(uuid.uuid4())
        
        # パスワードをハッシュ化
        hashed_password = get_password_hash(user_data.password)
        
        # DynamoDBに保存するアイテム
        item = {
            "user_id": user_id,
            "username": user_data.username,
            "hashed_password": hashed_password,
            "role": user_data.role.value,
            "created_at": now,
            "updated_at": now,
        }
        
        table.put_item(Item=item)
        
        return UserResponse(
            user_id=user_id,
            username=user_data.username,
            role=user_data.role,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
        )
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """
        ユーザーIDでユーザーを取得する
        
        Args:
            user_id: ユーザーID
        
        Returns:
            UserInDB: ユーザー情報、見つからない場合はNone
        """
        table = self._get_table()
        
        response = table.get_item(Key={"user_id": user_id})
        
        item = response.get("Item")
        if not item:
            return None
        
        return self._item_to_user_in_db(item)
    
    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """
        ユーザー名でユーザーを取得する
        
        Args:
            username: ユーザー名
        
        Returns:
            UserInDB: ユーザー情報、見つからない場合はNone
        """
        table = self._get_table()
        
        # GSI（グローバルセカンダリインデックス）を使用してクエリ
        response = table.query(
            IndexName="username-index",
            KeyConditionExpression=Key("username").eq(username)
        )
        
        items = response.get("Items", [])
        if not items:
            return None
        
        return self._item_to_user_in_db(items[0])
    
    def get_all_users(self) -> List[UserResponse]:
        """
        全ユーザーを取得する
        
        Returns:
            List[UserResponse]: ユーザーリスト
        """
        table = self._get_table()
        
        response = table.scan()
        items = response.get("Items", [])
        
        return [self._item_to_user_response(item) for item in items]
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """
        ユーザー情報を更新する
        
        Args:
            user_id: 更新対象のユーザーID
            user_data: 更新データ
        
        Returns:
            UserResponse: 更新後のユーザー情報、ユーザーが存在しない場合はNone
        
        Raises:
            ValueError: ユーザー名が既に使用されている場合
        """
        table = self._get_table()
        
        # 既存ユーザーを取得
        existing_user = self.get_user_by_id(user_id)
        if not existing_user:
            return None
        
        # ユーザー名の重複チェック（変更する場合）
        if user_data.username and user_data.username != existing_user.username:
            if self.get_user_by_username(user_data.username):
                raise ValueError("このユーザー名は既に使用されています")
        
        # 更新式を構築
        update_expression_parts = []
        expression_attribute_values = {}
        expression_attribute_names = {}
        
        if user_data.username:
            update_expression_parts.append("#username = :username")
            expression_attribute_values[":username"] = user_data.username
            expression_attribute_names["#username"] = "username"
        
        if user_data.password:
            update_expression_parts.append("hashed_password = :hashed_password")
            expression_attribute_values[":hashed_password"] = get_password_hash(user_data.password)
        
        if user_data.role:
            update_expression_parts.append("#role = :role")
            expression_attribute_values[":role"] = user_data.role.value
            expression_attribute_names["#role"] = "role"
        
        # 更新日時を設定
        now = datetime.utcnow().isoformat()
        update_expression_parts.append("updated_at = :updated_at")
        expression_attribute_values[":updated_at"] = now
        
        update_expression = "SET " + ", ".join(update_expression_parts)
        
        # 更新実行
        update_params = {
            "Key": {"user_id": user_id},
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": expression_attribute_values,
            "ReturnValues": "ALL_NEW"
        }
        
        if expression_attribute_names:
            update_params["ExpressionAttributeNames"] = expression_attribute_names
        
        response = table.update_item(**update_params)
        
        return self._item_to_user_response(response["Attributes"])
    
    def delete_user(self, user_id: str) -> bool:
        """
        ユーザーを削除する
        
        Args:
            user_id: 削除対象のユーザーID
        
        Returns:
            bool: 削除に成功した場合True
        """
        table = self._get_table()
        
        # 既存ユーザーを確認
        if not self.get_user_by_id(user_id):
            return False
        
        table.delete_item(Key={"user_id": user_id})
        return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """
        ユーザーを認証する
        
        Args:
            username: ユーザー名
            password: パスワード
        
        Returns:
            UserInDB: 認証に成功した場合はユーザー情報、失敗した場合はNone
        """
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def _item_to_user_in_db(self, item: dict) -> UserInDB:
        """
        DynamoDBアイテムをUserInDBモデルに変換する
        
        Args:
            item: DynamoDBアイテム
        
        Returns:
            UserInDB: ユーザーモデル
        """
        return UserInDB(
            user_id=item["user_id"],
            username=item["username"],
            hashed_password=item["hashed_password"],
            role=UserRole(item["role"]),
            created_at=datetime.fromisoformat(item["created_at"]),
            updated_at=datetime.fromisoformat(item["updated_at"]),
        )
    
    def _item_to_user_response(self, item: dict) -> UserResponse:
        """
        DynamoDBアイテムをUserResponseモデルに変換する
        
        Args:
            item: DynamoDBアイテム
        
        Returns:
            UserResponse: ユーザーレスポンスモデル
        """
        return UserResponse(
            user_id=item["user_id"],
            username=item["username"],
            role=UserRole(item["role"]),
            created_at=datetime.fromisoformat(item["created_at"]),
            updated_at=datetime.fromisoformat(item["updated_at"]),
        )


# シングルトンインスタンス
user_service = UserService()
