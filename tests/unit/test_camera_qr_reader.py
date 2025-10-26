"""
CameraQRReaderクラスのテスト
"""

import pytest
import cv2
import numpy as np
from unittest.mock import patch, Mock, MagicMock
from src.camera_qr_reader import CameraQRReader


class TestCameraQRReader:
    """CameraQRReaderクラスのテスト"""

    @pytest.fixture
    def camera_reader(self):
        """テスト用CameraQRReaderインスタンス"""
        return CameraQRReader()

    def test_check_camera_available_true(self, camera_reader):
        """TC-CAM-001: カメラ利用可能性チェック（成功）"""
        with patch("cv2.VideoCapture") as mock_video_capture:
            mock_camera = Mock()
            mock_camera.isOpened.return_value = True
            mock_video_capture.return_value = mock_camera

            result = camera_reader.check_camera_available()

            assert result is True
            mock_video_capture.assert_called_once_with(0)
            mock_camera.release.assert_called_once()

    def test_check_camera_available_false(self, camera_reader):
        """TC-CAM-002: カメラ利用可能性チェック（失敗）"""
        with patch("cv2.VideoCapture") as mock_video_capture:
            mock_camera = Mock()
            mock_camera.isOpened.return_value = False
            mock_video_capture.return_value = mock_camera

            result = camera_reader.check_camera_available()

            assert result is False
            mock_video_capture.assert_called_once_with(0)
            # isOpened()がFalseの場合、release()は呼ばれない
            mock_camera.release.assert_not_called()

    def test_check_camera_available_exception(self, camera_reader):
        """TC-CAM-003: カメラ利用可能性チェック（例外）"""
        with patch("cv2.VideoCapture", side_effect=Exception("Camera error")):
            result = camera_reader.check_camera_available()

            assert result is False

    def test_read_qr_from_image_valid(self, camera_reader):
        """TC-CAM-004: 画像からのQRコード読み取り（成功）"""
        test_image_path = "test_qr.png"
        mock_qr_data = "otpauth-migration://offline?data=test_data"

        with patch("os.path.exists", return_value=True):
            with patch("cv2.imread") as mock_imread:
                with patch("cv2.QRCodeDetector") as mock_detector_class:
                    mock_detector = Mock()
                    mock_detector_class.return_value = mock_detector
                    mock_detector.detectAndDecode.return_value = (
                        mock_qr_data,
                        None,
                        None,
                    )

                    # モック画像を作成
                    mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
                    mock_imread.return_value = mock_image

                    result = camera_reader.read_qr_from_image(test_image_path)

                    assert result == mock_qr_data
                    mock_imread.assert_called_once_with(test_image_path)
                    mock_detector.detectAndDecode.assert_called_once_with(mock_image)

    def test_read_qr_from_image_no_qr(self, camera_reader):
        """TC-CAM-005: 画像にQRコードなし"""
        test_image_path = "test_no_qr.png"

        with patch("cv2.imread") as mock_imread:
            with patch("cv2.QRCodeDetector") as mock_detector_class:
                mock_detector = Mock()
                mock_detector_class.return_value = mock_detector
                mock_detector.detectAndDecode.return_value = (False, "", None)

                mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
                mock_imread.return_value = mock_image

                result = camera_reader.read_qr_from_image(test_image_path)

                assert result is None

    def test_read_qr_from_image_file_not_found(self, camera_reader):
        """TC-CAM-006: 画像ファイルが見つからない"""
        test_image_path = "nonexistent.png"

        with patch("cv2.imread", return_value=None):
            result = camera_reader.read_qr_from_image(test_image_path)

            assert result is None

    def test_read_qr_from_image_invalid_format(self, camera_reader):
        """TC-CAM-007: 無効な画像形式"""
        test_image_path = "test.txt"

        with patch("cv2.imread", return_value=None):
            result = camera_reader.read_qr_from_image(test_image_path)

            assert result is None

    def test_read_qr_from_image_exception(self, camera_reader):
        """TC-CAM-008: 画像読み取り例外"""
        test_image_path = "test_qr.png"

        with patch("cv2.imread", side_effect=Exception("Image error")):
            result = camera_reader.read_qr_from_image(test_image_path)

            assert result is None

    def test_validate_qr_data_valid(self, camera_reader):
        """TC-CAM-009: QRデータ検証（有効）"""
        valid_qr_data = "otpauth-migration://offline?data=test_data"

        result = camera_reader.validate_qr_data(valid_qr_data)

        assert result is True

    def test_validate_qr_data_invalid(self, camera_reader):
        """TC-CAM-010: QRデータ検証（無効）"""
        invalid_qr_data = "http://example.com"

        result = camera_reader.validate_qr_data(invalid_qr_data)

        assert result is False

    def test_validate_qr_data_none(self, camera_reader):
        """TC-CAM-011: QRデータ検証（None）"""
        result = camera_reader.validate_qr_data(None)

        assert result is False

    def test_validate_qr_data_empty(self, camera_reader):
        """TC-CAM-012: QRデータ検証（空文字）"""
        result = camera_reader.validate_qr_data("")

        assert result is False

    def test_start_camera_success(self, camera_reader):
        """TC-CAM-013: カメラ開始（成功）"""
        with patch("cv2.VideoCapture") as mock_video_capture:
            mock_camera = Mock()
            mock_camera.isOpened.return_value = True
            mock_video_capture.return_value = mock_camera

            result = camera_reader.start_camera()

            assert result is True
            assert camera_reader.is_running is True
            mock_video_capture.assert_called_once_with(0)
            mock_camera.set.assert_any_call(cv2.CAP_PROP_FRAME_WIDTH, 640)

    def test_start_camera_unavailable(self, camera_reader):
        """TC-CAM-014: カメラ開始（利用不可）"""
        with patch("cv2.VideoCapture") as mock_video_capture:
            mock_camera = Mock()
            mock_camera.isOpened.return_value = False
            mock_video_capture.return_value = mock_camera

            result = camera_reader.start_camera()

            assert result is False
            assert camera_reader.is_running is False

    def test_start_camera_already_running(self, camera_reader):
        """TC-CAM-015: カメラ開始（既に動作中）"""
        camera_reader.is_running = True

        result = camera_reader.start_camera()

        # 既に動作中の場合、Trueを返す
        assert result is True

    def test_stop_camera_success(self, camera_reader):
        """TC-CAM-016: カメラ停止（成功）"""
        camera_reader.is_running = True
        mock_camera = Mock()
        camera_reader.camera = mock_camera
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        camera_reader.read_thread = mock_thread

        camera_reader.stop_camera()

        assert camera_reader.is_running is False
        mock_camera.release.assert_called_once()
        mock_thread.join.assert_called_once_with(timeout=3)

    def test_stop_camera_not_running(self, camera_reader):
        """TC-CAM-017: カメラ停止（動作中でない）"""
        camera_reader.is_running = False

        camera_reader.stop_camera()

        assert camera_reader.is_running is False

    def test_stop_camera_exception(self, camera_reader):
        """TC-CAM-018: カメラ停止（例外）"""
        camera_reader.is_running = True
        camera_reader.camera = Mock()
        camera_reader.read_thread = Mock()
        camera_reader.read_thread.is_alive.side_effect = Exception("Thread error")

        camera_reader.stop_camera()

        assert camera_reader.is_running is False

    def test_qr_detection_loop_success(self, camera_reader):
        """TC-CAM-022: QR検出ループ（成功）"""
        mock_qr_data = "otpauth-migration://offline?data=test_data"
        camera_reader.camera = Mock()
        camera_reader.camera.read.return_value = (
            True,
            np.zeros((100, 100, 3), dtype=np.uint8),
        )
        camera_reader.is_running = True

        with patch("cv2.QRCodeDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector_class.return_value = mock_detector
            mock_detector.detectAndDecode.return_value = (mock_qr_data, None, None)

            # _qr_detection_loopはコールバックを使用するため、テスト方法を変更
            # 実際にはこのメソッドは直接テストするのではなく、
            # start_qr_detection経由でテストする方が適切
            # ここでは簡略化して、QRコードが検出されたことのみを確認
            with patch("time.sleep", side_effect=[None, KeyboardInterrupt]):
                try:
                    camera_reader._qr_detection_loop()
                except KeyboardInterrupt:
                    pass

            # QRCodeDetectorが呼ばれたことを確認
            mock_detector.detectAndDecode.assert_called()

    def test_qr_detection_loop_no_qr(self, camera_reader):
        """TC-CAM-023: QR検出ループ（QRコードなし）"""
        camera_reader.camera = Mock()
        camera_reader.camera.read.return_value = (
            True,
            np.zeros((100, 100, 3), dtype=np.uint8),
        )

        with patch("cv2.QRCodeDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector_class.return_value = mock_detector
            mock_detector.detectAndDecode.return_value = (False, "", None)

            with patch("time.sleep", side_effect=KeyboardInterrupt):
                result = camera_reader._qr_detection_loop()

                assert result is None

    def test_qr_detection_loop_camera_error(self, camera_reader):
        """TC-CAM-024: QR検出ループ（カメラエラー）"""
        camera_reader.camera = Mock()
        camera_reader.camera.read.return_value = (False, None)

        with patch("time.sleep", side_effect=KeyboardInterrupt):
            result = camera_reader._qr_detection_loop()

            assert result is None

    def test_qr_detection_loop_exception(self, camera_reader):
        """TC-CAM-025: QR検出ループ（例外）"""
        camera_reader.camera = Mock()
        camera_reader.camera.read.side_effect = Exception("Camera error")

        with patch("time.sleep", side_effect=KeyboardInterrupt):
            result = camera_reader._qr_detection_loop()

            assert result is None

    def test_maximum_image_size(self, camera_reader):
        """TC-CAM-026: 最大画像サイズ"""
        test_image_path = "large_image.png"

        with patch("os.path.exists", return_value=True):
            with patch("cv2.imread") as mock_imread:
                with patch("cv2.QRCodeDetector") as mock_detector_class:
                    mock_detector = Mock()
                    mock_detector_class.return_value = mock_detector
                    mock_detector.detectAndDecode.return_value = (
                        "test_data",
                        None,
                        None,
                    )

                    # 大きな画像を作成
                    large_image = np.zeros((4000, 4000, 3), dtype=np.uint8)
                    mock_imread.return_value = large_image

                    result = camera_reader.read_qr_from_image(test_image_path)

                    assert result == "test_data"

    def test_minimum_image_size(self, camera_reader):
        """TC-CAM-027: 最小画像サイズ"""
        test_image_path = "small_image.png"

        with patch("os.path.exists", return_value=True):
            with patch("cv2.imread") as mock_imread:
                with patch("cv2.QRCodeDetector") as mock_detector_class:
                    mock_detector = Mock()
                    mock_detector_class.return_value = mock_detector
                    mock_detector.detectAndDecode.return_value = (
                        "test_data",
                        None,
                        None,
                    )

                    # 小さな画像を作成
                    small_image = np.zeros((10, 10, 3), dtype=np.uint8)
                    mock_imread.return_value = small_image

                    result = camera_reader.read_qr_from_image(test_image_path)

                    assert result == "test_data"

    def test_multiple_qr_codes_in_image(self, camera_reader):
        """TC-CAM-028: 画像内の複数QRコード"""
        test_image_path = "multiple_qr.png"

        with patch("os.path.exists", return_value=True):
            with patch("cv2.imread") as mock_imread:
                with patch("cv2.QRCodeDetector") as mock_detector_class:
                    mock_detector = Mock()
                    mock_detector_class.return_value = mock_detector
                    # 最初のQRコードを返す
                    mock_detector.detectAndDecode.return_value = (
                        "first_qr_data",
                        None,
                        None,
                    )

                    mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
                    mock_imread.return_value = mock_image

                    result = camera_reader.read_qr_from_image(test_image_path)

                    assert result == "first_qr_data"

    def test_camera_timeout(self, camera_reader):
        """TC-CAM-029: カメラタイムアウト"""
        camera_reader.camera = Mock()
        camera_reader.camera.read.return_value = (
            True,
            np.zeros((100, 100, 3), dtype=np.uint8),
        )

        with patch("cv2.QRCodeDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector_class.return_value = mock_detector
            mock_detector.detectAndDecode.return_value = (False, "", None)

            # タイムアウトをシミュレート
            with patch("time.sleep", side_effect=KeyboardInterrupt):
                result = camera_reader._qr_detection_loop()

                assert result is None

    def test_camera_resource_cleanup(self, camera_reader):
        """TC-CAM-030: カメラリソースクリーンアップ"""
        camera_reader.is_running = True
        mock_camera = Mock()
        camera_reader.camera = mock_camera
        mock_thread = Mock()
        mock_thread.is_alive.return_value = False
        camera_reader.read_thread = mock_thread

        camera_reader.stop_camera()

        assert camera_reader.is_running is False
        mock_camera.release.assert_called_once()
