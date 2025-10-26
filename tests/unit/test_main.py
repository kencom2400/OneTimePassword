"""
Mainモジュールのテスト
"""

import pytest
import sys
from unittest.mock import patch, Mock, MagicMock
from src.main import OneTimePasswordApp, main


class TestOneTimePasswordApp:
    """OneTimePasswordAppクラスのテスト"""

    @pytest.fixture
    def app(self):
        """テスト用アプリケーションインスタンス"""
        with patch("src.main.SecurityManager"), patch("src.main.OTPGenerator"), patch(
            "src.main.CameraQRReader"
        ), patch("src.main.DockerManager"):
            return OneTimePasswordApp()

    def test_add_account_from_camera_success(self, app):
        """TC-MAIN-001: カメラからのアカウント追加（成功）"""
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
        app.security_manager.add_account.return_value = "test-account-id"

        result = app.add_account_from_camera()

        assert result is True
        app.docker_manager.process_qr_url.assert_called_once_with(mock_qr_data)
        app.security_manager.add_account.assert_called_once_with(
            device_name="TestDevice",
            account_name="test@example.com",
            issuer="TestService",
            secret="JBSWY3DPEHPK3PXP",
        )

    def test_add_account_from_camera_qr_failure(self, app):
        """TC-MAIN-002: QRコード読み取り失敗"""

        # start_qr_detectionをモックして、QRコードを検出しない
        def mock_start_qr_detection(on_qr_detected, on_error):
            pass  # QRコードを検出しない

        app.camera_reader.start_qr_detection = mock_start_qr_detection
        app.running = False  # ループを終了させる

        result = app.add_account_from_camera()

        assert result is False

    def test_add_account_from_camera_parsing_failure(self, app):
        """TC-MAIN-003: QRコード解析失敗"""
        mock_qr_data = "otpauth-migration://offline?data=test_data"

        # start_qr_detectionをモックして、QRコードを検出させる
        def mock_start_qr_detection(on_qr_detected, on_error):
            on_qr_detected(mock_qr_data)

        app.camera_reader.start_qr_detection = mock_start_qr_detection
        app.docker_manager.process_qr_url.return_value = None

        result = app.add_account_from_camera()

        assert result is False

    def test_add_account_from_camera_add_failure(self, app):
        """TC-MAIN-004: アカウント追加失敗"""
        mock_qr_data = "otpauth-migration://offline?data=test_data"
        mock_parsed_data = {
            "device_name": "TestDevice",
            "account_name": "test@example.com",
            "issuer": "TestService",
            "secret": "JBSWY3DPEHPK3PXP",
        }

        # start_qr_detectionをモックして、QRコードを検出させる
        def mock_start_qr_detection(on_qr_detected, on_error):
            on_qr_detected(mock_qr_data)

        app.camera_reader.start_qr_detection = mock_start_qr_detection
        app.docker_manager.process_qr_url.return_value = mock_parsed_data
        app.security_manager.add_account.side_effect = Exception("Add failed")

        result = app.add_account_from_camera()

        assert result is False

    def test_add_account_from_image_success(self, app):
        """TC-MAIN-005: 画像ファイルからのアカウント追加（成功）"""
        image_path = "test_qr.png"
        mock_qr_data = "otpauth-migration://offline?data=test_data"
        mock_parsed_data = {
            "device_name": "TestDevice",
            "account_name": "test@example.com",
            "issuer": "TestService",
            "secret": "JBSWY3DPEHPK3PXP",
        }

        app.camera_reader.read_qr_from_image.return_value = mock_qr_data
        app.docker_manager.process_qr_url.return_value = mock_parsed_data
        app.security_manager.add_account.return_value = "test-account-id"

        result = app.add_account_from_image(image_path)

        assert result is True
        app.camera_reader.read_qr_from_image.assert_called_once_with(image_path)
        app.docker_manager.process_qr_url.assert_called_once_with(mock_qr_data)

    def test_add_account_from_image_file_not_found(self, app):
        """TC-MAIN-006: 画像ファイルが見つからない"""
        image_path = "nonexistent.png"

        app.camera_reader.read_qr_from_image.return_value = None

        result = app.add_account_from_image(image_path)

        assert result is False

    def test_show_otp_success(self, app):
        """TC-MAIN-007: OTP表示（成功）"""
        mock_accounts = [
            {
                "id": "account1",
                "account_name": "test1@example.com",
                "secret": "SECRET1",
            },
            {
                "id": "account2",
                "account_name": "test2@example.com",
                "secret": "SECRET2",
            },
        ]
        mock_otps = [
            {
                "otp": "123456",
                "account_name": "test1@example.com",
                "remaining_seconds": 15,
            },
            {
                "otp": "789012",
                "account_name": "test2@example.com",
                "remaining_seconds": 20,
            },
        ]

        app.security_manager.get_all_accounts.return_value = mock_accounts
        app.otp_generator.start_realtime_display.return_value = None
        app.running = False  # ループを終了させる

        app.show_otp(show_all=True)

        app.security_manager.get_all_accounts.assert_called_once()
        app.otp_generator.start_realtime_display.assert_called_once_with(mock_accounts)

    def test_show_otp_no_accounts(self, app):
        """TC-MAIN-008: OTP表示（アカウントなし）"""
        app.security_manager.get_all_accounts.return_value = []
        app.running = False  # ループを終了させる

        app.show_otp(show_all=True)

        app.security_manager.get_all_accounts.assert_called_once()
        app.otp_generator.start_realtime_display.assert_not_called()

    def test_show_otp_generation_error(self, app):
        """TC-MAIN-009: OTP生成エラー"""
        mock_accounts = [
            {"id": "account1", "account_name": "test@example.com", "secret": "SECRET1"}
        ]

        app.security_manager.get_all_accounts.return_value = mock_accounts
        app.otp_generator.start_realtime_display.side_effect = Exception(
            "Generation failed"
        )
        app.running = False  # ループを終了させる

        # 例外が発生することを期待
        with pytest.raises(Exception, match="Generation failed"):
            app.show_otp(show_all=True)

        app.security_manager.get_all_accounts.assert_called_once()
        app.otp_generator.start_realtime_display.assert_called_once()

    def test_list_accounts_success(self, app):
        """TC-MAIN-010: アカウント一覧表示（成功）"""
        mock_accounts = [
            {
                "id": "account1",
                "account_name": "test1@example.com",
                "issuer": "Service1",
                "created_at": "2025-01-26T10:00:00Z",
            },
            {
                "id": "account2",
                "account_name": "test2@example.com",
                "issuer": "Service2",
                "created_at": "2025-01-26T11:00:00Z",
            },
        ]

        app.security_manager.list_accounts.return_value = mock_accounts

        app.list_accounts()

        app.security_manager.list_accounts.assert_called_once()

    def test_list_accounts_empty(self, app):
        """TC-MAIN-011: アカウント一覧表示（空）"""
        app.security_manager.list_accounts.return_value = []

        app.list_accounts()

        app.security_manager.list_accounts.assert_called_once()

    def test_delete_account_success(self, app):
        """TC-MAIN-012: アカウント削除（成功）"""
        account_id = "test-account-id"

        app.security_manager.delete_account.return_value = True

        with patch("builtins.input", return_value="y"):
            result = app.delete_account(account_id)

        assert result is True
        app.security_manager.delete_account.assert_called_once_with(account_id)

    def test_delete_account_not_found(self, app):
        """TC-MAIN-013: アカウント削除（見つからない）"""
        account_id = "non-existent-id"

        app.security_manager.delete_account.return_value = False

        with patch("builtins.input", return_value="y"):
            result = app.delete_account(account_id)

        assert result is False
        app.security_manager.delete_account.assert_called_once_with(account_id)

    def test_update_account_success(self, app):
        """TC-MAIN-014: アカウント更新（成功）"""
        account_id = "test-account-id"
        updates = {"account_name": "updated@example.com"}

        app.security_manager.update_account.return_value = True

        result = app.update_account(account_id, **updates)

        assert result is True
        app.security_manager.update_account.assert_called_once_with(
            account_id, **updates
        )

    def test_update_account_not_found(self, app):
        """TC-MAIN-015: アカウント更新（見つからない）"""
        account_id = "non-existent-id"
        updates = {"account_name": "updated@example.com"}

        app.security_manager.update_account.return_value = False

        result = app.update_account(account_id, **updates)

        assert result is False
        app.security_manager.update_account.assert_called_once_with(
            account_id, **updates
        )

    def test_search_accounts_success(self, app):
        """TC-MAIN-016: アカウント検索（成功）"""
        keyword = "test"
        mock_results = [
            {
                "id": "account1",
                "account_name": "test@example.com",
                "issuer": "TestService",
                "created_at": "2025-01-26T10:00:00Z",
            }
        ]

        app.security_manager.search_accounts.return_value = mock_results

        app.search_accounts(keyword)

        app.security_manager.search_accounts.assert_called_once_with(keyword)

    def test_search_accounts_not_found(self, app):
        """TC-MAIN-017: アカウント検索（見つからない）"""
        keyword = "nonexistent"

        app.security_manager.search_accounts.return_value = []

        app.search_accounts(keyword)

        app.security_manager.search_accounts.assert_called_once_with(keyword)

    def test_setup_docker_environment_success(self, app):
        """TC-MAIN-018: Docker環境セットアップ（成功）"""
        app.docker_manager.setup_environment.return_value = True

        result = app.setup_environment()

        assert result is True
        app.docker_manager.setup_environment.assert_called_once()

    def test_setup_docker_environment_failure(self, app):
        """TC-MAIN-019: Docker環境セットアップ（失敗）"""
        app.docker_manager.setup_environment.return_value = False

        result = app.setup_environment()

        assert result is False
        app.docker_manager.setup_environment.assert_called_once()

    def test_delete_docker_image_success(self, app):
        """TC-MAIN-020: Dockerイメージ削除（成功）"""
        app.docker_manager.delete_image.return_value = True

        result = app.delete_docker_image()

        assert result is True
        app.docker_manager.delete_image.assert_called_once()

    def test_delete_docker_image_failure(self, app):
        """TC-MAIN-021: Dockerイメージ削除（失敗）"""
        app.docker_manager.delete_image.return_value = False

        result = app.delete_docker_image()

        assert result is False
        app.docker_manager.delete_image.assert_called_once()

    def test_show_status_success(self, app):
        """TC-MAIN-022: ステータス表示（成功）"""
        mock_accounts = [
            {"id": "account1", "account_name": "test1@example.com"},
            {"id": "account2", "account_name": "test2@example.com"},
        ]

        app.security_manager.get_account_count.return_value = 2
        app.camera_reader.check_camera_available.return_value = True
        app.docker_manager.check_docker_available.return_value = True

        app.show_status()

        app.security_manager.get_account_count.assert_called_once()
        app.camera_reader.check_camera_available.assert_called_once()
        app.docker_manager.check_docker_available.assert_called_once()

    def test_show_status_docker_unavailable(self, app):
        """TC-MAIN-023: ステータス表示（Docker利用不可）"""
        app.security_manager.get_account_count.return_value = 1
        app.camera_reader.check_camera_available.return_value = False
        app.docker_manager.check_docker_available.return_value = False

        app.show_status()

        app.security_manager.get_account_count.assert_called_once()
        app.camera_reader.check_camera_available.assert_called_once()
        app.docker_manager.check_docker_available.assert_called_once()
        app.docker_manager.check_image_exists.assert_not_called()


