"""
セキュリティコード管理モジュール
アカウント情報の保存・読み込み・管理機能を提供
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from .crypto_utils import CryptoUtils


class SecurityManager:
    """セキュリティコード管理クラス"""

    def __init__(
        self, data_file: str = "data/accounts.json", password: Optional[str] = None
    ):
        """
        初期化

        Args:
            data_file: データファイルのパス
            password: 暗号化用パスワード
        """
        self.data_file = data_file
        self.crypto = CryptoUtils(password)
        self.accounts: List[Dict[str, Any]] = []
        self._ensure_data_directory()
        self._load_accounts()

    def _ensure_data_directory(self) -> None:
        """データディレクトリが存在することを確認"""
        data_dir = os.path.dirname(self.data_file)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _load_accounts(self) -> None:
        """アカウントデータを読み込み"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.accounts = data.get("accounts", [])
            else:
                self.accounts = []
                self._save_accounts()
        except Exception as e:
            print(f"アカウントデータ読み込みエラー: {str(e)}")
            self.accounts = []

    def _save_accounts(self) -> None:
        """アカウントデータを保存"""
        try:
            data = {
                "accounts": self.accounts,
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"アカウントデータ保存エラー: {str(e)}")

    def add_account(
        self, device_name: str, account_name: str, issuer: str, secret: str
    ) -> str:
        """
        新しいアカウントを追加

        Args:
            device_name: デバイス名
            account_name: アカウント名
            issuer: 発行者名
            secret: セキュリティコード

        Returns:
            アカウントID
        """
        account_id = str(uuid.uuid4())

        account_data = {
            "id": account_id,
            "device_name": device_name,
            "account_name": account_name,
            "issuer": issuer,
            "secret": secret,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # 暗号化して保存
        encrypted_account = self.crypto.encrypt_account_data(account_data)
        self.accounts.append(encrypted_account)
        self._save_accounts()

        return account_id

    def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        アカウント情報を取得（復号化済み）

        Args:
            account_id: アカウントID

        Returns:
            アカウント情報（復号化済み）
        """
        for account in self.accounts:
            if account["id"] == account_id:
                return self.crypto.decrypt_account_data(account)
        return None

    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """
        全てのアカウント情報を取得（復号化済み）

        Returns:
            アカウント情報のリスト（復号化済み）
        """
        decrypted_accounts = []
        for account in self.accounts:
            decrypted_account = self.crypto.decrypt_account_data(account)
            decrypted_accounts.append(decrypted_account)
        return decrypted_accounts

    def update_account(self, account_id: str, **kwargs: Any) -> bool:
        """
        アカウント情報を更新

        Args:
            account_id: アカウントID
            **kwargs: 更新するフィールド

        Returns:
            更新成功の場合True
        """
        for i, account in enumerate(self.accounts):
            if account["id"] == account_id:
                # 復号化
                decrypted_account = self.crypto.decrypt_account_data(account)

                # 更新
                for key, value in kwargs.items():
                    if key in decrypted_account:
                        decrypted_account[key] = value

                decrypted_account["updated_at"] = datetime.now().isoformat()

                # 再暗号化して保存
                encrypted_account = self.crypto.encrypt_account_data(decrypted_account)
                self.accounts[i] = encrypted_account
                self._save_accounts()
                return True
        return False

    def delete_account(self, account_id: str) -> bool:
        """
        アカウントを削除

        Args:
            account_id: アカウントID

        Returns:
            削除成功の場合True
        """
        for i, account in enumerate(self.accounts):
            if account["id"] == account_id:
                del self.accounts[i]
                self._save_accounts()
                return True
        return False

    def list_accounts(self) -> List[Dict[str, Any]]:
        """
        アカウント一覧を取得（セキュリティコードは含まない）

        Returns:
            アカウント一覧
        """
        account_list = []
        for account in self.accounts:
            decrypted_account = self.crypto.decrypt_account_data(account)
            # セキュリティコードを除外
            safe_account = {
                "id": decrypted_account["id"],
                "device_name": decrypted_account["device_name"],
                "account_name": decrypted_account["account_name"],
                "issuer": decrypted_account["issuer"],
                "created_at": decrypted_account["created_at"],
                "updated_at": decrypted_account["updated_at"],
            }
            account_list.append(safe_account)
        return account_list

    def search_accounts(self, keyword: str) -> List[Dict[str, Any]]:
        """
        キーワードでアカウントを検索

        Args:
            keyword: 検索キーワード

        Returns:
            マッチしたアカウントのリスト
        """
        keyword_lower = keyword.lower()
        matching_accounts = []

        for account in self.accounts:
            decrypted_account = self.crypto.decrypt_account_data(account)

            # 検索対象フィールド
            search_fields = [
                decrypted_account.get("device_name", ""),
                decrypted_account.get("account_name", ""),
                decrypted_account.get("issuer", ""),
            ]

            # キーワードマッチング
            if any(keyword_lower in field.lower() for field in search_fields):
                # セキュリティコードを除外
                safe_account = {
                    "id": decrypted_account["id"],
                    "device_name": decrypted_account["device_name"],
                    "account_name": decrypted_account["account_name"],
                    "issuer": decrypted_account["issuer"],
                    "created_at": decrypted_account["created_at"],
                    "updated_at": decrypted_account["updated_at"],
                }
                matching_accounts.append(safe_account)

        return matching_accounts

    def get_account_count(self) -> int:
        """
        登録済みアカウント数を取得

        Returns:
            アカウント数
        """
        return len(self.accounts)

    def backup_accounts(self, backup_file: str) -> bool:
        """
        アカウントデータをバックアップ

        Args:
            backup_file: バックアップファイルのパス

        Returns:
            バックアップ成功の場合True
        """
        try:
            import shutil

            shutil.copy2(self.data_file, backup_file)
            return True
        except Exception as e:
            print(f"バックアップエラー: {str(e)}")
            return False

    def restore_accounts(self, backup_file: str) -> bool:
        """
        アカウントデータを復元

        Args:
            backup_file: バックアップファイルのパス

        Returns:
            復元成功の場合True
        """
        try:
            if not os.path.exists(backup_file):
                print(f"バックアップファイルが見つかりません: {backup_file}")
                return False

            import shutil

            shutil.copy2(backup_file, self.data_file)
            self._load_accounts()
            return True
        except Exception as e:
            print(f"復元エラー: {str(e)}")
            return False

    def clear_all_accounts(self) -> bool:
        """
        全てのアカウントを削除

        Returns:
            削除成功の場合True
        """
        try:
            self.accounts = []
            self._save_accounts()
            return True
        except Exception as e:
            print(f"全削除エラー: {str(e)}")
            return False


def test_security_manager() -> None:
    """セキュリティマネージャーのテスト"""
    # テスト用の固定パスワードを使用
    manager = SecurityManager("test_accounts.json", password="test_password_for_demo")

    print("セキュリティマネージャーテスト")
    print("-" * 40)

    # アカウント追加テスト
    account_id = manager.add_account(
        device_name="Test Device",
        account_name="Test Account",
        issuer="Test Issuer",
        secret="JBSWY3DPEHPK3PXP",
    )
    print(f"アカウント追加: {account_id}")

    # アカウント取得テスト
    account = manager.get_account(account_id)
    if account:
        print(f"アカウント取得: {account['account_name']}")

    # アカウント一覧テスト
    accounts = manager.list_accounts()
    print(f"アカウント数: {len(accounts)}")

    # アカウント更新テスト
    success = manager.update_account(account_id, account_name="Updated Account")
    print(f"アカウント更新: {'成功' if success else '失敗'}")

    # アカウント削除テスト
    success = manager.delete_account(account_id)
    print(f"アカウント削除: {'成功' if success else '失敗'}")

    # テストファイルを削除
    if os.path.exists("test_accounts.json"):
        os.remove("test_accounts.json")


if __name__ == "__main__":
    test_security_manager()
