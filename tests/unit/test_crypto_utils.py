"""
CryptoUtilsクラスのテスト
"""

import pytest
import json
from unittest.mock import patch, Mock
from src.crypto_utils import CryptoUtils


class TestCryptoUtils:
    """CryptoUtilsクラスのテスト"""

    @pytest.fixture
    def crypto_utils(self):
        """テスト用CryptoUtilsインスタンス"""
        # テスト用の固定パスワードを使用
        return CryptoUtils("test_password_for_unit_tests")

    def test_encrypt_normal(self, crypto_utils):
        """TC-CRYPTO-001: 正常な暗号化"""
        test_data = "test_secret_key_12345"
        
        encrypted = crypto_utils.encrypt(test_data)
        
        assert isinstance(encrypted, str)
        assert encrypted != test_data  # 暗号化されていることを確認
        assert len(encrypted) > 0

    def test_decrypt_normal(self, crypto_utils):
        """TC-CRYPTO-002: 正常な復号化"""
        test_data = "test_secret_key_12345"
        
        encrypted = crypto_utils.encrypt(test_data)
        decrypted = crypto_utils.decrypt(encrypted)
        
        assert decrypted == test_data

    def test_encrypt_decrypt_roundtrip(self, crypto_utils):
        """TC-CRYPTO-003: 暗号化・復号化のラウンドトリップ"""
        test_data = "test_secret_key_12345"
        
        encrypted = crypto_utils.encrypt(test_data)
        decrypted = crypto_utils.decrypt(encrypted)
        
        assert decrypted == test_data

    def test_encrypt_empty_string(self, crypto_utils):
        """TC-CRYPTO-004: 空文字列の暗号化"""
        test_data = ""
        
        encrypted = crypto_utils.encrypt(test_data)
        decrypted = crypto_utils.decrypt(encrypted)
        
        assert decrypted == test_data

    def test_encrypt_special_characters(self, crypto_utils):
        """TC-CRYPTO-005: 特殊文字の暗号化"""
        test_data = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        encrypted = crypto_utils.encrypt(test_data)
        decrypted = crypto_utils.decrypt(encrypted)
        
        assert decrypted == test_data

    def test_encrypt_japanese_characters(self, crypto_utils):
        """TC-CRYPTO-006: 日本語文字の暗号化"""
        test_data = "テストデータ日本語"
        
        encrypted = crypto_utils.encrypt(test_data)
        decrypted = crypto_utils.decrypt(encrypted)
        
        assert decrypted == test_data

    def test_encrypt_long_string(self, crypto_utils):
        """TC-CRYPTO-007: 長い文字列の暗号化"""
        test_data = "A" * 1000
        
        encrypted = crypto_utils.encrypt(test_data)
        decrypted = crypto_utils.decrypt(encrypted)
        
        assert decrypted == test_data

    def test_decrypt_invalid_data(self, crypto_utils):
        """TC-CRYPTO-008: 無効なデータの復号化"""
        invalid_data = "invalid_encrypted_data"
        
        with pytest.raises(Exception):
            crypto_utils.decrypt(invalid_data)

    def test_decrypt_corrupted_data(self, crypto_utils):
        """TC-CRYPTO-009: 破損したデータの復号化"""
        corrupted_data = "corrupted_base64_data!"
        
        with pytest.raises(Exception):
            crypto_utils.decrypt(corrupted_data)

    def test_encrypt_account_data_normal(self, crypto_utils):
        """TC-CRYPTO-010: 正常なアカウントデータ暗号化"""
        account_data = {
            'id': 'test-id',
            'account_name': 'test@example.com',
            'secret': 'SECRET123',
            'issuer': 'TestService'
        }
        
        encrypted_data = crypto_utils.encrypt_account_data(account_data)
        
        assert 'secret' not in encrypted_data
        assert 'encrypted_secret' in encrypted_data
        assert encrypted_data['id'] == 'test-id'
        assert encrypted_data['account_name'] == 'test@example.com'
        assert encrypted_data['issuer'] == 'TestService'

    def test_decrypt_account_data_normal(self, crypto_utils):
        """TC-CRYPTO-011: 正常なアカウントデータ復号化"""
        account_data = {
            'id': 'test-id',
            'account_name': 'test@example.com',
            'secret': 'SECRET123',
            'issuer': 'TestService'
        }
        
        encrypted_data = crypto_utils.encrypt_account_data(account_data)
        decrypted_data = crypto_utils.decrypt_account_data(encrypted_data)
        
        assert decrypted_data['secret'] == 'SECRET123'
        assert decrypted_data['id'] == 'test-id'
        assert decrypted_data['account_name'] == 'test@example.com'
        assert decrypted_data['issuer'] == 'TestService'
        assert 'encrypted_secret' not in decrypted_data

    def test_encrypt_account_data_no_secret(self, crypto_utils):
        """TC-CRYPTO-012: セキュリティコードなしのアカウントデータ暗号化"""
        account_data = {
            'id': 'test-id',
            'account_name': 'test@example.com',
            'issuer': 'TestService'
        }
        
        encrypted_data = crypto_utils.encrypt_account_data(account_data)
        
        assert encrypted_data == account_data  # 変更なし

    def test_decrypt_account_data_no_encrypted_secret(self, crypto_utils):
        """TC-CRYPTO-013: 暗号化セキュリティコードなしのアカウントデータ復号化"""
        account_data = {
            'id': 'test-id',
            'account_name': 'test@example.com',
            'issuer': 'TestService'
        }
        
        decrypted_data = crypto_utils.decrypt_account_data(account_data)
        
        assert decrypted_data == account_data  # 変更なし

    def test_custom_password(self):
        """TC-CRYPTO-014: カスタムパスワードでの暗号化"""
        custom_password = "custom_password_123"
        crypto_utils = CryptoUtils(custom_password)
        
        test_data = "test_secret"
        
        encrypted = crypto_utils.encrypt(test_data)
        decrypted = crypto_utils.decrypt(encrypted)
        
        assert decrypted == test_data

    def test_none_password(self):
        """TC-CRYPTO-015: Noneパスワードで環境変数から取得"""
        # 環境変数を設定してテスト
        with patch.dict('os.environ', {'OTP_MASTER_PASSWORD': 'env_test_password'}):
            crypto_utils = CryptoUtils(None)
            
            test_data = "test_secret"
            
            encrypted = crypto_utils.encrypt(test_data)
            decrypted = crypto_utils.decrypt(encrypted)
            
            assert decrypted == test_data

    def test_different_passwords_produce_different_encryption(self):
        """TC-CRYPTO-016: 異なるパスワードで異なる暗号化結果"""
        crypto1 = CryptoUtils("password1")
        crypto2 = CryptoUtils("password2")
        
        test_data = "test_secret"
        
        encrypted1 = crypto1.encrypt(test_data)
        encrypted2 = crypto2.encrypt(test_data)
        
        assert encrypted1 != encrypted2

    def test_same_password_produces_different_encryption(self):
        """TC-CRYPTO-017: 同じパスワードでも異なる暗号化結果（ソルトの効果）"""
        crypto1 = CryptoUtils("password")
        crypto2 = CryptoUtils("password")
        
        test_data = "test_secret"
        
        encrypted1 = crypto1.encrypt(test_data)
        encrypted2 = crypto2.encrypt(test_data)
        
        # 同じパスワードでも、暗号化結果は異なる（ランダム性のため）
        assert encrypted1 != encrypted2

    def test_encrypt_decrypt_multiple_times(self, crypto_utils):
        """TC-CRYPTO-018: 複数回の暗号化・復号化"""
        test_data = "test_secret"
        
        for _ in range(10):
            encrypted = crypto_utils.encrypt(test_data)
            decrypted = crypto_utils.decrypt(encrypted)
            assert decrypted == test_data

    def test_clear_memory(self, crypto_utils):
        """TC-CRYPTO-019: メモリクリア"""
        # メモリクリアがエラーなく実行されることを確認
        crypto_utils.clear_memory()
        
        # クリア後も暗号化・復号化が正常に動作することを確認
        test_data = "test_secret"
        encrypted = crypto_utils.encrypt(test_data)
        decrypted = crypto_utils.decrypt(encrypted)
        
        assert decrypted == test_data

    def test_encrypt_unicode_characters(self, crypto_utils):
        """TC-CRYPTO-020: Unicode文字の暗号化"""
        test_data = "🚀🌟💫✨🎉"
        
        encrypted = crypto_utils.encrypt(test_data)
        decrypted = crypto_utils.decrypt(encrypted)
        
        assert decrypted == test_data

    def test_encrypt_json_data(self, crypto_utils):
        """TC-CRYPTO-021: JSONデータの暗号化"""
        json_data = json.dumps({
            'name': 'test',
            'value': 123,
            'nested': {'key': 'value'}
        })
        
        encrypted = crypto_utils.encrypt(json_data)
        decrypted = crypto_utils.decrypt(encrypted)
        
        assert decrypted == json_data

    def test_encrypt_large_data(self, crypto_utils):
        """TC-CRYPTO-022: 大きなデータの暗号化"""
        large_data = "A" * 10000  # 10KB
        
        encrypted = crypto_utils.encrypt(large_data)
        decrypted = crypto_utils.decrypt(encrypted)
        
        assert decrypted == large_data

    def test_encrypt_binary_like_data(self, crypto_utils):
        """TC-CRYPTO-023: バイナリ風データの暗号化"""
        binary_like_data = "\\x00\\x01\\x02\\x03\\xff\\xfe\\xfd"
        
        encrypted = crypto_utils.encrypt(binary_like_data)
        decrypted = crypto_utils.decrypt(encrypted)
        
        assert decrypted == binary_like_data

    def test_key_derivation_consistency(self):
        """TC-CRYPTO-024: キー導出の一貫性（同じパスワード＋ソルトから同じキー）"""
        password = "test_password"
        salt = b'test_salt_16byte'  # 16バイトのテスト用ソルト
        
        crypto1 = CryptoUtils(password)
        crypto2 = CryptoUtils(password)
        
        # 同じパスワードとソルトから同じキーが導出されることを確認
        key1 = crypto1._derive_key(password, salt)
        key2 = crypto2._derive_key(password, salt)
        
        assert key1 == key2

    def test_encrypt_decrypt_with_different_instances(self):
        """TC-CRYPTO-025: 異なるインスタンス間での暗号化・復号化"""
        password = "shared_password"
        crypto1 = CryptoUtils(password)
        crypto2 = CryptoUtils(password)
        
        test_data = "test_secret"
        
        encrypted = crypto1.encrypt(test_data)
        decrypted = crypto2.decrypt(encrypted)
        
        assert decrypted == test_data