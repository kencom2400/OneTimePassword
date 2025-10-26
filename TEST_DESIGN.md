# ワンタイムパスワードアプリケーション テスト設計書

## 1. 概要

### 1.1 目的
本テスト設計書は、ワンタイムパスワード生成アプリケーションの品質保証を目的として、包括的なテスト戦略とテストケースを定義する。

### 1.2 対象システム
- **アプリケーション名**: OneTimePassword
- **バージョン**: 1.0.0
- **主要機能**: Google Authenticatorと同様のOTP生成、QRコード読み取り、アカウント管理

### 1.3 テスト範囲
- 全モジュールの単体テスト
- モジュール間の統合テスト
- エンドツーエンドテスト
- パフォーマンステスト
- セキュリティテスト

## 2. テスト戦略

### 2.1 テストピラミッド
```
        E2E Tests (10%)
       ┌─────────────────┐
      │                 │
     ┌─────────────────────┐
    │   Integration Tests   │ (20%)
   │                       │
  ┌─────────────────────────────┐
 │        Unit Tests            │ (70%)
└─────────────────────────────────┘
```

### 2.2 テストカバレッジ目標
- **コードカバレッジ**: 90%以上
- **ブランチカバレッジ**: 85%以上
- **関数カバレッジ**: 95%以上
- **行カバレッジ**: 90%以上

### 2.3 テスト環境
- **開発環境**: ローカル開発マシン
- **CI/CD環境**: GitHub Actions
- **テストデータ**: モックデータとフィクスチャ

## 3. モジュール別テスト設計

### 3.1 crypto_utils.py

#### 3.1.1 テスト対象メソッド
- `generate_key(password: str, salt: bytes) -> bytes`
- `encrypt_data(data: str, password: str) -> Dict[str, str]`
- `decrypt_data(encrypted_data: Dict[str, str], password: str) -> str`

#### 3.1.2 テストケース

**正常系テスト**
- TC-CRYPTO-001: 正常な暗号化・復号化
- TC-CRYPTO-002: 空文字列の暗号化・復号化
- TC-CRYPTO-003: 特殊文字を含むデータの暗号化・復号化
- TC-CRYPTO-004: 長い文字列の暗号化・復号化
- TC-CRYPTO-005: 日本語文字の暗号化・復号化

**異常系テスト**
- TC-CRYPTO-006: 異なるパスワードでの復号化失敗
- TC-CRYPTO-007: 無効な暗号化データでの復号化失敗
- TC-CRYPTO-008: 破損した暗号化データでの復号化失敗
- TC-CRYPTO-009: 空のパスワードでの暗号化失敗
- TC-CRYPTO-010: None値での処理失敗

**境界値テスト**
- TC-CRYPTO-011: 最小長パスワード（1文字）
- TC-CRYPTO-012: 最大長パスワード（1000文字）
- TC-CRYPTO-013: 最小長データ（1文字）
- TC-CRYPTO-014: 最大長データ（10000文字）

### 3.2 otp_generator.py

#### 3.2.1 テスト対象メソッド
- `generate_totp(secret: str) -> str`
- `get_remaining_time() -> int`
- `start_realtime_display(accounts: List[Dict])`
- `stop_realtime_display()`

#### 3.2.2 テストケース

**正常系テスト**
- TC-OTP-001: 正常なTOTP生成
- TC-OTP-002: 複数アカウントのTOTP生成
- TC-OTP-003: 残り時間の正確な計算
- TC-OTP-004: リアルタイム表示の開始・停止
- TC-OTP-005: 30秒周期でのTOTP更新

**異常系テスト**
- TC-OTP-006: 無効なシークレットでのTOTP生成失敗
- TC-OTP-007: 空のシークレットでの処理失敗
- TC-OTP-008: 不正な形式のシークレットでの処理失敗
- TC-OTP-009: None値での処理失敗

**境界値テスト**
- TC-OTP-010: 最小長シークレット（16文字）
- TC-OTP-011: 最大長シークレット（128文字）
- TC-OTP-012: 時刻境界でのTOTP生成

### 3.3 security_manager.py

#### 3.3.1 テスト対象メソッド
- `add_account(device_name, account_name, issuer, secret) -> str`
- `get_account(account_id) -> Optional[Dict]`
- `list_accounts() -> List[Dict]`
- `update_account(account_id, **kwargs) -> bool`
- `delete_account(account_id) -> bool`
- `search_accounts(keyword) -> List[Dict]`
- `get_account_count() -> int`

#### 3.3.2 テストケース

**正常系テスト**
- TC-SEC-001: アカウントの追加
- TC-SEC-002: アカウントの取得
- TC-SEC-003: アカウント一覧の取得
- TC-SEC-004: アカウント情報の更新
- TC-SEC-005: アカウントの削除
- TC-SEC-006: アカウントの検索
- TC-SEC-007: アカウント数の取得
- TC-SEC-008: 複数アカウントの管理

