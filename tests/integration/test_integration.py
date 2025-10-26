"""
統合テスト
"""

import pytest
import os
import tempfile
from unittest.mock import patch, Mock, MagicMock
from src.security_manager import SecurityManager
from src.otp_generator import OTPGenerator
from src.camera_qr_reader import CameraQRReader
from src.docker_manager import DockerManager
from src.main import OneTimePasswordApp


class TestCryptoIntegration:
    """暗号化機能の統合テスト"""

    @pytest.fixture
    def temp_data_dir(self):
        """一時データディレクトリ"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_encryption_decryption_integration(self, temp_data_dir):
        """TC-INT-001: 暗号化・復号化の統合テスト"""
        data_file = os.path.join(temp_data_dir, "test_accounts.json")
        security_manager = SecurityManager(
            data_file=data_file, password="test_password_integration"
        )

        # アカウント追加
        account_id = security_manager.add_account(
            device_name="Test Device",
            account_name="test@example.com",
            issuer="TestService",
            secret="JBSWY3DPEHPK3PXP",
        )

        assert account_id is not None

        # アカウント取得（復号化）
        account = security_manager.get_account(account_id)
        assert account is not None
        assert account["secret"] == "JBSWY3DPEHPK3PXP"
        assert account["account_name"] == "test@example.com"

    def test_security_manager_encryption_integration(self, temp_data_dir):
        """TC-INT-002: SecurityManager暗号化統合テスト"""
        data_file = os.path.join(temp_data_dir, "test_accounts.json")
        security_manager = SecurityManager(
            data_file=data_file, password="test_password_integration"
        )

        # 複数アカウント追加
        account_ids = []
        for i in range(3):
            account_id = security_manager.add_account(
                device_name=f"Device{i}",
                account_name=f"user{i}@example.com",
                issuer=f"Service{i}",
                secret=f"SECRET{i}",
            )
            account_ids.append(account_id)

        # 全アカウント取得
        all_accounts = security_manager.get_all_accounts()
        assert len(all_accounts) == 3

        # 各アカウントの復号化確認
        for i, account in enumerate(all_accounts):
            assert account["secret"] == f"SECRET{i}"
            assert account["account_name"] == f"user{i}@example.com"


class TestDockerIntegration:
    """Docker機能の統合テスト"""

    def test_docker_environment_setup_integration(self):
        """TC-INT-003: Docker環境セットアップ統合テスト"""
        docker_manager = DockerManager()

        with patch.object(docker_manager, "check_docker_available", return_value=True):
            with patch.object(docker_manager, "clone_repository", return_value=True):
                with patch.object(docker_manager, "build_image", return_value=True):
                    result = docker_manager.setup_environment()

                    assert result is True

    def test_docker_qr_processing_integration(self):
        """TC-INT-004: Docker QRコード処理統合テスト"""
        docker_manager = DockerManager()

        with patch.object(docker_manager, "_validate_qr_url", return_value=True):
            with patch.object(
                docker_manager, "ensure_image_available", return_value=True
            ):
                with patch.object(
                    docker_manager,
                    "run_container",
                    return_value=(
                        True,
                        "otpauth://totp/test@example.com?algorithm=SHA1&digits=6&issuer=TestService&period=30&secret=JBSWY3DPEHPK3PXP",
                    ),
                ):
                    result = docker_manager.process_qr_url(
                        "otpauth-migration://offline?data=test"
                    )

                    assert result is not None
                    assert result["device_name"] == "test"
                    assert result["account_name"] == "example.com"
                    assert result["secret"] == "JBSWY3DPEHPK3PXP"


class TestAccountFlowIntegration:
    """アカウントフローの統合テスト"""

    @pytest.fixture
    def temp_data_dir(self):
        """一時データディレクトリ"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def app(self, temp_data_dir):
        """テスト用アプリケーションインスタンス"""
        data_file = os.path.join(temp_data_dir, "test_accounts.json")
        with patch("src.main.SecurityManager") as mock_sm_class, patch(
            "src.main.OTPGenerator"
        ) as mock_otp_class, patch("src.main.CameraQRReader") as mock_cam_class, patch(
            "src.main.DockerManager"
        ) as mock_docker_class:
            # 実際のSecurityManagerインスタンスを作成
            real_sm = SecurityManager(
                data_file=data_file, password="test_password_integration"
            )
            mock_sm_class.return_value = real_sm

            app = OneTimePasswordApp()
            app.security_manager = real_sm
            return app

    def test_account_add_flow_integration(self, app):
        """TC-INT-005: アカウント追加フロー統合テスト"""
        # モックデータ
        mock_qr_data = "otpauth-migration://offline?data=test_data"
        mock_parsed_data = {
            "device_name": "TestDevice",
            "account_name": "test@example.com",
            "issuer": "TestService",
            "secret": "JBSWY3DPEHPK3PXP",
        }

        # start_qr_detectionをモックして、即座にQRコードを検出させる
        def mock_start_qr_detection(on_qr_detected, on_error):
            on_qr_detected(mock_qr_data)

        app.camera_reader.start_qr_detection = mock_start_qr_detection
        app.docker_manager.process_qr_url.return_value = mock_parsed_data

        # アカウント追加
        result = app.add_account_from_camera()

        assert result is True

        # 追加されたアカウントを確認
        accounts = app.security_manager.list_accounts()
        assert len(accounts) == 1
        assert accounts[0]["account_name"] == "test@example.com"
        assert accounts[0]["issuer"] == "TestService"

    def test_otp_display_flow_integration(self, app):
        """TC-INT-006: OTP表示フロー統合テスト"""
        # テストアカウントを追加
        account_id = app.security_manager.add_account(
            device_name="Test Device",
            account_name="test@example.com",
            issuer="TestService",
            secret="JBSWY3DPEHPK3PXP",
        )

        # OTP表示
        app.show_otp()

        # アカウントが存在することを確認
        accounts = app.security_manager.get_all_accounts()
        assert len(accounts) == 1
        assert accounts[0]["account_name"] == "test@example.com"

    def test_account_management_flow_integration(self, app):
        """TC-INT-007: アカウント管理フロー統合テスト"""
        # アカウント追加
        account_id = app.security_manager.add_account(
            device_name="Test Device",
            account_name="test@example.com",
            issuer="TestService",
            secret="JBSWY3DPEHPK3PXP",
        )

        # アカウント一覧表示
        app.list_accounts()

        # アカウント更新
        success = app.update_account(account_id, account_name="updated@example.com")
        assert success is True

        # 更新確認
        account = app.security_manager.get_account(account_id)
        assert account["account_name"] == "updated@example.com"

        # アカウント削除
        with patch("builtins.input", return_value="y"):
            success = app.delete_account(account_id)
        assert success is True

        # 削除確認
        account = app.security_manager.get_account(account_id)
        assert account is None


