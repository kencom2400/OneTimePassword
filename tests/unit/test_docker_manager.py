"""
DockerManagerクラスのテスト
"""

import pytest
import subprocess
from unittest.mock import patch, Mock, MagicMock
from src.docker_manager import DockerManager


class TestDockerManager:
    """DockerManagerクラスのテスト"""

    @pytest.fixture
    def docker_manager(self):
        """テスト用DockerManagerインスタンス"""
        return DockerManager()

    def test_check_docker_available_true(self, docker_manager):
        """TC-DM-001: Docker利用可能性チェック（成功）"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Docker version 20.10.0"
            
            result = docker_manager.check_docker_available()
            
            assert result is True
            mock_run.assert_called_once_with(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

    def test_check_docker_available_false(self, docker_manager):
        """TC-DM-002: Docker利用可能性チェック（失敗）"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            
            result = docker_manager.check_docker_available()
            
            assert result is False

    def test_check_docker_available_not_installed(self, docker_manager):
        """TC-DM-003: Docker未インストール"""
        with patch('subprocess.run', side_effect=FileNotFoundError()):
            result = docker_manager.check_docker_available()
            
            assert result is False

    def test_check_image_exists_true(self, docker_manager):
        """TC-DM-004: イメージ存在チェック（存在）"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "abc123def456"
            
            result = docker_manager.check_image_exists()
            
            assert result is True
            mock_run.assert_called_once_with(
                ["docker", "images", "-q", "otpauth:latest"],
                capture_output=True,
                text=True,
                timeout=10
            )

    def test_check_image_exists_false(self, docker_manager):
        """TC-DM-005: イメージ存在チェック（不存在）"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""
            
            result = docker_manager.check_image_exists()
            
            assert result is False

    def test_setup_environment_success(self, docker_manager):
        """TC-DM-006: 環境セットアップ（成功）"""
        with patch.object(docker_manager, 'check_docker_available', return_value=True):
            with patch.object(docker_manager, 'clone_repository', return_value=True):
                with patch.object(docker_manager, 'build_image', return_value=True):
                    result = docker_manager.setup_environment()
                    
                    assert result is True

    def test_setup_environment_docker_unavailable(self, docker_manager):
        """TC-DM-007: Docker利用不可での環境セットアップ"""
        with patch.object(docker_manager, 'check_docker_available', return_value=False):
            result = docker_manager.setup_environment()
            
            assert result is False

    def test_clone_repository_success(self, docker_manager):
        """TC-DM-008: リポジトリクローン（成功）"""
        with patch('tempfile.mkdtemp', return_value="/tmp/test"):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                
                result = docker_manager.clone_repository()
                
                assert result is True
                assert docker_manager.local_repo_path == "/tmp/test/otpauth"

    def test_clone_repository_failure(self, docker_manager):
        """TC-DM-009: リポジトリクローン（失敗）"""
        with patch('tempfile.mkdtemp', return_value="/tmp/test"):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = "Clone failed"
                
                result = docker_manager.clone_repository()
                
                assert result is False

    def test_build_image_success(self, docker_manager):
        """TC-DM-010: イメージビルド（成功）"""
        docker_manager.local_repo_path = "/tmp/test/otpauth"
        
        with patch('os.path.exists', return_value=True):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                
                result = docker_manager.build_image()
                
                assert result is True
                mock_run.assert_called_once_with(
                    ["docker", "build", "-t", "otpauth:latest", "."],
                    cwd="/tmp/test/otpauth",
                    capture_output=True,
                    text=True,
                    timeout=300
                )

    def test_build_image_failure(self, docker_manager):
        """TC-DM-011: イメージビルド（失敗）"""
        docker_manager.local_repo_path = "/tmp/test/otpauth"
        
        with patch('os.path.exists', return_value=True):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = "Build failed"
                
                result = docker_manager.build_image()
                
                assert result is False

    def test_run_container_success(self, docker_manager):
        """TC-DM-012: コンテナ実行（成功）"""
        with patch.object(docker_manager, 'stop_container'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "otpauth://totp/test@example.com?algorithm=SHA1&digits=6&issuer=TestService&period=30&secret=JBSWY3DPEHPK3PXP"
                
                success, output = docker_manager.run_container("otpauth-migration://offline?data=test")
                
                assert success is True
                assert "otpauth://totp/test@example.com" in output

    def test_run_container_failure(self, docker_manager):
        """TC-DM-013: コンテナ実行（失敗）"""
        with patch.object(docker_manager, 'stop_container'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = "Container failed"
                
                success, output = docker_manager.run_container("otpauth-migration://offline?data=test")
                
                assert success is False
                assert "Container failed" in output

    def test_parse_otpauth_output_pattern1(self, docker_manager):
        """TC-DM-014: otpauth出力解析（パターン1: @なし）"""
        output = "otpauth://totp/kencom2400?algorithm=SHA1&digits=6&issuer=GitHub&period=30&secret=VHYHKC3QB22RE5HE"
        
        result = docker_manager.parse_otpauth_output(output)
        
        assert result is not None
        assert result['device_name'] == "kencom2400"
        assert result['account_name'] == "kencom2400"
        assert result['algorithm'] == "SHA1"
        assert result['digits'] == "6"
        assert result['issuer'] == "GitHub"
        assert result['period'] == "30"
        assert result['secret'] == "VHYHKC3QB22RE5HE"

    def test_parse_otpauth_output_pattern2(self, docker_manager):
        """TC-DM-015: otpauth出力解析（パターン2: @あり）"""
        output = "otpauth://totp/DeviceName@AccountName?algorithm=SHA1&digits=6&issuer=TestService&period=30&secret=JBSWY3DPEHPK3PXP"
        
        result = docker_manager.parse_otpauth_output(output)
        
        assert result is not None
        assert result['device_name'] == "DeviceName"
        assert result['account_name'] == "AccountName"
        assert result['algorithm'] == "SHA1"
        assert result['digits'] == "6"
        assert result['issuer'] == "TestService"
        assert result['period'] == "30"
        assert result['secret'] == "JBSWY3DPEHPK3PXP"

    def test_parse_otpauth_output_invalid(self, docker_manager):
        """TC-DM-016: otpauth出力解析（無効な形式）"""
        output = "invalid output format"
        
        result = docker_manager.parse_otpauth_output(output)
        
        assert result is None

    def test_process_qr_url_success(self, docker_manager):
        """TC-DM-017: QRコードURL処理（成功）"""
        qr_url = "otpauth-migration://offline?data=test_data"
        
        with patch.object(docker_manager, '_validate_qr_url', return_value=True):
            with patch.object(docker_manager, 'ensure_image_available', return_value=True):
                with patch.object(docker_manager, 'run_container', return_value=(True, "otpauth://totp/test@example.com?algorithm=SHA1&digits=6&issuer=TestService&period=30&secret=JBSWY3DPEHPK3PXP")):
                    result = docker_manager.process_qr_url(qr_url)
                    
                    assert result is not None
                    assert result['device_name'] == "test"
                    assert result['account_name'] == "example.com"

    def test_process_qr_url_invalid_format(self, docker_manager):
        """TC-DM-018: QRコードURL処理（無効な形式）"""
        qr_url = "invalid://url"
        
        with patch.object(docker_manager, '_validate_qr_url', return_value=False):
            result = docker_manager.process_qr_url(qr_url)
            
            assert result is None

    def test_process_qr_url_image_unavailable(self, docker_manager):
        """TC-DM-019: QRコードURL処理（イメージ利用不可）"""
        qr_url = "otpauth-migration://offline?data=test_data"
        
        with patch.object(docker_manager, '_validate_qr_url', return_value=True):
            with patch.object(docker_manager, 'ensure_image_available', return_value=False):
                result = docker_manager.process_qr_url(qr_url)
                
                assert result is None

    def test_ensure_image_available_exists(self, docker_manager):
        """TC-DM-020: イメージ利用可能性保証（既存）"""
        with patch.object(docker_manager, 'check_image_exists', return_value=True):
            result = docker_manager.ensure_image_available()
            
            assert result is True

    def test_ensure_image_available_build(self, docker_manager):
        """TC-DM-021: イメージ利用可能性保証（ビルド）"""
        with patch.object(docker_manager, 'check_image_exists', return_value=False):
            with patch.object(docker_manager, 'setup_environment', return_value=True):
                result = docker_manager.ensure_image_available()
                
                assert result is True

    def test_delete_image_success(self, docker_manager):
        """TC-DM-022: イメージ削除（成功）"""
        with patch.object(docker_manager, 'check_image_exists', return_value=True):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                
                result = docker_manager.delete_image()
                
                assert result is True
                mock_run.assert_called_once_with(
                    ["docker", "rmi", "otpauth:latest"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

    def test_delete_image_failure(self, docker_manager):
        """TC-DM-023: イメージ削除（失敗）"""
        with patch.object(docker_manager, 'check_image_exists', return_value=True):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = "Delete failed"
                
                result = docker_manager.delete_image()
                
                assert result is False

    def test_delete_image_docker_unavailable(self, docker_manager):
        """TC-DM-024: Docker利用不可でのイメージ削除"""
        with patch.object(docker_manager, 'check_image_exists', side_effect=Exception()):
            result = docker_manager.delete_image()
            
            assert result is False

    def test_stop_container_success(self, docker_manager):
        """TC-DM-025: コンテナ停止（成功）"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = docker_manager.stop_container()
            
            assert result is True
            # stopとrmの両方が呼ばれることを確認
            assert mock_run.call_count == 2

    def test_stop_container_failure(self, docker_manager):
        """TC-DM-026: コンテナ停止（失敗）"""
        with patch('subprocess.run', side_effect=Exception()):
            result = docker_manager.stop_container()
            
            assert result is False

    def test_cleanup_success(self, docker_manager):
        """TC-DM-027: クリーンアップ（成功）"""
        docker_manager.local_repo_path = "/tmp/test/otpauth"
        
        with patch.object(docker_manager, 'stop_container'):
            with patch('os.path.exists', return_value=True):
                with patch('shutil.rmtree'):
                    docker_manager.cleanup()
                    
                    # エラーが発生しないことを確認

    def test_validate_qr_url_valid(self, docker_manager):
        """TC-DM-028: QRコードURL検証（有効）"""
        valid_url = "otpauth-migration://offline?data=test_data"
        
        result = docker_manager._validate_qr_url(valid_url)
        
        assert result is True

    def test_validate_qr_url_invalid(self, docker_manager):
        """TC-DM-029: QRコードURL検証（無効）"""
        invalid_url = "http://example.com"
        
        result = docker_manager._validate_qr_url(invalid_url)
        
        assert result is False

    def test_maximum_qr_url_length(self, docker_manager):
        """TC-DM-030: 最大QRコードURL長"""
        long_url = "otpauth-migration://offline?data=" + "x" * 1000
        
        with patch.object(docker_manager, '_validate_qr_url', return_value=True):
            with patch.object(docker_manager, 'ensure_image_available', return_value=True):
                with patch.object(docker_manager, 'run_container', return_value=(True, "otpauth://totp/test@example.com?algorithm=SHA1&digits=6&issuer=TestService&period=30&secret=JBSWY3DPEHPK3PXP")):
                    result = docker_manager.process_qr_url(long_url)
                    
                    assert result is not None

    def test_docker_service_stopped(self, docker_manager):
        """TC-DM-031: Dockerサービス停止"""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired("docker", 10)):
            result = docker_manager.check_docker_available()
            
            assert result is False

    def test_multiple_qr_processing(self, docker_manager):
        """TC-DM-032: 複数QRコードの連続処理"""
        qr_data_list = [
            "otpauth-migration://offline?data=test1",
            "otpauth-migration://offline?data=test2",
            "otpauth-migration://offline?data=test3"
        ]
        
        with patch.object(docker_manager, '_validate_qr_url', return_value=True):
            with patch.object(docker_manager, 'ensure_image_available', return_value=True):
                with patch.object(docker_manager, 'run_container', return_value=(True, "otpauth://totp/test@example.com?algorithm=SHA1&digits=6&issuer=TestService&period=30&secret=JBSWY3DPEHPK3PXP")):
                    results = []
                    for qr_data in qr_data_list:
                        result = docker_manager.process_qr_url(qr_data)
                        results.append(result)
                    
                    assert len(results) == 3
                    assert all(result is not None for result in results)