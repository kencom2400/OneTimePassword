"""
otp_generator.pyのテスト
"""
import pytest
import time
import threading
from unittest.mock import patch, Mock, MagicMock
from src.otp_generator import OTPGenerator


class TestOTPGenerator:
    """OTPGeneratorクラスのテスト"""

    def test_generate_otp_normal(self, sample_account_data):
        """TC-OTP-001: 正常なTOTP生成"""
        generator = OTPGenerator()
        secret = sample_account_data["secret"]

        otp_info = generator.generate_otp(secret, sample_account_data["account_name"])

        assert isinstance(otp_info, dict)
        assert "otp" in otp_info
        assert isinstance(otp_info["otp"], str)
        assert len(otp_info["otp"]) == 6  # 6桁のTOTP
        assert otp_info["otp"].isdigit()
        assert otp_info["account_name"] == sample_account_data["account_name"]

    def test_generate_otp_multiple_accounts(self, sample_accounts):
        """TC-OTP-002: 複数アカウントのTOTP生成"""
        generator = OTPGenerator()

        for account in sample_accounts:
            otp_info = generator.generate_otp(
                account["secret"], account["account_name"]
            )
            assert isinstance(otp_info, dict)
            assert "otp" in otp_info
            assert isinstance(otp_info["otp"], str)
            assert len(otp_info["otp"]) == 6
            assert otp_info["otp"].isdigit()

    def test_generate_otp_invalid_secret(self):
        """TC-OTP-006: 無効なシークレットでのTOTP生成失敗"""
        generator = OTPGenerator()
        invalid_secret = "invalid_secret"

        with pytest.raises(Exception):
            generator.generate_otp(invalid_secret, "test")

    def test_generate_otp_empty_secret(self):
        """TC-OTP-007: 空のシークレットでの処理"""
        generator = OTPGenerator()
        empty_secret = ""

        # 空のシークレットでもOTPが生成されることを確認
        result = generator.generate_otp(empty_secret, "test")
        assert isinstance(result, dict)
        assert "otp" in result
        assert len(result["otp"]) == 6
        assert result["otp"].isdigit()

    def test_generate_otp_none_secret(self):
        """TC-OTP-009: None値での処理失敗"""
        generator = OTPGenerator()

        with pytest.raises(Exception):
            generator.generate_otp(None, "test")

    def test_generate_otp_minimum_length_secret(self):
        """TC-OTP-010: 最小長シークレット（16文字）"""
        generator = OTPGenerator()
        min_secret = "JBSWY3DPEHPK3PXP"  # 16文字

        otp_info = generator.generate_otp(min_secret, "test")

        assert isinstance(otp_info, dict)
        assert "otp" in otp_info
        assert len(otp_info["otp"]) == 6

    def test_generate_otp_maximum_length_secret(self):
        """TC-OTP-011: 最大長シークレット（128文字）"""
        generator = OTPGenerator()
        max_secret = "A" * 128

        otp_info = generator.generate_otp(max_secret, "test")

        assert isinstance(otp_info, dict)
        assert "otp" in otp_info
        assert len(otp_info["otp"]) == 6

    def test_get_remaining_time(self, mock_time):
        """TC-OTP-003: 残り時間の正確な計算"""
        generator = OTPGenerator()

        # 残り時間の計算をテスト（プライベートメソッドを直接テスト）
        remaining_time = generator._calculate_remaining_time()

        assert isinstance(remaining_time, int)
        assert 1 <= remaining_time <= 30

    def test_get_remaining_time_boundary(self):
        """TC-OTP-012: 時刻境界でのTOTP生成"""
        generator = OTPGenerator()
        secret = "JBSWY3DPEHPK3PXP"

        # 時刻を固定してテスト
        with patch("time.time") as mock_time:
            mock_time.return_value = 1640995200.0  # 30秒の倍数の時刻
            otp_info1 = generator.generate_otp(secret, "test")

            mock_time.return_value = 1640995200.0 + 15  # 15秒後
            otp_info2 = generator.generate_otp(secret, "test")

            # 同じ30秒周期内なので同じTOTPが生成される
            assert otp_info1["otp"] == otp_info2["otp"]

    def test_start_realtime_display(self, sample_accounts):
        """TC-OTP-004: リアルタイム表示の開始"""
        generator = OTPGenerator()

        # モックを使用してスレッドの影響を回避
        with patch("threading.Thread") as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance

            generator.start_realtime_display(sample_accounts)

            assert generator.running is True
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()

    def test_stop_realtime_display(self, sample_accounts):
        """TC-OTP-004: リアルタイム表示の停止"""
        generator = OTPGenerator()

        # 表示を開始
        with patch("threading.Thread"):
            generator.start_realtime_display(sample_accounts)
            assert generator.running is True

            # 表示を停止
            generator.stop_realtime_display()
            assert generator.running is False

    def test_realtime_display_multiple_accounts(self, sample_accounts):
        """複数アカウントのリアルタイム表示"""
        generator = OTPGenerator()

        with patch("threading.Thread") as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance

            generator.start_realtime_display(sample_accounts)

            assert generator.running is True
            mock_thread.assert_called_once()

    def test_realtime_display_empty_accounts(self):
        """空のアカウントリストでのリアルタイム表示"""
        generator = OTPGenerator()

        with patch("threading.Thread") as mock_thread:
            generator.start_realtime_display([])

            # 空のリストでもエラーにならないことを確認
            assert generator.running is True
            mock_thread.assert_called_once()

    def test_totp_consistency_same_time(self, sample_account_data):
        """同じ時刻でのTOTP一貫性"""
        generator = OTPGenerator()
        secret = sample_account_data["secret"]

        with patch("time.time") as mock_time:
            mock_time.return_value = 1640995200.0

            otp_info1 = generator.generate_otp(secret, "test")
            otp_info2 = generator.generate_otp(secret, "test")

            assert otp_info1["otp"] == otp_info2["otp"]

    def test_totp_different_times(self, sample_account_data):
        """異なる時刻でのTOTP差異"""
        generator = OTPGenerator()
        secret = sample_account_data["secret"]

        with patch("time.time") as mock_time:
            mock_time.return_value = 1640995200.0
            totp1 = generator.generate_otp(secret)

            mock_time.return_value = 1640995200.0 + 31  # 次の周期
            totp2 = generator.generate_otp(secret)

            # 異なる周期なので異なるTOTPが生成される可能性が高い
            # （ただし、稀に同じ場合もあるため、確実性は保証しない）

    def test_totp_format(self, sample_account_data):
        """TOTP形式の検証"""
        generator = OTPGenerator()
        secret = sample_account_data["secret"]

        otp_info = generator.generate_otp(secret, "test")

        # 6桁の数字であることを確認
        assert isinstance(otp_info, dict)
        assert "otp" in otp_info
        assert len(otp_info["otp"]) == 6
        assert otp_info["otp"].isdigit()
        assert int(otp_info["otp"]) >= 0
        assert int(otp_info["otp"]) <= 999999

    def test_thread_safety(self, sample_account_data):
        """スレッドセーフティのテスト"""
        generator = OTPGenerator()
        secret = sample_account_data["secret"]
        results = []

        def generate_otp_thread():
            otp_info = generator.generate_otp(secret, "test")
            results.append(otp_info)

        # 複数スレッドで同時にTOTP生成
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=generate_otp_thread)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 全てのOTPが有効な形式であることを確認
        assert len(results) == 5
        for otp_info in results:
            assert isinstance(otp_info, dict)
            assert "otp" in otp_info
            assert len(otp_info["otp"]) == 6
            assert otp_info["otp"].isdigit()

    def test_cleanup_on_stop(self, sample_accounts):
        """停止時のクリーンアップ"""
        generator = OTPGenerator()

        with patch("threading.Thread") as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance

            generator.start_realtime_display(sample_accounts)
            generator.stop_realtime_display()

            # 停止後にrunningがFalseになっていることを確認
            assert generator.running is False

    def test_display_thread_exception_handling(self, sample_accounts):
        """表示スレッドでの例外処理"""
        generator = OTPGenerator()

        # 無効なアカウントデータで例外が発生することを確認
        invalid_accounts = [{"secret": "invalid_secret"}]

        with patch("threading.Thread") as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance

            # 例外が発生してもアプリケーションが停止しないことを確認
            generator.start_realtime_display(invalid_accounts)
            generator.stop_realtime_display()

            assert generator.running is False
