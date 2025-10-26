"""
テスト共通フィクスチャ
"""

import pytest
import tempfile
import os
import json
import uuid
from typing import Dict, Any, List
from unittest.mock import Mock, patch


@pytest.fixture
def temp_data_dir():
    """一時的なデータディレクトリを作成"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_account_data():
    """テスト用アカウントデータ"""
    return {
        "device_name": "TestDevice",
        "account_name": "test@example.com",
        "issuer": "TestService",
        "secret": "JBSWY3DPEHPK3PXP",
    }


@pytest.fixture
def sample_accounts():
    """テスト用複数アカウントデータ"""
    return [
        {
            "id": str(uuid.uuid4()),
            "device_name": "TestDevice1",
            "account_name": "test1@example.com",
            "issuer": "TestService1",
            "secret": "JBSWY3DPEHPK3PXP",
            "created_at": "2025-01-26T10:00:00Z",
        },
        {
            "id": str(uuid.uuid4()),
            "device_name": "TestDevice2",
            "account_name": "test2@example.com",
            "issuer": "TestService2",
            "secret": "GEZDGNBVGY3TQOJQ",
            "created_at": "2025-01-26T11:00:00Z",
        },
    ]


@pytest.fixture
def sample_qr_data():
    """テスト用QRコードデータ"""
    return "otpauth-migration://offline?data=test_qr_data"


@pytest.fixture
def sample_otpauth_url():
    """テスト用otpauth URL"""
    return "otpauth://totp/test@example.com?algorithm=SHA1&digits=6&issuer=TestService&period=30&secret=JBSWY3DPEHPK3PXP"


@pytest.fixture
def sample_encrypted_data():
    """テスト用暗号化データ"""
    return {
        "data": "encrypted_data_here",
        "salt": "salt_here",
        "nonce": "nonce_here",
        "tag": "tag_here",
    }


@pytest.fixture
def mock_camera():
    """モックカメラ"""
    mock = Mock()
    mock.isOpened.return_value = True
    mock.read.return_value = (True, None)
    mock.release.return_value = None
    return mock


@pytest.fixture
def mock_docker_client():
    """モックDockerクライアント"""
    mock = Mock()
    mock.images.list.return_value = []
    mock.containers.run.return_value = Mock()
    return mock


@pytest.fixture
def temp_image_file():
    """一時的な画像ファイル"""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        # ダミーのPNGデータを書き込み
        f.write(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def mock_time():
    """モック時刻"""
    with patch("time.time") as mock:
        mock.return_value = 1640995200.0  # 2022-01-01 00:00:00 UTC
        yield mock