class TestMainFunction:
    """main関数のテスト"""

    def test_main_add_command(self):
        """TC-MAIN-024: addコマンドの実行"""
        with patch("sys.argv", ["main.py", "add", "--camera"]):
            with patch("src.main.OneTimePasswordApp") as mock_app_class:
                mock_app = Mock()
                mock_app_class.return_value = mock_app
                mock_app.add_account_from_camera.return_value = True

                main()

                mock_app_class.assert_called_once()
                mock_app.add_account_from_camera.assert_called_once()

    def test_main_show_command(self):
        """TC-MAIN-025: showコマンドの実行"""
        with patch("sys.argv", ["main.py", "show", "--all"]):
            with patch("src.main.OneTimePasswordApp") as mock_app_class:
                mock_app = Mock()
                mock_app_class.return_value = mock_app
                mock_app.running = False  # ループを終了させる

                main()

                mock_app_class.assert_called_once()
                mock_app.show_otp.assert_called_once_with(None, True)

    def test_main_list_command(self):
        """TC-MAIN-026: listコマンドの実行"""
        with patch("sys.argv", ["main.py", "list"]):
            with patch("src.main.OneTimePasswordApp") as mock_app_class:
                mock_app = Mock()
                mock_app_class.return_value = mock_app

                main()

                mock_app_class.assert_called_once()
                mock_app.list_accounts.assert_called_once()

    def test_main_delete_command(self):
        """TC-MAIN-027: deleteコマンドの実行"""
        with patch("sys.argv", ["main.py", "delete", "account-id"]):
            with patch("src.main.OneTimePasswordApp") as mock_app_class:
                mock_app = Mock()
                mock_app_class.return_value = mock_app
                mock_app.delete_account.return_value = True

                main()

                mock_app_class.assert_called_once()
                mock_app.delete_account.assert_called_once_with("account-id")

    def test_main_update_command(self):
        """TC-MAIN-028: updateコマンドの実行"""
        with patch(
            "sys.argv", ["main.py", "update", "account-id", "--name", "new-name"]
        ):
            with patch("src.main.OneTimePasswordApp") as mock_app_class:
                mock_app = Mock()
                mock_app_class.return_value = mock_app
                mock_app.update_account.return_value = True

                main()

                mock_app_class.assert_called_once()
                mock_app.update_account.assert_called_once_with(
                    "account-id", account_name="new-name"
                )

    def test_main_search_command(self):
        """TC-MAIN-029: searchコマンドの実行"""
        with patch("sys.argv", ["main.py", "search", "keyword"]):
            with patch("src.main.OneTimePasswordApp") as mock_app_class:
                mock_app = Mock()
                mock_app_class.return_value = mock_app

                main()

                mock_app_class.assert_called_once()
                mock_app.search_accounts.assert_called_once_with("keyword")

    def test_main_setup_command(self):
        """TC-MAIN-030: setupコマンドの実行"""
        with patch("sys.argv", ["main.py", "setup"]):
            with patch("src.main.OneTimePasswordApp") as mock_app_class:
                mock_app = Mock()
                mock_app_class.return_value = mock_app
                mock_app.setup_environment.return_value = True

                main()

                mock_app_class.assert_called_once()
                mock_app.setup_environment.assert_called_once()

    def test_main_cleanup_command(self):
        """TC-MAIN-031: cleanupコマンドの実行"""
        with patch("sys.argv", ["main.py", "cleanup"]):
            with patch("src.main.OneTimePasswordApp") as mock_app_class:
                mock_app = Mock()
                mock_app_class.return_value = mock_app
                mock_app.delete_docker_image.return_value = True

                main()

                mock_app_class.assert_called_once()
                mock_app.delete_docker_image.assert_called_once()

    def test_main_status_command(self):
        """TC-MAIN-032: statusコマンドの実行"""
        with patch("sys.argv", ["main.py", "status"]):
            with patch("src.main.OneTimePasswordApp") as mock_app_class:
                mock_app = Mock()
                mock_app_class.return_value = mock_app

                main()

                mock_app_class.assert_called_once()
                mock_app.show_status.assert_called_once()

    def test_main_invalid_command(self):
        """TC-MAIN-033: 無効なコマンドでの実行"""
        with patch("sys.argv", ["main.py", "invalid"]):
            with pytest.raises(SystemExit):
                main()

    def test_main_no_command(self):
        """TC-MAIN-034: コマンドなしでの実行"""
        with patch("sys.argv", ["main.py"]):
            # コマンドなしで実行するとヘルプが表示されるが、SystemExitは発生しない
            # （argparse が自動的にヘルプを表示）
            main()

    def test_main_help_command(self):
        """TC-MAIN-035: ヘルプコマンドの実行"""
        with patch("sys.argv", ["main.py", "--help"]):
            with pytest.raises(SystemExit):
                main()
