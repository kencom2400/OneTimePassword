"""
SecurityManagerクラスのテスト
"""

import pytest
import os
import tempfile
from unittest.mock import patch, Mock
from src.security_manager import SecurityManager


class TestSecurityManager:
    """SecurityManagerクラスのテスト"""

    @pytest.fixture
    def temp_data_dir(self):
        """一時データディレクトリ"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def security_manager(self, temp_data_dir):
        """テスト用SecurityManagerインスタンス"""
        data_file = os.path.join(temp_data_dir, "test_accounts.json")
        # テスト用の固定パスワードを使用
        return SecurityManager(
            data_file=data_file, password="test_password_for_unit_tests"
        )

    def test_add_account_normal(self, security_manager):
        """TC-SM-001: 正常なアカウント追加"""
        account_id = security_manager.add_account(
            device_name="Test Device",
            account_name="test@example.com",
            issuer="TestService",
            secret="JBSWY3DPEHPK3PXP",
        )

        assert isinstance(account_id, str)
        assert len(account_id) > 0

        # アカウントが正しく追加されたか確認
        account = security_manager.get_account(account_id)
        assert account is not None
        assert account["device_name"] == "Test Device"
        assert account["account_name"] == "test@example.com"
        assert account["issuer"] == "TestService"
        assert account["secret"] == "JBSWY3DPEHPK3PXP"

    def test_add_account_minimum_length_name(self, security_manager):
        """TC-SM-002: 最小長アカウント名（1文字）"""
        account_id = security_manager.add_account(
            device_name="A",
            account_name="a@b.c",
            issuer="Test",
            secret="JBSWY3DPEHPK3PXP",
        )

        assert isinstance(account_id, str)
        account = security_manager.get_account(account_id)
        assert account is not None

    def test_add_account_maximum_length_name(self, security_manager):
        """TC-SM-003: 最大長アカウント名（100文字）"""
        long_name = "a" * 100
        account_id = security_manager.add_account(
            device_name=long_name,
            account_name=long_name + "@example.com",
            issuer=long_name,
            secret="JBSWY3DPEHPK3PXP",
        )

        assert isinstance(account_id, str)
        account = security_manager.get_account(account_id)
        assert account is not None

    def test_get_account_normal(self, security_manager):
        """TC-SM-004: 正常なアカウント取得"""
        account_id = security_manager.add_account(
            device_name="Test Device",
            account_name="test@example.com",
            issuer="TestService",
            secret="JBSWY3DPEHPK3PXP",
        )

        account = security_manager.get_account(account_id)
        assert account is not None
        assert account["id"] == account_id
        assert account["device_name"] == "Test Device"
        assert account["account_name"] == "test@example.com"

    def test_get_account_not_found(self, security_manager):
        """TC-SM-005: 存在しないアカウント取得"""
        account = security_manager.get_account("non-existent-id")
        assert account is None

    def test_get_account_invalid_id(self, security_manager):
        """TC-SM-006: 無効なIDでのアカウント取得"""
        account = security_manager.get_account("")
        assert account is None

        account = security_manager.get_account(None)
        assert account is None

    def test_list_accounts_normal(self, security_manager):
        """TC-SM-007: 正常なアカウント一覧取得"""
        # 複数のアカウントを追加
        security_manager.add_account(
            "Device1", "user1@example.com", "Service1", "SECRET1"
        )
        security_manager.add_account(
            "Device2", "user2@example.com", "Service2", "SECRET2"
        )

        accounts = security_manager.list_accounts()
        assert len(accounts) == 2

        # セキュリティコードが含まれていないことを確認
        for account in accounts:
            assert "secret" not in account
            assert "id" in account
            assert "device_name" in account
            assert "account_name" in account
            assert "issuer" in account

    def test_list_accounts_empty(self, security_manager):
        """TC-SM-008: 空のアカウント一覧"""
        accounts = security_manager.list_accounts()
        assert accounts == []

    def test_update_account_normal(self, security_manager):
        """TC-SM-009: 正常なアカウント更新"""
        account_id = security_manager.add_account(
            device_name="Test Device",
            account_name="test@example.com",
            issuer="TestService",
            secret="JBSWY3DPEHPK3PXP",
        )

        success = security_manager.update_account(
            account_id, account_name="updated@example.com", issuer="UpdatedService"
        )

        assert success is True

        # 更新されたアカウントを確認
        account = security_manager.get_account(account_id)
        assert account["account_name"] == "updated@example.com"
        assert account["issuer"] == "UpdatedService"
        assert account["device_name"] == "Test Device"  # 更新されていないフィールド

    def test_update_account_not_found(self, security_manager):
        """TC-SM-010: 存在しないアカウント更新"""
        success = security_manager.update_account(
            "non-existent-id", account_name="updated@example.com"
        )
        assert success is False

    def test_update_account_invalid_id(self, security_manager):
        """TC-SM-011: 無効なIDでのアカウント更新"""
        success = security_manager.update_account(
            "", account_name="updated@example.com"
        )
        assert success is False

    def test_delete_account_normal(self, security_manager):
        """TC-SM-012: 正常なアカウント削除"""
        account_id = security_manager.add_account(
            device_name="Test Device",
            account_name="test@example.com",
            issuer="TestService",
            secret="JBSWY3DPEHPK3PXP",
        )

        success = security_manager.delete_account(account_id)
        assert success is True

        # 削除されたアカウントが取得できないことを確認
        account = security_manager.get_account(account_id)
        assert account is None

    def test_delete_account_not_found(self, security_manager):
        """TC-SM-013: 存在しないアカウント削除"""
        success = security_manager.delete_account("non-existent-id")
        assert success is False

    def test_delete_account_invalid_id(self, security_manager):
        """TC-SM-014: 無効なIDでのアカウント削除"""
        success = security_manager.delete_account("")
        assert success is False

    def test_search_accounts_normal(self, security_manager):
        """TC-SM-015: 正常なアカウント検索"""
        security_manager.add_account(
            "Device1", "user1@example.com", "Service1", "SECRET1"
        )
        security_manager.add_account(
            "Device2", "user2@example.com", "Service2", "SECRET2"
        )

        # アカウント名で検索
        results = security_manager.search_accounts("user1")
        assert len(results) == 1
        assert results[0]["account_name"] == "user1@example.com"

        # 発行者で検索
        results = security_manager.search_accounts("Service1")
        assert len(results) == 1
        assert results[0]["issuer"] == "Service1"

    def test_search_accounts_by_issuer(self, security_manager):
        """TC-SM-016: 発行者でのアカウント検索"""
        security_manager.add_account(
            "Device1", "user1@example.com", "GitHub", "SECRET1"
        )
        security_manager.add_account(
            "Device2", "user2@example.com", "Google", "SECRET2"
        )

        results = security_manager.search_accounts("GitHub")
        assert len(results) == 1
        assert results[0]["issuer"] == "GitHub"

    def test_search_accounts_not_found(self, security_manager):
        """TC-SM-017: 見つからないアカウント検索"""
        security_manager.add_account(
            "Device1", "user1@example.com", "Service1", "SECRET1"
        )

        results = security_manager.search_accounts("nonexistent")
        assert results == []

    def test_search_accounts_empty_keyword(self, security_manager):
        """TC-SM-018: 空のキーワードでの検索（全件返却）"""
        security_manager.add_account(
            "Device1", "user1@example.com", "Service1", "SECRET1"
        )
        security_manager.add_account(
            "Device2", "user2@example.com", "Service2", "SECRET2"
        )

        results = security_manager.search_accounts("")
        assert len(results) == 2
        assert results[0]["account_name"] == "user1@example.com"
        assert results[1]["account_name"] == "user2@example.com"

    def test_get_account_count_normal(self, security_manager):
        """TC-SM-019: 正常なアカウント数取得"""
        assert security_manager.get_account_count() == 0

        security_manager.add_account(
            "Device1", "user1@example.com", "Service1", "SECRET1"
        )
        assert security_manager.get_account_count() == 1

        security_manager.add_account(
            "Device2", "user2@example.com", "Service2", "SECRET2"
        )
        assert security_manager.get_account_count() == 2

    def test_get_account_count_after_delete(self, security_manager):
        """TC-SM-020: 削除後のアカウント数取得"""
        account_id = security_manager.add_account(
            "Device1", "user1@example.com", "Service1", "SECRET1"
        )
        assert security_manager.get_account_count() == 1

        security_manager.delete_account(account_id)
        assert security_manager.get_account_count() == 0

    def test_multiple_accounts_management(self, security_manager):
        """TC-SM-021: 複数アカウントの管理"""
        # 複数アカウント追加
        ids = []
        for i in range(5):
            account_id = security_manager.add_account(
                f"Device{i}", f"user{i}@example.com", f"Service{i}", f"SECRET{i}"
            )
            ids.append(account_id)

        assert security_manager.get_account_count() == 5

        # アカウント一覧確認
        accounts = security_manager.list_accounts()
        assert len(accounts) == 5

        # 一部アカウント更新
        security_manager.update_account(ids[0], account_name="updated@example.com")

        # 一部アカウント削除
        security_manager.delete_account(ids[1])

        assert security_manager.get_account_count() == 4

        # 残りのアカウント確認
        remaining_accounts = security_manager.list_accounts()
        assert len(remaining_accounts) == 4

    def test_file_access_permission_error(self, security_manager):
        """TC-SM-022: ファイルアクセス権限エラー"""
        # 読み取り専用ディレクトリでのテスト（権限エラーのシミュレーション）
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(Exception):
                security_manager.add_account(
                    "Device", "user@example.com", "Service", "SECRET"
                )

    def test_empty_data_handling(self, security_manager):
        """TC-SM-023: 空データの処理"""
        # 空のJSONファイルでのテスト
        with patch("json.load", return_value={}):
            security_manager._load_accounts()
            assert security_manager.accounts == []

    def test_data_persistence(self, security_manager):
        """TC-SM-024: データの永続化"""
        account_id = security_manager.add_account(
            device_name="Test Device",
            account_name="test@example.com",
            issuer="TestService",
            secret="JBSWY3DPEHPK3PXP",
        )

        # 新しいインスタンスでデータを読み込み
        new_manager = SecurityManager(
            data_file=security_manager.data_file,
            password="test_password_for_unit_tests",
        )
        account = new_manager.get_account(account_id)

        assert account is not None
        assert account["device_name"] == "Test Device"
        assert account["account_name"] == "test@example.com"

    def test_maximum_accounts_limit(self, security_manager):
        """TC-SM-025: 最大アカウント数制限"""
        # 大量のアカウント追加テスト
        for i in range(100):
            security_manager.add_account(
                f"Device{i}", f"user{i}@example.com", f"Service{i}", f"SECRET{i}"
            )

        assert security_manager.get_account_count() == 100

        # 検索機能の動作確認
        results = security_manager.search_accounts("Device50")
        assert len(results) == 1
        assert results[0]["device_name"] == "Device50"
