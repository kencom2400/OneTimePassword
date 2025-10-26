"""
ワンタイムパスワード生成モジュール
pyotpライブラリを使用してOTPを生成・管理
"""

import pyotp
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import sys


class OTPGenerator:
    """ワンタイムパスワード生成クラス"""

    def __init__(self):
        """初期化"""
        self.running = False
        self.update_thread = None

    def generate_otp(
        self, secret: str, account_name: str = "Unknown"
    ) -> Dict[str, any]:
        """
        ワンタイムパスワードを生成

        Args:
            secret: セキュリティコード
            account_name: アカウント名

        Returns:
            OTP情報を含む辞書
        """
        try:
            # TOTPオブジェクトを作成
            totp = pyotp.TOTP(secret)

            # 現在のOTPを生成
            current_otp = totp.now()

            # 残り時間を計算
            remaining_time = self._calculate_remaining_time()

            return {
                "otp": current_otp,
                "account_name": account_name,
                "remaining_seconds": remaining_time,
                "timestamp": datetime.now(),
                "secret": secret,  # デバッグ用（本番では削除）
            }
        except Exception as e:
            raise Exception(f"OTP生成エラー ({account_name}): {str(e)}")

    def _calculate_remaining_time(self) -> int:
        """
        残り時間を計算（30秒周期）

        Returns:
            残り秒数
        """
        current_time = int(time.time())
        period = 30  # TOTPの周期は30秒
        remaining = period - (current_time % period)
        return remaining

    def generate_multiple_otps(
        self, accounts: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        """
        複数のアカウントのOTPを生成

        Args:
            accounts: アカウント情報のリスト

        Returns:
            OTP情報のリスト
        """
        otps = []
        for account in accounts:
            try:
                if "secret" in account:
                    otp_info = self.generate_otp(
                        account["secret"], account.get("account_name", "Unknown")
                    )
                    otps.append(otp_info)
            except Exception as e:
                print(f"エラー: {account.get('account_name', 'Unknown')} - {str(e)}")
                continue
        return otps

    def start_realtime_display(
        self, accounts: List[Dict[str, any]], update_interval: int = 1
    ):
        """
        リアルタイムでOTPを表示

        Args:
            accounts: アカウント情報のリスト
            update_interval: 更新間隔（秒）
        """
        self.running = True
        self.update_thread = threading.Thread(
            target=self._realtime_update_loop, args=(accounts, update_interval)
        )
        self.update_thread.daemon = True
        self.update_thread.start()

    def stop_realtime_display(self):
        """リアルタイム表示を停止"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()

    def _realtime_update_loop(
        self, accounts: List[Dict[str, any]], update_interval: int
    ):
        """
        リアルタイム更新ループ

        Args:
            accounts: アカウント情報のリスト
            update_interval: 更新間隔（秒）
        """
        while self.running:
            try:
                # 画面をクリア
                self._clear_screen()

                # OTPを生成・表示
                otps = self.generate_multiple_otps(accounts)
                self._display_otps(otps)

                # 更新間隔分待機
                time.sleep(update_interval)

            except KeyboardInterrupt:
                print("\n\n表示を停止します...")
                self.running = False
                break
            except Exception as e:
                print(f"\nエラー: {str(e)}")
                time.sleep(update_interval)

    def _clear_screen(self):
        """画面をクリア"""
        import os

        os.system("cls" if os.name == "nt" else "clear")

    def _display_otps(self, otps: List[Dict[str, any]]):
        """
        OTPを表示

        Args:
            otps: OTP情報のリスト
        """
        print("=" * 60)
        print("ワンタイムパスワード")
        print("=" * 60)
        print(f"更新時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)

        if not otps:
            print("登録されているアカウントがありません。")
            return

        for otp_info in otps:
            account_name = otp_info["account_name"]
            otp = otp_info["otp"]
            remaining = otp_info["remaining_seconds"]

            # プログレスバーを作成
            progress_bar = self._create_progress_bar(remaining, 30)

            print(f"アカウント: {account_name}")
            print(f"OTP: {otp}")
            print(f"残り時間: {remaining}秒 {progress_bar}")
            print("-" * 60)

        print("\nCtrl+C で停止")

    def _create_progress_bar(self, remaining: int, total: int) -> str:
        """
        プログレスバーを作成

        Args:
            remaining: 残り時間
            total: 総時間

        Returns:
            プログレスバーの文字列
        """
        filled = total - remaining
        bar_length = 20
        filled_length = int(bar_length * filled / total)

        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        return f"[{bar}]"

    def validate_secret(self, secret: str) -> bool:
        """
        セキュリティコードの形式を検証

        Args:
            secret: セキュリティコード

        Returns:
            有効な場合True
        """
        try:
            # Base32形式かどうかをチェック
            pyotp.TOTP(secret)
            return True
        except Exception:
            return False

    def get_secret_info(self, secret: str) -> Dict[str, any]:
        """
        セキュリティコードの情報を取得

        Args:
            secret: セキュリティコード

        Returns:
            セキュリティコードの情報
        """
        try:
            totp = pyotp.TOTP(secret)
            return {
                "valid": True,
                "algorithm": "SHA1",
                "digits": 6,
                "period": 30,
                "issuer": "Unknown",
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}


def test_otp_generator():
    """OTP生成器のテスト"""
    generator = OTPGenerator()

    # テスト用のセキュリティコード（実際のコードに置き換えてください）
    test_secret = "JBSWY3DPEHPK3PXP"

    print("OTP生成テスト")
    print("-" * 40)

    # 単一OTP生成テスト
    otp_info = generator.generate_otp(test_secret, "テストアカウント")
    print(f"アカウント: {otp_info['account_name']}")
    print(f"OTP: {otp_info['otp']}")
    print(f"残り時間: {otp_info['remaining_seconds']}秒")

    # セキュリティコード検証テスト
    print(f"\nセキュリティコード検証: {generator.validate_secret(test_secret)}")

    # セキュリティコード情報取得テスト
    secret_info = generator.get_secret_info(test_secret)
    print(f"セキュリティコード情報: {secret_info}")


if __name__ == "__main__":
    test_otp_generator()
