"""
暗号化ユーティリティモジュール
セキュリティコードの暗号化・復号化機能を提供
"""

import os
import base64
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json


class CryptoUtils:
    """暗号化・復号化のユーティリティクラス"""
    
    # ソルトのバイト長（16バイト = 128ビット）
    SALT_LENGTH = 16
    # PBKDF2の反復回数
    PBKDF2_ITERATIONS = 100000
    
    def __init__(self, password: str = None):
        """
        初期化
        
        Args:
            password: 暗号化用パスワード（Noneの場合は環境変数またはユーザー入力から取得）
        """
        self.password = password or self._get_password()
        if not self.password:
            raise ValueError("暗号化パスワードが提供されていません。環境変数OTP_MASTER_PASSWORDを設定するか、パスワードを指定してください。")
    
    def _get_password(self) -> str:
        """
        パスワードを安全に取得
        
        優先順位:
        1. 環境変数 OTP_MASTER_PASSWORD
        2. 環境変数 OTP_PASSWORD_FILE からファイルパスを読み込み
        3. ユーザー入力（インタラクティブモード時のみ）
        
        Returns:
            パスワード文字列
        """
        # 1. 環境変数から直接取得
        password = os.environ.get("OTP_MASTER_PASSWORD", "")
        if password:
            return password
        
        # 2. ファイルから取得
        password_file = os.environ.get("OTP_PASSWORD_FILE", "")
        if password_file and os.path.exists(password_file):
            try:
                with open(password_file, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                print(f"警告: パスワードファイルの読み込みに失敗: {str(e)}")
        
        # 3. インタラクティブモードの場合のみユーザー入力
        # 非インタラクティブモード（テストやCI/CD）では空文字列を返す
        if os.isatty(0):  # 標準入力が端末かチェック
            try:
                return getpass.getpass("マスターパスワードを入力してください: ")
            except Exception:
                pass
        
        return ""
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        パスワードとソルトから暗号化キーを導出
        
        Args:
            password: マスターパスワード
            salt: ランダムに生成されたソルト
            
        Returns:
            導出された暗号化キー
        """
        password_bytes = password.encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.PBKDF2_ITERATIONS,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt(self, data: str) -> str:
        """
        データを暗号化（各暗号化ごとにランダムなソルトを生成）
        
        Args:
            data: 暗号化するデータ
            
        Returns:
            暗号化されたデータ（Base64エンコード）
            形式: base64(salt + encrypted_data)
        """
        try:
            # ランダムなソルトを生成
            salt = os.urandom(self.SALT_LENGTH)
            
            # ソルトから暗号化キーを導出
            key = self._derive_key(self.password, salt)
            cipher = Fernet(key)
            
            # データを暗号化
            encrypted_data = cipher.encrypt(data.encode())
            
            # ソルト + 暗号化データを結合してBase64エンコード
            combined = salt + encrypted_data
            return base64.urlsafe_b64encode(combined).decode()
        except Exception as e:
            raise Exception(f"暗号化エラー: {str(e)}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        データを復号化（ソルトを抽出して使用）
        
        Args:
            encrypted_data: 暗号化されたデータ（Base64エンコード）
            形式: base64(salt + encrypted_data)
            
        Returns:
            復号化されたデータ
        """
        try:
            # Base64デコード
            combined = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # ソルトと暗号化データを分離
            salt = combined[:self.SALT_LENGTH]
            encrypted_bytes = combined[self.SALT_LENGTH:]
            
            # ソルトから暗号化キーを導出
            key = self._derive_key(self.password, salt)
            cipher = Fernet(key)
            
            # データを復号化
            decrypted_data = cipher.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            raise Exception(f"復号化エラー: {str(e)}")
    
    def encrypt_account_data(self, account_data: dict) -> dict:
        """
        アカウントデータを暗号化
        
        Args:
            account_data: アカウントデータ辞書
            
        Returns:
            セキュリティコードが暗号化されたアカウントデータ
        """
        encrypted_data = account_data.copy()
        if 'secret' in encrypted_data:
            encrypted_data['encrypted_secret'] = self.encrypt(encrypted_data['secret'])
            del encrypted_data['secret']
        return encrypted_data
    
    def decrypt_account_data(self, encrypted_account_data: dict) -> dict:
        """
        アカウントデータを復号化
        
        Args:
            encrypted_account_data: 暗号化されたアカウントデータ
            
        Returns:
            セキュリティコードが復号化されたアカウントデータ
        """
        decrypted_data = encrypted_account_data.copy()
        if 'encrypted_secret' in decrypted_data:
            decrypted_data['secret'] = self.decrypt(decrypted_data['encrypted_secret'])
            del decrypted_data['encrypted_secret']
        return decrypted_data
    
    def clear_memory(self):
        """メモリ上の機密データをクリア"""
        # Pythonのガベージコレクションに依存
        # 実際の実装では、より積極的なメモリクリアを行う
        import gc
        gc.collect()


def create_crypto_utils(password: str = None) -> CryptoUtils:
    """
    CryptoUtilsインスタンスを作成するファクトリ関数
    
    Args:
        password: 暗号化用パスワード
        
    Returns:
        CryptoUtilsインスタンス
    """
    return CryptoUtils(password)


# テスト用の関数
def test_encryption():
    """暗号化・復号化のテスト"""
    # テスト用のパスワードを使用
    crypto = CryptoUtils("test_password_for_demo")
    
    test_data = "test_secret_key_12345"
    encrypted = crypto.encrypt(test_data)
    decrypted = crypto.decrypt(encrypted)
    
    print(f"元データ: {test_data}")
    print(f"暗号化後: {encrypted}")
    print(f"復号化後: {decrypted}")
    print(f"テスト結果: {'成功' if test_data == decrypted else '失敗'}")


if __name__ == "__main__":
    test_encryption()
