"""
Dockerコンテナ管理モジュール
otpauthコンテナの起動・停止・実行機能を提供
"""

import subprocess
import os
import tempfile
from typing import Dict, Optional
from urllib.parse import urlparse, parse_qs, unquote


class DockerManager:
    """Dockerコンテナ管理クラス"""

    def __init__(
        self, image_name: str = "otpauth:latest", container_name: str = "otpauth"
    ):
        """
        初期化

        Args:
            image_name: Dockerイメージ名
            container_name: コンテナ名
        """
        self.image_name = image_name
        self.container_name = container_name
        self.repository_url = "https://github.com/dim13/otpauth"
        self.local_repo_path: Optional[str] = None

    def check_docker_available(self) -> bool:
        """
        Dockerが利用可能かチェック

        Returns:
            Dockerが利用可能な場合True
        """
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_image_exists(self) -> bool:
        """
        otpauthイメージが存在するかチェック

        Returns:
            イメージが存在する場合True
        """
        try:
            result = subprocess.run(
                ["docker", "images", "-q", self.image_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0 and result.stdout.strip() != ""
        except Exception:
            return False

    def ensure_image_available(self) -> bool:
        """
        イメージが利用可能であることを保証（存在しない場合は自動ビルド）

        Returns:
            イメージが利用可能な場合True
        """
        if self.check_image_exists():
            print(f"Dockerイメージ '{self.image_name}' が見つかりました")
            return True

        print(
            f"Dockerイメージ '{self.image_name}' が見つかりません。自動ビルドを開始します..."
        )
        return self.setup_environment()

    def delete_image(self) -> bool:
        """
        otpauthイメージを削除

        Returns:
            削除成功の場合True
        """
        try:
            if not self.check_image_exists():
                print(f"イメージ '{self.image_name}' は存在しません")
                return True

            # イメージを削除
            result = subprocess.run(
                ["docker", "rmi", self.image_name],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print(f"Dockerイメージ '{self.image_name}' を削除しました")
                return True
            else:
                print(f"イメージ削除エラー: {result.stderr}")
                return False

        except Exception as e:
            print(f"イメージ削除エラー: {str(e)}")
            return False

    def clone_repository(self) -> bool:
        """
        otpauthリポジトリをクローン

        Returns:
            クローン成功の場合True
        """
        try:
            # 一時ディレクトリを作成
            temp_dir = tempfile.mkdtemp(prefix="otpauth_")
            self.local_repo_path = os.path.join(temp_dir, "otpauth")

            # git cloneを実行
            result = subprocess.run(
                ["git", "clone", self.repository_url, self.local_repo_path],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                print(f"リポジトリをクローンしました: {self.local_repo_path}")
                return True
            else:
                print(f"クローンエラー: {result.stderr}")
                return False

        except Exception as e:
            print(f"リポジトリクローンエラー: {str(e)}")
            return False

    def build_image(self) -> bool:
        """
        Dockerイメージをビルド

        Returns:
            ビルド成功の場合True
        """
        try:
            if not self.local_repo_path or not os.path.exists(self.local_repo_path):
                print("リポジトリがクローンされていません")
                return False

            # Dockerイメージをビルド
            result = subprocess.run(
                ["docker", "build", "-t", self.image_name, "."],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5分タイムアウト
            )

            if result.returncode == 0:
                print(f"Dockerイメージをビルドしました: {self.image_name}")
                return True
            else:
                print(f"ビルドエラー: {result.stderr}")
                return False

        except Exception as e:
            print(f"イメージビルドエラー: {str(e)}")
            return False

    def run_container(self, qr_url: str) -> tuple[bool, str]:
        """
        コンテナを実行してQRコードURLを解析

        Args:
            qr_url: QRコードのURL

        Returns:
            (成功フラグ, 出力結果)
        """
        try:
            # 既存のコンテナを停止・削除
            self.stop_container()

            # コンテナを実行
            cmd = [
                "docker",
                "run",
                "--name",
                self.container_name,
                "--rm",
                self.image_name,
                "-link",
                qr_url,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                output = result.stdout.strip()
                print(f"コンテナ実行成功: {output}")
                return True, output
            else:
                error = result.stderr.strip()
                print(f"コンテナ実行エラー: {error}")
                return False, error

        except Exception as e:
            error_msg = f"コンテナ実行エラー: {str(e)}"
            print(error_msg)
            return False, error_msg

    def stop_container(self) -> bool:
        """
        コンテナを停止

        Returns:
            停止成功の場合True
        """
        try:
            # コンテナを停止
            subprocess.run(
                ["docker", "stop", self.container_name], capture_output=True, timeout=10
            )

            # コンテナを削除
            subprocess.run(
                ["docker", "rm", self.container_name], capture_output=True, timeout=10
            )

            return True
        except Exception:
            return False

    def parse_otpauth_output(self, output: str) -> Optional[Dict[str, Optional[str]]]:
        """
        otpauthの出力を解析（urllib.parseを使用、OTP URI標準仕様準拠）

        Args:
            output: otpauthの出力文字列
            標準形式:
              - otpauth://totp/issuer:account?issuer=issuer&secret=...
              - otpauth://totp/account?issuer=issuer&secret=...

        Returns:
            解析結果の辞書

        Note:
            labelは "issuer:account" または "account" の形式。
            メールアドレス（例: test@example.com）もアカウント名として正しく扱う。
        """
        try:
            # URLをパース
            parsed_url = urlparse(output.strip())

            # スキーマとホストを検証
            if parsed_url.scheme != "otpauth":
                print(f"無効なスキーマ: {parsed_url.scheme}")
                return None

            if parsed_url.netloc != "totp":
                print(f"無効なotpauthタイプ: {parsed_url.netloc}")
                return None

            # クエリパラメータをパース
            params = parse_qs(parsed_url.query)
            issuer_param = params.get("issuer", [None])[0]

            # パスからlabelを取得（URLデコード）
            label = unquote(parsed_url.path.lstrip("/"))

            # labelから issuer と account を分離
            # 標準: "issuer:account" または "account"
            if ":" in label and issuer_param:
                # issuer:account 形式の場合、issuerを削除してaccountを取得
                # issuerパラメータと一致する場合のみ
                parts = label.split(":", 1)
                if parts[0] == issuer_param:
                    account_name = parts[1]
                else:
                    # issuerパラメータと不一致の場合、label全体をaccountとして扱う
                    account_name = label
            else:
                # シンプル形式（issuerなし）または ":" が含まれない場合
                account_name = label

            # device_name は issuer を使用、なければ account_name をフォールバック
            device_name = issuer_param if issuer_param else account_name

            # 各パラメータを取得（リストの最初の要素を取得）
            result = {
                "device_name": device_name,
                "account_name": account_name,
                "algorithm": params.get("algorithm", [None])[0],
                "digits": params.get("digits", [None])[0],
                "issuer": issuer_param,
                "period": params.get("period", [None])[0],
                "secret": params.get("secret", [None])[0],
            }

            # 必須パラメータの検証
            if not result["secret"]:
                print(f"秘密鍵が見つかりません: {output}")
                return None

            return result

        except Exception as e:
            print(f"出力解析エラー: {str(e)}")
            return None

    def process_qr_url(self, qr_url: str) -> Optional[Dict[str, Optional[str]]]:
        """
        QRコードURLを処理してセキュリティコードを抽出

        Args:
            qr_url: QRコードのURL

        Returns:
            抽出された情報の辞書
        """
        try:
            # URL形式を検証
            if not self._validate_qr_url(qr_url):
                print("無効なQRコードURL形式です")
                return None

            # イメージが利用可能であることを保証
            if not self.ensure_image_available():
                print("Dockerイメージの準備に失敗しました")
                return None

            # コンテナを実行
            success, output = self.run_container(qr_url)
            if not success:
                return None

            # 出力を解析
            parsed_data = self.parse_otpauth_output(output)
            return parsed_data

        except Exception as e:
            print(f"QRコードURL処理エラー: {str(e)}")
            return None

    def _validate_qr_url(self, qr_url: str) -> bool:
        """
        QRコードURLの形式を検証

        Args:
            qr_url: QRコードのURL

        Returns:
            有効な場合True
        """
        return qr_url.startswith("otpauth-migration://offline?data=")

    def cleanup(self) -> None:
        """リソースをクリーンアップ"""
        try:
            # コンテナを停止
            self.stop_container()

            # 一時ディレクトリを削除
            if self.local_repo_path:
                import shutil

                temp_dir = os.path.dirname(self.local_repo_path)
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    print("一時ファイルを削除しました")

        except Exception as e:
            print(f"クリーンアップエラー: {str(e)}")

    def setup_environment(self) -> bool:
        """
        環境をセットアップ（リポジトリクローン + イメージビルド）

        Returns:
            セットアップ成功の場合True
        """
        try:
            print("Docker環境をセットアップしています...")

            # Dockerが利用可能かチェック
            if not self.check_docker_available():
                print("Dockerが利用できません")
                return False

            # リポジトリをクローン
            if not self.clone_repository():
                return False

            # イメージをビルド
            if not self.build_image():
                return False

            print("Docker環境のセットアップが完了しました")
            return True

        except Exception as e:
            print(f"環境セットアップエラー: {str(e)}")
            return False


def test_docker_manager() -> None:
    """Dockerマネージャーのテスト"""
    manager = DockerManager()

    print("Dockerマネージャーテスト")
    print("-" * 40)

    # Docker利用可能性チェック
    docker_available = manager.check_docker_available()
    print(f"Docker利用可能: {docker_available}")

    if not docker_available:
        print("Dockerが利用できないため、テストをスキップします")
        return

    # 環境セットアップ
    setup_success = manager.setup_environment()
    print(f"環境セットアップ: {'成功' if setup_success else '失敗'}")

    if setup_success:
        # テスト用のQRコードURL（実際のURLに置き換えてください）
        test_qr_url = "otpauth-migration://offline?data=test_data"

        # QRコードURL処理テスト
        result = manager.process_qr_url(test_qr_url)
        if result:
            print(f"QRコード処理結果: {result}")
        else:
            print("QRコード処理に失敗しました")

        # クリーンアップ
        manager.cleanup()


if __name__ == "__main__":
    test_docker_manager()