**異常系テスト**
- TC-SEC-009: 存在しないアカウントIDでの取得失敗
- TC-SEC-010: 存在しないアカウントIDでの更新失敗
- TC-SEC-011: 存在しないアカウントIDでの削除失敗
- TC-SEC-012: 無効なアカウントIDでの処理失敗
- TC-SEC-013: 空のデータでの処理失敗
- TC-SEC-014: ファイルアクセス権限エラー

**境界値テスト**
- TC-SEC-015: 最大アカウント数（1000件）
- TC-SEC-016: 最小長アカウント名（1文字）
- TC-SEC-017: 最大長アカウント名（100文字）

### 3.4 camera_qr_reader.py

#### 3.4.1 テスト対象メソッド
- `check_camera_available() -> bool`
- `read_qr_from_image(image_path) -> Optional[str]`
- `validate_qr_data(qr_data) -> bool`
- `start_qr_detection(callback, error_callback)`
- `stop_camera()`

#### 3.4.2 テストケース

**正常系テスト**
- TC-CAM-001: カメラの利用可能性チェック
- TC-CAM-002: 画像ファイルからのQRコード読み取り
- TC-CAM-003: QRコードデータの検証
- TC-CAM-004: カメラの開始・停止
- TC-CAM-005: QRコード検出コールバック

**異常系テスト**
- TC-CAM-006: 存在しない画像ファイルでの読み取り失敗
- TC-CAM-007: 無効な画像形式での読み取り失敗
- TC-CAM-008: QRコードが含まれない画像での読み取り失敗
- TC-CAM-009: 無効なQRコードデータでの検証失敗
- TC-CAM-010: カメラアクセス権限エラー

**境界値テスト**
- TC-CAM-011: 最小サイズ画像（1x1ピクセル）
- TC-CAM-012: 最大サイズ画像（10000x10000ピクセル）
- TC-CAM-013: 最小QRコードサイズ

### 3.5 docker_manager.py

#### 3.5.1 テスト対象メソッド
- `check_docker_available() -> bool`
- `check_image_exists() -> bool`
- `setup_environment() -> bool`
- `process_qr_url(qr_data) -> Optional[Dict]`
- `parse_otpauth_output(output) -> Optional[Dict]`
- `delete_image() -> bool`

#### 3.5.2 テストケース

**正常系テスト**
- TC-DOCK-001: Dockerの利用可能性チェック
- TC-DOCK-002: イメージの存在確認
- TC-DOCK-003: 環境セットアップ
- TC-DOCK-004: QRコードURLの処理
- TC-DOCK-005: otpauth出力の解析
- TC-DOCK-006: イメージの削除

**異常系テスト**
- TC-DOCK-007: Docker未インストール環境での処理失敗
- TC-DOCK-008: Dockerサービス停止時の処理失敗
- TC-DOCK-009: 無効なQRコードURLでの処理失敗
- TC-DOCK-010: 解析失敗時の出力処理
- TC-DOCK-011: イメージ削除失敗

**境界値テスト**
- TC-DOCK-012: 最大長QRコードURL（10000文字）
- TC-DOCK-013: 最小長QRコードURL（10文字）

### 3.6 main.py

#### 3.6.1 テスト対象メソッド
- `OneTimePasswordApp`クラスの全メソッド
- CLI引数の解析
- コマンドの実行

#### 3.6.2 テストケース

**正常系テスト**
- TC-MAIN-001: add --cameraコマンドの実行
- TC-MAIN-002: add --imageコマンドの実行
- TC-MAIN-003: show --allコマンドの実行
- TC-MAIN-004: show <account_id>コマンドの実行
- TC-MAIN-005: listコマンドの実行
- TC-MAIN-006: deleteコマンドの実行
- TC-MAIN-007: updateコマンドの実行
- TC-MAIN-008: searchコマンドの実行
- TC-MAIN-009: setupコマンドの実行
- TC-MAIN-010: cleanupコマンドの実行
- TC-MAIN-011: statusコマンドの実行

**異常系テスト**
- TC-MAIN-012: 無効なコマンドでの処理失敗
- TC-MAIN-013: 必須引数不足での処理失敗
- TC-MAIN-014: 存在しないアカウントIDでの処理失敗
- TC-MAIN-015: 存在しない画像ファイルでの処理失敗

## 4. 統合テスト設計

### 4.1 モジュール間統合テスト

**TC-INT-001: アカウント追加フロー**
1. QRコード読み取り → Docker解析 → アカウント追加 → 暗号化保存

**TC-INT-002: OTP表示フロー**
1. アカウント取得 → 復号化 → TOTP生成 → 表示

**TC-INT-003: アカウント管理フロー**
1. アカウント一覧 → 検索 → 更新 → 削除

### 4.2 エンドツーエンドテスト

**TC-E2E-001: 完全なユーザーシナリオ**
1. 環境セットアップ
2. QRコード読み取りでアカウント追加
3. OTP表示
4. アカウント管理
5. クリーンアップ

## 5. パフォーマンステスト設計

### 5.1 負荷テスト
- TC-PERF-001: 大量アカウント（1000件）での処理性能
- TC-PERF-002: 同時OTP生成（100アカウント）の性能
- TC-PERF-003: メモリ使用量の測定

