"""
カメラQRコード読み取りモジュール
PCカメラを使用してQRコードを読み取る機能を提供
"""

import cv2
import numpy as np
import time
import threading
from typing import Optional, Tuple, Callable
import os


class CameraQRReader:
    """カメラQRコード読み取りクラス"""
    
    def __init__(self, camera_index: int = 0):
        """
        初期化
        
        Args:
            camera_index: カメラのインデックス（通常は0）
        """
        self.camera_index = camera_index
        self.camera = None
        self.is_running = False
        self.read_thread = None
        self.on_qr_detected = None
        self.on_error = None
    
    def check_camera_available(self) -> bool:
        """
        カメラが利用可能かチェック
        
        Returns:
            カメラが利用可能な場合True
        """
        try:
            camera = cv2.VideoCapture(self.camera_index)
            if camera.isOpened():
                camera.release()
                return True
            return False
        except Exception:
            return False
    
    def get_camera_list(self) -> list:
        """
        利用可能なカメラのリストを取得
        
        Returns:
            カメラインデックスのリスト
        """
        available_cameras = []
        for i in range(10):  # 最大10個のカメラをチェック
            try:
                camera = cv2.VideoCapture(i)
                if camera.isOpened():
                    available_cameras.append(i)
                camera.release()
            except Exception:
                continue
        return available_cameras
    
    def start_camera(self) -> bool:
        """
        カメラを開始
        
        Returns:
            開始成功の場合True
        """
        try:
            if self.is_running:
                print("カメラは既に起動しています")
                return True
            
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                print(f"カメラ {self.camera_index} を開けませんでした")
                return False
            
            # カメラ設定
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_running = True
            print(f"カメラ {self.camera_index} を開始しました")
            return True
            
        except Exception as e:
            print(f"カメラ開始エラー: {str(e)}")
            return False
    
    def stop_camera(self):
        """カメラを停止"""
        try:
            # 既に停止済みの場合は何もしない
            if not self.is_running:
                return
                
            self.is_running = False
            
            # スレッドの停止を待機
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join(timeout=3)  # タイムアウトを3秒に延長
            
            # カメラリソースの解放
            if self.camera:
                self.camera.release()
                self.camera = None
            
            print("カメラを停止しました")
            
        except Exception as e:
            print(f"カメラ停止エラー: {str(e)}")
            # エラーが発生してもカメラリソースは解放
            try:
                if self.camera:
                    self.camera.release()
                    self.camera = None
            except:
                pass
    
    def start_qr_detection(self, on_qr_detected: Callable = None, on_error: Callable = None):
        """
        QRコード検出を開始
        
        Args:
            on_qr_detected: QRコード検出時のコールバック関数
            on_error: エラー時のコールバック関数
        """
        self.on_qr_detected = on_qr_detected
        self.on_error = on_error
        
        if not self.start_camera():
            if self.on_error:
                self.on_error("カメラの開始に失敗しました")
            return
        
        self.read_thread = threading.Thread(target=self._qr_detection_loop)
        self.read_thread.daemon = True
        self.read_thread.start()
    
    def _qr_detection_loop(self):
        """QRコード検出ループ"""
        last_detection_time = 0
        detection_cooldown = 2.0  # 2秒間のクールダウン
        
        try:
            while self.is_running:
                try:
                    if not self.camera or not self.camera.isOpened():
                        break
                        
                    ret, frame = self.camera.read()
                    if not ret:
                        if self.on_error:
                            self.on_error("フレームの読み取りに失敗しました")
                        break
                    
                    # QRコードを検出（OpenCVを使用）
                    qr_detector = cv2.QRCodeDetector()
                    qr_data, bbox, _ = qr_detector.detectAndDecode(frame)
                    
                    if qr_data:
                        current_time = time.time()
                        if current_time - last_detection_time > detection_cooldown:
                            print(f"QRコード検出: {qr_data}")
                            
                            if self.on_qr_detected:
                                self.on_qr_detected(qr_data)
                            
                            last_detection_time = current_time
                    
                    # フレームレート制御
                    time.sleep(1/30)  # 30fps
                    
                except Exception as e:
                    if self.on_error:
                        self.on_error(f"QRコード検出エラー: {str(e)}")
                    break
        finally:
            # ループ終了時にカメラリソースのみ解放（stop_cameraは呼ばない）
            try:
                if self.camera:
                    self.camera.release()
                    self.camera = None
                self.is_running = False
            except Exception as e:
                print(f"カメラリソース解放エラー: {str(e)}")
    
    def read_qr_from_image(self, image_path: str) -> Optional[str]:
        """
        画像ファイルからQRコードを読み取り
        
        Args:
            image_path: 画像ファイルのパス
            
        Returns:
            QRコードのデータ（検出できない場合はNone）
        """
        try:
            if not os.path.exists(image_path):
                print(f"画像ファイルが見つかりません: {image_path}")
                return None
            
            # 画像を読み込み
            image = cv2.imread(image_path)
            if image is None:
                print(f"画像の読み込みに失敗しました: {image_path}")
                return None
            
            # QRコードを検出（OpenCVを使用）
            qr_detector = cv2.QRCodeDetector()
            qr_data, bbox, _ = qr_detector.detectAndDecode(image)
            
            if qr_data:
                print(f"QRコード検出: {qr_data}")
                return qr_data
            else:
                print("QRコードが検出されませんでした")
                return None
                
        except Exception as e:
            print(f"画像QRコード読み取りエラー: {str(e)}")
            return None
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        現在のフレームをキャプチャ
        
        Returns:
            フレーム画像（numpy配列）
        """
        try:
            if not self.camera or not self.is_running:
                return None
            
            ret, frame = self.camera.read()
            if ret:
                return frame
            return None
            
        except Exception as e:
            print(f"フレームキャプチャエラー: {str(e)}")
            return None
    
    def save_frame(self, file_path: str) -> bool:
        """
        現在のフレームを保存
        
        Args:
            file_path: 保存先ファイルパス
            
        Returns:
            保存成功の場合True
        """
        try:
            frame = self.capture_frame()
            if frame is not None:
                cv2.imwrite(file_path, frame)
                print(f"フレームを保存しました: {file_path}")
                return True
            return False
            
        except Exception as e:
            print(f"フレーム保存エラー: {str(e)}")
            return False
    
    def validate_qr_data(self, qr_data: str) -> bool:
        """
        QRコードデータの形式を検証
        
        Args:
            qr_data: QRコードのデータ
            
        Returns:
            有効な場合True
        """
        if qr_data is None:
            return False
        return qr_data.startswith("otpauth-migration://offline?data=")
    
    def get_camera_info(self) -> dict:
        """
        カメラ情報を取得
        
        Returns:
            カメラ情報の辞書
        """
        try:
            if not self.camera:
                return {}
            
            info = {
                'camera_index': self.camera_index,
                'is_opened': self.camera.isOpened(),
                'width': int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': self.camera.get(cv2.CAP_PROP_FPS),
                'is_running': self.is_running
            }
            return info
            
        except Exception as e:
            print(f"カメラ情報取得エラー: {str(e)}")
            return {}


def test_camera_qr_reader():
    """カメラQRリーダーのテスト"""
    reader = CameraQRReader()
    
    print("カメラQRリーダーテスト")
    print("-" * 40)
    
    # カメラ利用可能性チェック
    camera_available = reader.check_camera_available()
    print(f"カメラ利用可能: {camera_available}")
    
    if not camera_available:
        print("カメラが利用できないため、テストをスキップします")
        return
    
    # カメラ情報取得
    camera_info = reader.get_camera_info()
    print(f"カメラ情報: {camera_info}")
    
    # 利用可能なカメラリスト
    cameras = reader.get_camera_list()
    print(f"利用可能なカメラ: {cameras}")
    
    # QRコード検出のテスト（実際の使用時は適切なコールバックを設定）
    def on_qr_detected(data):
        print(f"QRコード検出: {data}")
        reader.stop_camera()
    
    def on_error(error):
        print(f"エラー: {error}")
        reader.stop_camera()
    
    print("QRコード検出を開始します（5秒間）...")
    reader.start_qr_detection(on_qr_detected, on_error)
    
    # 5秒間待機
    time.sleep(5)
    
    # カメラを停止
    reader.stop_camera()
    print("テスト完了")


if __name__ == "__main__":
    test_camera_qr_reader()
