"""
ワンタイムパスワード生成アプリケーション
メインアプリケーション - コマンドラインインターフェース
"""

import argparse
import sys
import os
import time
import signal
import threading
from typing import List, Dict, Any

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.security_manager import SecurityManager
from src.otp_generator import OTPGenerator
from src.camera_qr_reader import CameraQRReader
from src.docker_manager import DockerManager
from src.crypto_utils import CryptoUtils


class OneTimePasswordApp:
    """ワンタイムパスワードアプリケーションのメインクラス"""

    def __init__(self):
        """初期化"""
        self.security_manager = SecurityManager()
        self.otp_generator = OTPGenerator()
        self.camera_reader = CameraQRReader()
        self.docker_manager = DockerManager()
        self.running = True
        self.qr_detected_event = threading.Event()

        # シグナルハンドラーを設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """シグナルハンドラー"""
        print("\n\nアプリケーションを終了します...")
        self.running = False
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """リソースをクリーンアップ"""
        try:
            self.camera_reader.stop_camera()
            self.otp_generator.stop_realtime_display()
            self.docker_manager.cleanup()
        except Exception as e:
            print(f"クリーンアップエラー: {str(e)}")

    def add_account_from_camera(self):
        """カメラからQRコードを読み取ってアカウントを追加"""
        print("カメラでQRコードを読み取ります...")
        print("QRコードをカメラに向けてください。")
        print("Ctrl+C でキャンセル")

        qr_data = None
        self.qr_detected_event.clear()

        def on_qr_detected(data):
            nonlocal qr_data
            qr_data = data
            print(f"\nQRコードを検出しました: {data}")
            self.qr_detected_event.set()

        def on_error(error):
            print(f"エラー: {error}")

        try:
            self.camera_reader.start_qr_detection(on_qr_detected, on_error)

            # QRコードが検出されるまで待機（効率的なイベント待機）
            while self.running and not self.qr_detected_event.is_set():
                self.qr_detected_event.wait(timeout=0.1)

            if qr_data:
                return self._process_qr_data(qr_data)
            else:
                return False

        except KeyboardInterrupt:
            print("\nキャンセルされました")
            return False
        finally:
            # カメラが動作中の場合のみ停止
            if self.camera_reader.is_running:
                self.camera_reader.stop_camera()

    def add_account_from_image(self, image_path: str):
        """画像ファイルからQRコードを読み取ってアカウントを追加"""
        print(f"画像ファイルからQRコードを読み取ります: {image_path}")

        qr_data = self.camera_reader.read_qr_from_image(image_path)
        if qr_data:
            return self._process_qr_data(qr_data)
        else:
            print("QRコードの読み取りに失敗しました")
            return False

    def _process_qr_data(self, qr_data: str):
        """QRコードデータを処理してアカウントを追加"""
        try:
            # QRコードデータの形式を検証
            if not self.camera_reader.validate_qr_data(qr_data):
                print("無効なQRコード形式です")
                print("期待される形式: otpauth-migration://offline?data=[英数特殊記号文字列]")
                return False

            print("QRコードを解析中...")

            # DockerコンテナでQRコードを解析
            parsed_data = self.docker_manager.process_qr_url(qr_data)
            if not parsed_data:
                print("QRコードの解析に失敗しました")
                return False

            # アカウントを追加
            account_id = self.security_manager.add_account(
                device_name=parsed_data["device_name"],
                account_name=parsed_data["account_name"],
                issuer=parsed_data["issuer"],
                secret=parsed_data["secret"],
            )

            print(f"アカウントを追加しました: {parsed_data['account_name']}")
            print(f"アカウントID: {account_id}")
            return True

        except Exception as e:
            print(f"QRコード処理エラー: {str(e)}")
            return False

    def show_otp(self, account_id: str = None, show_all: bool = False):
        """OTPを表示"""
        try:
            if show_all:
                # 全アカウントのOTPを表示（復号化済み・secretを含む）
                accounts = self.security_manager.get_all_accounts()
                if not accounts:
                    print("登録されているアカウントがありません")
                    return False

                print("全アカウントのOTPを表示します...")
                print("Ctrl+C で停止")

                self.otp_generator.start_realtime_display(accounts)

                # ユーザーが停止するまで待機
                while self.running:
                    time.sleep(1)

            elif account_id:
                # 特定のアカウントのOTPを表示
                account = self.security_manager.get_account(account_id)
                if not account:
                    print(f"アカウントが見つかりません: {account_id}")
                    return False

                print(f"アカウント '{account['account_name']}' のOTPを表示します...")
                print("Ctrl+C で停止")

                self.otp_generator.start_realtime_display([account])

                # ユーザーが停止するまで待機
                while self.running:
                    time.sleep(1)

            else:
                print("アカウントIDまたは--allオプションを指定してください")

        except KeyboardInterrupt:
            print("\n表示を停止します...")
        finally:
            self.otp_generator.stop_realtime_display()

    def _print_accounts_table(self, accounts: List[Dict[str, Any]]):
        """アカウント情報をテーブル形式で表示（共通メソッド）"""
        if not accounts:
            return

        # 各列の最大幅を計算
        max_id_width = max(len(account["id"]) for account in accounts)
        max_name_width = max(len(account["account_name"]) for account in accounts)
        max_issuer_width = max(len(account["issuer"]) for account in accounts)

        # 最小幅を設定（ヘッダー名の長さ以上）
        id_width = max(max_id_width, 2)  # ID列
        name_width = max(max_name_width, 12)  # Account Name列
        issuer_width = max(max_issuer_width, 7)  # Issuer列
        created_width = 19  # Created列（固定）

        # 総幅を計算（列間のスペース3文字×3 = 9文字）
        total_width = id_width + name_width + issuer_width + created_width + 9

        print("-" * total_width)
        print(
            f"{'ID':<{id_width}} {'Account Name':<{name_width}} {'Issuer':<{issuer_width}} {'Created':<{created_width}}"
        )
        print("-" * total_width)

        for account in accounts:
            created_at = account["created_at"][:19].replace("T", " ")
            print(
                f"{account['id']:<{id_width}} {account['account_name']:<{name_width}} {account['issuer']:<{issuer_width}} {created_at:<{created_width}}"
            )

    def list_accounts(self):
        """アカウント一覧を表示"""
        accounts = self.security_manager.list_accounts()

        if not accounts:
            print("登録されているアカウントがありません")
            return

        print(f"登録済みアカウント ({len(accounts)}件):")
        self._print_accounts_table(accounts)

    def delete_account(self, account_id: str):
        """アカウントを削除"""
        account = self.security_manager.get_account(account_id)
        if not account:
            print(f"アカウントが見つかりません: {account_id}")
            return False

        print(f"アカウント '{account['account_name']}' を削除しますか？ (y/N): ", end="")
        confirm = input().strip().lower()

        if confirm == "y":
            success = self.security_manager.delete_account(account_id)
            if success:
                print("アカウントを削除しました")
            else:
                print("アカウントの削除に失敗しました")
            return success
        else:
            print("削除をキャンセルしました")
            return False

    def update_account(self, account_id: str, **kwargs):
        """アカウント情報を更新"""
        account = self.security_manager.get_account(account_id)
        if not account:
            print(f"アカウントが見つかりません: {account_id}")
            return False

        success = self.security_manager.update_account(account_id, **kwargs)
        if success:
            print("アカウント情報を更新しました")
        else:
            print("アカウント情報の更新に失敗しました")
        return success

    def search_accounts(self, keyword: str):
        """アカウントを検索"""
        accounts = self.security_manager.search_accounts(keyword)

        if not accounts:
            print(f"キーワード '{keyword}' に一致するアカウントが見つかりません")
            return

        print(f"検索結果 ({len(accounts)}件):")
        self._print_accounts_table(accounts)

    def setup_environment(self):
        """環境をセットアップ"""
        print("Docker環境をセットアップしています...")
        success = self.docker_manager.setup_environment()
        if success:
            print("環境のセットアップが完了しました")
        else:
            print("環境のセットアップに失敗しました")
        return success

    def delete_docker_image(self):
        """Dockerイメージを削除"""
        print("Dockerイメージを削除しています...")
        success = self.docker_manager.delete_image()
        if success:
            print("Dockerイメージの削除が完了しました")
        else:
            print("Dockerイメージの削除に失敗しました")
        return success

    def show_status(self):
        """アプリケーションの状態を表示"""
        print("アプリケーション状態:")
        print("-" * 40)

        # アカウント数
        account_count = self.security_manager.get_account_count()
        print(f"登録済みアカウント数: {account_count}")

        # カメラ状態
        camera_available = self.camera_reader.check_camera_available()
        print(f"カメラ利用可能: {'はい' if camera_available else 'いいえ'}")

        # Docker状態
        docker_available = self.docker_manager.check_docker_available()
        print(f"Docker利用可能: {'はい' if docker_available else 'いいえ'}")

        # カメラが動作中の場合は停止
        if self.camera_reader.is_running:
            self.camera_reader.stop_camera()


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="ワンタイムパスワード生成アプリケーション",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python main.py add --camera                    # カメラでQRコード読み取り
  python main.py add --image qr_code.png         # 画像ファイルからQRコード読み取り
  python main.py show --all                      # 全アカウントのOTP表示
  python main.py show <account_id>               # 特定アカウントのOTP表示
  python main.py list                             # アカウント一覧
  python main.py delete <account_id>             # アカウント削除
  python main.py update <account_id> --name "新名称"  # アカウント更新
  python main.py search "キーワード"              # アカウント検索
  python main.py setup                           # 環境セットアップ
  python main.py cleanup                         # Dockerイメージ削除
  python main.py status                          # 状態表示
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="利用可能なコマンド")

    # add コマンド
    add_parser = subparsers.add_parser("add", help="アカウントを追加")
    add_group = add_parser.add_mutually_exclusive_group(required=True)
    add_group.add_argument("--camera", action="store_true", help="カメラでQRコード読み取り")
    add_group.add_argument("--image", type=str, help="画像ファイルからQRコード読み取り")

    # show コマンド
    show_parser = subparsers.add_parser("show", help="OTPを表示")
    show_group = show_parser.add_mutually_exclusive_group(required=True)
    show_group.add_argument("--all", action="store_true", help="全アカウントのOTP表示")
    show_group.add_argument("account_id", nargs="?", help="アカウントID")

    # list コマンド
    subparsers.add_parser("list", help="アカウント一覧を表示")

    # delete コマンド
    delete_parser = subparsers.add_parser("delete", help="アカウントを削除")
    delete_parser.add_argument("account_id", help="アカウントID")

    # update コマンド
    update_parser = subparsers.add_parser("update", help="アカウント情報を更新")
    update_parser.add_argument("account_id", help="アカウントID")
    update_parser.add_argument("--name", type=str, help="新しいアカウント名")

    # search コマンド
    search_parser = subparsers.add_parser("search", help="アカウントを検索")
    search_parser.add_argument("keyword", help="検索キーワード")

    # setup コマンド
    subparsers.add_parser("setup", help="環境をセットアップ")

    # cleanup コマンド
    subparsers.add_parser("cleanup", help="Dockerイメージを削除")

    # status コマンド
    subparsers.add_parser("status", help="アプリケーションの状態を表示")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # アプリケーションを初期化
    app = OneTimePasswordApp()

    try:
        # コマンドを実行
        if args.command == "add":
            if args.camera:
                app.add_account_from_camera()
            elif args.image:
                app.add_account_from_image(args.image)

        elif args.command == "show":
            app.show_otp(args.account_id, args.all)

        elif args.command == "list":
            app.list_accounts()

        elif args.command == "delete":
            app.delete_account(args.account_id)

        elif args.command == "update":
            update_kwargs = {}
            if args.name:
                update_kwargs["account_name"] = args.name
            app.update_account(args.account_id, **update_kwargs)

        elif args.command == "search":
            app.search_accounts(args.keyword)

        elif args.command == "setup":
            app.setup_environment()

        elif args.command == "cleanup":
            app.delete_docker_image()

        elif args.command == "status":
            app.show_status()

    except Exception as e:
        print(f"エラー: {str(e)}")
        sys.exit(1)

    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