### 5.2 レスポンス時間テスト
- TC-PERF-004: TOTP生成時間（1秒以内）
- TC-PERF-005: アカウント検索時間（0.1秒以内）
- TC-PERF-006: QRコード読み取り時間（5秒以内）

## 6. セキュリティテスト設計

### 6.1 暗号化テスト
- TC-SEC-001: 暗号化強度の検証
- TC-SEC-002: パスワードハッシュ化の検証
- TC-SEC-003: ソルト生成のランダム性検証

### 6.2 データ保護テスト
- TC-SEC-004: メモリ上の機密データクリア
- TC-SEC-005: 一時ファイルの安全な削除
- TC-SEC-006: ログファイルへの機密情報漏洩防止

## 7. テストデータ設計

### 7.1 テスト用アカウントデータ
```json
{
  "test_accounts": [
    {
      "device_name": "TestDevice1",
      "account_name": "test@example.com",
      "issuer": "TestService",
      "secret": "JBSWY3DPEHPK3PXP"
    },
    {
      "device_name": "TestDevice2",
      "account_name": "user@test.com",
      "issuer": "TestApp",
      "secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
    }
  ]
}
```

### 7.2 テスト用QRコードデータ
- 有効なotpauth-migration URL
- 無効な形式のURL
- 破損したQRコードデータ

### 7.3 テスト用画像ファイル
- 有効なQRコード画像
- 無効な画像ファイル
- 破損した画像ファイル

## 8. テスト実行計画

### 8.1 実行順序
1. 単体テスト（各モジュール）
2. 統合テスト（モジュール間）
3. エンドツーエンドテスト
4. パフォーマンステスト
5. セキュリティテスト

### 8.2 実行環境
- **開発環境**: ローカル開発マシン
- **CI/CD環境**: GitHub Actions
- **テスト実行時間**: 全体で10分以内

### 8.3 品質ゲート
- コードカバレッジ90%以上
- 全テストケースの成功
- パフォーマンス要件の満足
- セキュリティ要件の満足

## 9. テストツールとフレームワーク

### 9.1 主要ツール
- **pytest**: テストフレームワーク
- **pytest-cov**: カバレッジ測定
- **pytest-mock**: モック機能
- **pytest-asyncio**: 非同期テスト

### 9.2 補助ツール
- **coverage**: カバレッジレポート
- **tox**: マルチ環境テスト
- **pre-commit**: コミット前テスト

## 10. テストメンテナンス

### 10.1 テストケース更新
- 機能追加時のテストケース追加
- バグ修正時のテストケース更新
- リファクタリング時のテストケース調整

### 10.2 テストデータ管理
- テストデータのバージョン管理
- 古いテストデータの削除
- 新しいテストデータの追加

## 11. リスクと対策

### 11.1 テストリスク
- **外部依存**: Docker、カメラなどの外部リソース
- **環境依存**: OS、Pythonバージョンによる動作差異
- **時間依存**: TOTPの時刻依存性

### 11.2 対策
- **モック化**: 外部依存のモック化
- **CI/CD**: 複数環境での自動テスト
- **時刻固定**: テスト時の時刻固定

## 12. 成功基準

### 12.1 品質基準
- コードカバレッジ90%以上
- 全テストケースの成功
- パフォーマンス要件の満足
- セキュリティ要件の満足

### 12.2 完了基準
- 全テストケースの実装完了
- テスト実行の自動化完了
- テストレポートの生成完了
- ドキュメントの整備完了

## 13. テスト実装ガイド

### 13.1 テストファイル構造
```
tests/
├── conftest.py              # 共通フィクスチャ
├── unit/                    # 単体テスト
│   ├── test_crypto_utils.py
│   ├── test_otp_generator.py
│   ├── test_security_manager.py
│   ├── test_camera_qr_reader.py
│   ├── test_docker_manager.py
│   └── test_main.py
├── integration/             # 統合テスト
│   ├── test_account_flow.py
│   ├── test_otp_display.py
│   └── test_docker_integration.py
├── e2e/                     # エンドツーエンドテスト
│   └── test_user_scenarios.py
├── fixtures/                # テストフィクスチャ
│   ├── test_accounts.json
│   ├── test_qr_data.txt
│   └── test_images/
└── data/                    # テストデータ
    └── sample_accounts.json
```

### 13.2 テスト命名規則
- テストファイル: `test_<module_name>.py`
- テストクラス: `Test<ClassName>`
- テストメソッド: `test_<functionality>_<scenario>`

### 13.3 テスト実行コマンド
```bash
# 全テスト実行
pytest

# カバレッジ付き実行
pytest --cov=src --cov-report=html

# 特定のテスト実行
pytest tests/unit/test_crypto_utils.py

# マーカー指定実行
pytest -m unit
pytest -m integration
pytest -m e2e
```

## 14. 継続的改善

### 14.1 テストメトリクス
- テストカバレッジの推移
- テスト実行時間の推移
- バグ検出率の推移

### 14.2 テスト品質向上
- テストケースの見直し
- テストデータの最適化
- テスト実行の高速化

---

**作成日**: 2025年1月26日  
**バージョン**: 1.0  
**作成者**: OneTimePassword Team
