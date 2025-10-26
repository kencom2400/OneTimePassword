# ワンタイムパスワード生成アプリケーション

Google Authenticatorと同様の機能を持つワンタイムパスワード（OTP）生成アプリケーションです。PCカメラを使用してQRコードを読み取り、複数のアカウントのOTPを同時に管理・表示できます。

**[English version is available here (英語版はこちら)](README.en.md)**

## 📑 目次

- [🚀 主な機能](#-主な機能)
- [📖 使用方法](#-使用方法)
- [🛠️ セットアップ](#️-セットアップ)
- [📋 要件](#-要件)
- [🔒 セキュリティ](#-セキュリティ)
- [🐛 トラブルシューティング](#-トラブルシューティング)
- [📝 ライセンス](#-ライセンス)
- [📞 サポート](#-サポート)
- [🔧 開発者向け情報](#-開発者向け情報)
- [🧪 テスト](#-テスト) ⭐ **テスト設計書付き**
- [🤝 貢献](#-貢献)

## 🚀 主な機能

- **QRコード読み取り**: PCカメラまたは画像ファイルからQRコードを読み取り
- **複数アカウント管理**: 複数のアカウントのOTPを同時に管理・表示
- **リアルタイム表示**: 1秒間隔でOTPを自動更新（プログレスバー付き）
- **セキュアな保存**: セキュリティコードはPBKDF2で暗号化してローカル保存
- **コマンドライン操作**: 直感的なコマンドラインインターフェース
- **Docker連携**: otpauthコンテナを使用したQRコード解析
- **アカウント管理**: 一覧、検索、更新、削除機能

## 📖 使用方法

### Poetry環境での実行

```bash
# Poetry仮想環境内で実行
poetry run python src/main.py [コマンド]

# または仮想環境をアクティベートしてから実行
poetry shell
python src/main.py [コマンド]
```

### コマンド一覧

#### アカウントの追加

```bash
# カメラでQRコード読み取り
poetry run python src/main.py add --camera

# 画像ファイルからQRコード読み取り
poetry run python src/main.py add --image qr_code.png
```

#### OTPの表示

```bash
# 全アカウントのOTP表示（リアルタイム更新）
poetry run python src/main.py show --all

# 特定アカウントのOTP表示
poetry run python src/main.py show <account_id>
```

#### アカウント管理

```bash
# アカウント一覧表示
poetry run python src/main.py list

# アカウント削除
poetry run python src/main.py delete <account_id>

# アカウント情報更新
poetry run python src/main.py update <account_id> --name "新しい名前"

# アカウント検索
poetry run python src/main.py search "キーワード"
```

#### システム管理

```bash
# アプリケーション状態表示
poetry run python src/main.py status

# Docker環境のセットアップ
poetry run python src/main.py setup

# Dockerイメージの削除
poetry run python src/main.py cleanup
```

## 🛠️ セットアップ

### 1. Poetry環境のセットアップ

```bash
# Poetryがインストールされていない場合
curl -sSL https://install.python-poetry.org | python3 -

# PATH設定（~/.zshrcに追加）
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# プロジェクトディレクトリに移動
cd /path/to/OneTimePassword

# 依存関係のインストール
poetry install
```

### 2. システム依存関係のインストール（macOS）

```bash
# zbarライブラリ（QRコード読み取り用）
brew install zbar
```

### 3. Docker環境のセットアップ

```bash
# Docker環境のセットアップ（otpauthリポジトリのクローンとイメージビルド）
poetry run python src/main.py setup

# セットアップ完了の確認
docker images | grep otpauth
# 出力例: otpauth      latest    eeb083890349   9 minutes ago   21.1MB
```

**注意**: QRコードの読み取り機能は、イメージが存在しない場合に自動的にビルドを試行します。初回使用時は時間がかかる場合があります。

### 4. 環境テスト

```bash
# アプリケーションの動作確認
poetry run python src/main.py --help

# ステータス確認
poetry run python src/main.py status
```

## 📋 要件

- **Python**: 3.8.1以上（推奨: 3.13.9）
- **Poetry**: 依存関係管理
- **Docker**: QRコード解析用
- **macOS**: カメラアクセス権限
- **システムライブラリ**: zbar（QRコード読み取り用）

## 🔒 セキュリティ

- **暗号化**: セキュリティコードはPBKDF2で暗号化して保存
- **ランダムソルト**: 各暗号化ごとに16バイトのランダムなソルトを生成（レインボーテーブル攻撃対策）
- **ローカル保存**: 機密データはGitHubにコミットされません
- **メモリクリア**: 使用後の機密データは即座にクリア
- **権限管理**: 適切なファイル権限設定
- **カメラアクセス**: 最小限の権限でカメラにアクセス
- **環境変数**: マスターパスワードは環境変数で安全に管理

### 🔐 暗号化の仕組み

本アプリケーションは業界標準のセキュリティプラクティスを採用しています：

1. **各暗号化ごとに一意のソルト**: 同じデータを暗号化しても、毎回異なる結果が生成されます
2. **PBKDF2キー導出**: 100,000回の反復でマスターパスワードから暗号化キーを導出
3. **Fernet暗号化**: AES-128-CBCとHMAC-SHA256による認証付き暗号化
4. **ソルトの保存**: 16バイトのランダムソルトを暗号化データと一緒に保存

### 🔐 マスターパスワードの設定（重要）

アプリケーションはセキュリティコードを暗号化するためにマスターパスワードを使用します。
以下のいずれかの方法でマスターパスワードを設定してください：

#### 方法1: 環境変数で設定（推奨）

```bash
# ~/.zshrc または ~/.bashrc に追加
export OTP_MASTER_PASSWORD="your_strong_password_here"

# 設定を反映
source ~/.zshrc
```

#### 方法2: パスワードファイルで設定（より安全・推奨）

**デフォルトファイル `~/.otp_password` を使用（環境変数不要）:**

```bash
# パスワードファイルを作成（権限を制限）
echo "your_strong_password_here" > ~/.otp_password
chmod 600 ~/.otp_password

# これだけで完了！環境変数の設定は不要です
poetry run python src/main.py show --all
```

**カスタムパスワードファイルを使用する場合:**

```bash
# 任意の場所にパスワードファイルを作成
echo "your_strong_password_here" > /path/to/custom_password
chmod 600 /path/to/custom_password

# ~/.zshrc または ~/.bashrc に追加
export OTP_PASSWORD_FILE="/path/to/custom_password"

# 設定を反映
source ~/.zshrc
```

#### 方法3: インタラクティブ入力

環境変数もパスワードファイルも設定していない場合、アプリケーション起動時にパスワードの入力を求められます。

#### オプション: カスタムソルトの設定

デフォルトのソルトをカスタマイズする場合：

```bash
# ~/.zshrc または ~/.bashrc に追加
export OTP_SALT="your_custom_salt_value"
```

**⚠️ セキュリティ警告**:
- マスターパスワードは推測しにくい強力なものを使用してください
- パスワードファイルを使用する場合は、必ず適切なファイル権限（600）を設定してください
- 環境変数やパスワードファイルをバージョン管理システムにコミットしないでください
- パスワードを変更すると、既存のデータが復号化できなくなる可能性があります

## 🐛 トラブルシューティング

### カメラが認識されない場合

```bash
# カメラの接続確認
poetry run python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# カメラ権限の確認（macOS）
# システム環境設定 > セキュリティとプライバシー > プライバシー > カメラ
```

### Dockerエラーの場合

```bash
# Dockerの状態確認
docker --version
docker info

# Dockerデーモンの起動確認
docker ps

# ネットワーク接続確認
ping github.com

# otpauthイメージが存在しない場合（自動ビルドされる）
poetry run python src/main.py add --camera

# 手動でセットアップする場合
poetry run python src/main.py setup

# イメージの確認
docker images | grep otpauth

# イメージを削除する場合
poetry run python src/main.py cleanup
```

### QRコードが読み取れない場合

- QRコードが鮮明で十分なサイズか確認
- カメラの焦点を調整
- 照明条件を改善
- QRコードの形式確認（`otpauth-migration://offline?data=...`）

### QRコード解析エラーの場合

```bash
# 解析エラーのデバッグ
poetry run python -c "
from src.docker_manager import DockerManager
dm = DockerManager()
# テスト用の出力で解析を確認
test_output = 'otpauth://totp/account?algorithm=SHA1&digits=6&issuer=GitHub&period=30&secret=SECRET'
result = dm.parse_otpauth_output(test_output)
print('解析結果:', result)
"
```

### Poetry環境の問題

```bash
# 仮想環境の再作成
poetry env remove python
poetry install

# 依存関係の更新
poetry update

# ロックファイルの再生成
poetry lock
```

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 📞 サポート

問題が発生した場合は、以下の手順でサポートを受けてください：

1. [トラブルシューティング](#-トラブルシューティング)セクションを確認
2. 既存のIssueを検索
3. 新しいIssueを作成（詳細な情報を含める）

---

## 🔧 開発者向け情報

### プロジェクト構成

```
OneTimePassword/
├── src/                          # ソースコード
│   ├── __init__.py              # パッケージ初期化
│   ├── main.py                  # メインアプリケーション（CLI）
│   ├── camera_qr_reader.py      # カメラQRコード読み取り
│   ├── otp_generator.py         # OTP生成・表示
│   ├── security_manager.py      # セキュリティコード管理
│   ├── crypto_utils.py          # 暗号化ユーティリティ
│   └── docker_manager.py        # Dockerコンテナ管理
├── tests/                        # テストコード
│   ├── TEST_DESIGN.md           # テスト設計書
│   ├── conftest.py              # pytest共通フィクスチャ
│   ├── unit/                    # 単体テスト（163個）
│   │   ├── test_crypto_utils.py
│   │   ├── test_otp_generator.py
│   │   ├── test_security_manager.py
│   │   ├── test_camera_qr_reader.py
│   │   ├── test_docker_manager.py
│   │   └── test_main.py
│   ├── integration/             # 統合テスト（10個）
│   │   └── test_integration.py
│   ├── run_tests.py             # Pythonテスト実行スクリプト
│   └── run_tests.sh             # Bashラッパースクリプト
├── data/                         # データディレクトリ
│   └── accounts.json            # アカウントデータ（暗号化）
├── htmlcov/                      # カバレッジHTMLレポート（自動生成）
├── pyproject.toml               # Poetry設定ファイル
├── poetry.lock                  # Poetry依存関係ロックファイル
├── requirements.txt             # 従来の依存関係（参考用）
├── .gitignore                   # Git除外設定
├── LICENSE                      # ライセンスファイル
├── README.md                    # このファイル
├── REQUIREMENTS_OVERVIEW.md     # プロジェクト要件概要
└── requirements_specification.md # 要件定義書
```

### 技術仕様

#### 使用技術

- **言語**: Python 3.8.1+
- **依存関係管理**: Poetry
- **仮想環境**: pyenv + Poetry
- **暗号化**: cryptography（PBKDF2）
- **QRコード**: OpenCV（cv2.QRCodeDetector）
- **OTP生成**: pyotp
- **コンテナ**: Docker
- **画像処理**: Pillow

#### 依存関係

```toml
[tool.poetry.dependencies]
python = "^3.8.1"
pyotp = "^2.9.0"
opencv-python = "^4.8.1"
cryptography = "^41.0.7"
Pillow = "^10.0.1"
docker = "^6.1.3"
numpy = "^1.24.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-cov = "^4.0.0"
pytest-mock = "^3.0.0"
pytest-asyncio = "^0.21.0"
black = "^23.0.0"
flake8 = "^6.0.0"
mypy = "^1.0.0"
```

### 開発環境情報

- **Python**: 3.13.9（pyenv管理）
- **Poetry**: 2.2.1
- **仮想環境**: `/Users/kencom/Library/Caches/pypoetry/virtualenvs/onetimepassword-78G70__u-py3.13`
- **OS**: macOS Sequoia 24.6.0

## 🧪 テスト

### 📚 テスト設計書

詳細なテスト設計については、[テスト設計書（TEST_DESIGN.md）](tests/TEST_DESIGN.md)を参照してください。

テスト設計書には以下の情報が含まれています：
- テスト戦略とテストピラミッド
- モジュール別テスト設計（173個のテストケース）
- 統合テスト・E2Eテスト設計
- モック化のベストプラクティス
- トラブルシューティングガイド
- テスト実行方法の詳細

### 📊 テスト統計

- **総テスト数**: 173個
  - 単体テスト: 163個
  - 統合テスト: 10個
- **テスト成功率**: 100% ✅
- **実行時間**: 約2.8秒
- **現在のカバレッジ**: 67%
- **目標カバレッジ**: 90%以上

### 🚀 テスト実行方法

#### 1. ラッパーシェルスクリプト（推奨）

```bash
# 全テスト実行（推奨）
./run_tests.sh

# 単体テストのみ実行
./run_tests.sh unit

# 統合テストのみ実行
./run_tests.sh integration

# カバレッジ付きテスト実行（HTML・XMLレポート生成）
./run_tests.sh coverage --html

# クイックテスト実行（カバレッジなし）
./run_tests.sh quick

# 監視モード（ファイル変更時に自動実行）
./run_tests.sh watch

# テストキャッシュクリア
./run_tests.sh clean

# ヘルプ表示
./run_tests.sh --help
```

#### 2. 直接実行

```bash
# 全テスト実行
poetry run pytest tests/ -v

# カバレッジ付きテスト実行
poetry run pytest tests/ --cov=src --cov-report=html --cov-report=term

# 特定のモジュールのテスト実行
poetry run pytest tests/unit/test_crypto_utils.py -v

# 特定のテストクラス実行
poetry run pytest tests/unit/test_main.py::TestOneTimePasswordApp -v

# 特定のテスト関数実行
poetry run pytest tests/unit/test_main.py::TestOneTimePasswordApp::test_add_account_from_camera_success -v

# 並列実行（高速化）
poetry run pytest tests/ -n auto

# タイムアウト付き実行（ハングするテスト対策）
timeout 120 poetry run pytest tests/ -v
```

### 🗂️ テスト構造

```
tests/
├── TEST_DESIGN.md           # テスト設計書（詳細なドキュメント）
├── conftest.py              # pytest共通フィクスチャ
├── unit/                    # 単体テスト（163個）
│   ├── test_crypto_utils.py      # 暗号化ユーティリティ（25個）
│   ├── test_otp_generator.py     # OTP生成（19個）
│   ├── test_security_manager.py  # セキュリティ管理（23個）
│   ├── test_camera_qr_reader.py  # カメラQR読み取り（30個）
│   ├── test_docker_manager.py    # Docker管理（32個）
│   └── test_main.py              # メインアプリ（34個）
├── integration/             # 統合テスト（10個）
│   └── test_integration.py
├── run_tests.py             # Pythonテスト実行スクリプト
└── run_tests.sh             # Bashラッパースクリプト
```

### 📋 テスト実行オプション

#### ラッパーシェルオプション

- `-v, --verbose`: 詳細出力（テストケース名と結果を表示）
- `-q, --quiet`: 簡潔出力（サマリーのみ表示）
- `-f, --fail-fast`: 最初の失敗で停止
- `-p, --parallel`: 並列実行（高速化）
- `--no-cov`: カバレッジ測定を無効化（高速実行）
- `--html`: HTMLカバレッジレポート生成（`htmlcov/index.html`）
- `--xml`: XMLカバレッジレポート生成（`coverage.xml`）
- `-m MARKER`: 特定のマーカーのテストのみ実行

#### pytestオプション例

```bash
# 失敗したテストのみ再実行
poetry run pytest tests/ --lf

# 失敗したテストを最初に実行
poetry run pytest tests/ --ff

# トレースバックを短く表示
poetry run pytest tests/ --tb=short

# トレースバックを表示しない
poetry run pytest tests/ --tb=no

# 詳細な出力（各テストの詳細）
poetry run pytest tests/ -vv

# テストの実行時間を表示
poetry run pytest tests/ --durations=10
```

### 🔍 カバレッジレポート

テスト実行後、以下のカバレッジレポートが生成されます：

```bash
# HTMLレポートの確認
open htmlcov/index.html

# ターミナルでのカバレッジ表示
poetry run pytest tests/ --cov=src --cov-report=term-missing
```

**現在のカバレッジ詳細**:
- `src/main.py`: 84%
- `src/crypto_utils.py`: 80%
- `src/docker_manager.py`: 73%
- `src/security_manager.py`: 67%
- `src/camera_qr_reader.py`: 52%
- `src/otp_generator.py`: 37%

### 🐛 テストのトラブルシューティング

#### テストがハングする場合

```bash
# タイムアウトを設定して実行
timeout 120 poetry run pytest tests/ -v

# 特定のテストをスキップ
poetry run pytest tests/ -k "not test_hanging_test"
```

#### カメラアクセスエラー

全てのカメラテストは完全にモック化されているため、実際のカメラは不要です。
エラーが発生する場合は、[テスト設計書のトラブルシューティング](tests/TEST_DESIGN.md#13-トラブルシューティング)を参照してください。

#### Docker関連エラー

Docker環境が不要なため、Dockerが起動していなくてもテストは成功します。
全てのDockerコマンドは`subprocess.run`でモック化されています。

### 📝 テストの書き方

新しいテストを追加する際は、以下のガイドラインに従ってください：

1. **適切なモック化**: 外部依存は必ずモック化
2. **明確なテスト名**: `test_<method>_<scenario>`の形式
3. **AAA パターン**: Arrange（準備）、Act（実行）、Assert（検証）
4. **独立性**: 各テストは独立して実行可能に
5. **ドキュメント**: docstringでテストケースIDと目的を記載

例：
```python
def test_add_account_success(self, security_manager):
    """TC-SEC-001: アカウントの追加（成功）"""
    # Arrange
    account_data = {...}
    
    # Act
    result = security_manager.add_account(**account_data)
    
    # Assert
    assert result is not None
    assert len(result) > 0
```

詳細は[テスト設計書](tests/TEST_DESIGN.md)を参照してください。

### 開発コマンド

```bash
# コードフォーマット
poetry run black src/

# リント
poetry run flake8 src/

# 型チェック
poetry run mypy src/

# テスト実行
poetry run pytest
```

### 前提条件の確認（開発者向け）

```bash
# Python 3.13.9の確認
python --version

# pyenvの確認
pyenv versions

# Dockerの確認
docker --version

# 仮想環境の確認
poetry env info
```

## 🤝 貢献

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

---

**注意**: このアプリケーションは教育・研究目的で作成されています。本番環境での使用前に十分なテストを行ってください。