class TestEndToEndIntegration:
    """エンドツーエンド統合テスト"""

    @pytest.fixture
    def temp_data_dir(self):
        """一時データディレクトリ"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def app(self, temp_data_dir):
        """テスト用アプリケーションインスタンス"""
        data_file = os.path.join(temp_data_dir, "test_accounts.json")
        with patch("src.main.SecurityManager") as mock_sm_class, patch(
            "src.main.OTPGenerator"
        ) as mock_otp_class, patch("src.main.CameraQRReader") as mock_cam_class, patch(
            "src.main.DockerManager"
        ) as mock_docker_class:
            # 実際のSecurityManagerインスタンスを作成
            real_sm = SecurityManager(
                data_file=data_file, password="test_password_integration"
            )
            mock_sm_class.return_value = real_sm

            app = OneTimePasswordApp()
            app.security_manager = real_sm
            return app

    def test_complete_user_scenario(self, app):
        """TC-INT-008: 完全なユーザーシナリオ"""
        # 1. Docker環境セットアップ
        app.docker_manager.setup_environment.return_value = True
        setup_result = app.setup_environment()
        assert setup_result is True

        # 2. カメラからアカウント追加
        mock_qr_data = "otpauth-migration://offline?data=test_data"
        mock_parsed_data = {
            "device_name": "TestDevice",
            "account_name": "test@example.com",
            "issuer": "TestService",
            "secret": "JBSWY3DPEHPK3PXP",
        }

        # start_qr_detectionをモックして、即座にQRコードを検出させる
        def mock_start_qr_detection(on_qr_detected, on_error):
            on_qr_detected(mock_qr_data)

        app.camera_reader.start_qr_detection = mock_start_qr_detection
        app.docker_manager.process_qr_url.return_value = mock_parsed_data

        add_result = app.add_account_from_camera()
        assert add_result is True

        # 3. アカウント一覧確認
        accounts = app.security_manager.list_accounts()
        assert len(accounts) == 1

        # 4. OTP表示
        app.running = False  # ループを終了させる
        app.show_otp(show_all=True)

        # 5. ステータス確認
        app.show_status()

        # 6. アカウント削除
        account_id = accounts[0]["id"]
        with patch("builtins.input", return_value="y"):
            delete_result = app.delete_account(account_id)
        assert delete_result is True

        # 7. 削除確認
        remaining_accounts = app.security_manager.list_accounts()
        assert len(remaining_accounts) == 0

    def test_error_handling_integration(self, app):
        """TC-INT-009: エラーハンドリング統合テスト"""

        # 無効なQRコードでのアカウント追加
        # start_qr_detectionをモックして、無効なQRコードを検出させる
        def mock_start_qr_detection(on_qr_detected, on_error):
            on_qr_detected("invalid_qr_data")

        app.camera_reader.start_qr_detection = mock_start_qr_detection
        app.docker_manager.process_qr_url.return_value = None

        result = app.add_account_from_camera()
        assert result is False

        # アカウントが追加されていないことを確認
        accounts = app.security_manager.list_accounts()
        assert len(accounts) == 0

    def test_concurrent_operations_integration(self, app):
        """TC-INT-010: 並行操作統合テスト"""
        # 複数アカウントの同時追加
        account_ids = []
        for i in range(5):
            account_id = app.security_manager.add_account(
                device_name=f"Device{i}",
                account_name=f"user{i}@example.com",
                issuer=f"Service{i}",
                secret=f"SECRET{i}",
            )
            account_ids.append(account_id)

        # 全アカウント取得
        all_accounts = app.security_manager.get_all_accounts()
        assert len(all_accounts) == 5

        # 並行検索
        search_results = app.security_manager.search_accounts("user")
        assert len(search_results) == 5

        # 並行更新
        for i, account_id in enumerate(account_ids):
            success = app.security_manager.update_account(
                account_id, account_name=f"updated_user{i}@example.com"
            )
            assert success is True

        # 更新確認
        updated_accounts = app.security_manager.get_all_accounts()
        for i, account in enumerate(updated_accounts):
            assert account["account_name"] == f"updated_user{i}@example.com"
