# ワンタイムパスワード生成アプリケーション

Google Authenticatorと同様の機能を持つワンタイムパスワード（OTP）生成アプリケーションです。PCカメラを使用してQRコードを読み取り、複数のアカウントのOTPを同時に管理・表示できます。

**[English version is available here (英語版はこちら)](README.en.md)**

## 📑 目次

### 👤 ユーザー向け（アプリを使う）
- [🚀 クイックスタート](#-クイックスタート)
- [📖 基本的な使い方](#-基本的な使い方)
- [📋 コマンドリファレンス](#-コマンドリファレンス)
- [🔒 セキュリティ設定](#-セキュリティ設定)
- [🐛 トラブルシューティング](#-トラブルシューティング)

### 👨‍💻 開発者向け（アプリを開発する）
- [🛠️ 開発環境セットアップ](#️-開発環境セットアップ)
- [📂 プロジェクト構成](#-プロジェクト構成)
- [🔧 開発ツールとコマンド](#-開発ツールとコマンド)
- [🧪 テスト実行とカバレッジ](#-テスト実行とカバレッジ)
- [📚 開発者ドキュメント](#-開発者ドキュメント)

### 📚 その他
- [🚀 主な機能](#-主な機能)
- [📋 システム要件](#-システム要件)

---

## 👤 ユーザー向け（アプリを使う）

このセクションは、OneTimePasswordアプリケーションを**使用したい方**向けです。

### 🚀 クイックスタート

**最もシンプルな始め方：** ラッパーシェルを使用

```bash
# 1. リポジトリをクローン
git clone https://github.com/your-username/OneTimePassword.git
cd OneTimePassword

# 2. Poetryをインストール（未インストールの場合のみ）
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"

# 3. すぐに実行！（初回は自動で依存関係をインストール）
./otp --help

# 4. マスターパスワードを設定（初回のみ）
echo "your_strong_password" > ~/.otp_password
chmod 600 ~/.otp_password

# 完了！これだけです 🎉
```

**次のステップ：**
- [基本的な使い方](#-基本的な使い方) - アカウント追加とOTP表示
- [セキュリティ設定](#-セキュリティ設定) - マスターパスワードの詳細設定

### 📖 基本的な使い方

#### 1. アカウントを追加する

```bash
# カメラでQRコードを読み取って追加
./otp add --camera

# または画像ファイルから追加
./otp add --image qr_code.png
```

#### 2. OTPを表示する

```bash
# 全アカウントのOTPを表示（リアルタイム更新）
./otp show --all

# 特定のアカウントのみ表示
./otp show <account_id>
```

#### 3. アカウントを管理する

```bash
# アカウント一覧を表示
./otp list

# アカウントを検索
./otp search "GitHub"

# アカウント情報を更新
./otp update <account_id> --name "新しい名前"

# アカウントを削除
./otp delete <account_id>
```

#### 4. システム状態を確認する

```bash
# アプリケーションの状態を確認
./otp status

# Docker環境をセットアップ（初回のみ）
./otp setup

# Dockerイメージをクリーンアップ
./otp cleanup
```

### 📋 コマンドリファレンス

#### 実行方法の選択

このアプリケーションには3つの実行方法があります：

| 方法 | コマンド例 | 推奨度 | 用途 |
|------|-----------|--------|------|
| **ラッパーシェル** | `./otp show --all` | ⭐⭐⭐ | 日常使用（最も簡単） |
| **Poetry直接** | `poetry run python src/main.py show --all` | ⭐⭐ | 開発・デバッグ時 |
| **Docker** | `docker-compose -f docker/docker-compose.yml run --rm app ...` | ⭐ | テスト実行 |

以降のコマンド例は、**ラッパーシェル形式**で記載します。他の方法で実行する場合は、上記の表を参考に読み替えてください。

#### コマンド一覧

**アカウント管理**

```bash
./otp add --camera              # カメラでQRコード読み取り
./otp add --image <path>        # 画像ファイルから読み取り
./otp list                      # アカウント一覧
./otp show --all                # 全OTP表示（リアルタイム更新）
./otp show <account_id>         # 特定アカウントのOTP表示
./otp search <keyword>          # アカウント検索
./otp update <id> --name <name> # アカウント更新
./otp delete <account_id>       # アカウント削除
```

**システム管理**

```bash
./otp status                    # ステータス表示
./otp setup                     # Docker環境セットアップ
./otp cleanup                   # Dockerイメージ削除
./otp --help                    # ヘルプ表示
```

### 🔒 セキュリティ設定

#### マスターパスワードについて

このアプリケーションは、セキュリティコードを暗号化して保存するためにマスターパスワードを使用します。

**暗号化の仕組み：**
- PBKDF2キー導出（100,000回の反復）
- Fernet暗号化（AES-128-CBC + HMAC-SHA256）
- 各暗号化ごとに一意の16バイトランダムソルト
- ローカルストレージのみ（GitHubにコミットされません）

#### マスターパスワードの設定方法

**方法1: パスワードファイル（推奨・最も簡単）**

```bash
# デフォルトファイルに保存（環境変数不要）
echo "your_strong_password" > ~/.otp_password
chmod 600 ~/.otp_password

# これだけで完了！
./otp show --all
```

**方法2: カスタムパスワードファイル**

```bash
# 任意の場所に保存
echo "your_strong_password" > /path/to/password
chmod 600 /path/to/password

# 環境変数で場所を指定（~/.zshrcに追加）
echo 'export OTP_PASSWORD_FILE="/path/to/password"' >> ~/.zshrc
source ~/.zshrc
```

**方法3: 環境変数**

```bash
# ~/.zshrcに追加
echo 'export OTP_MASTER_PASSWORD="your_strong_password"' >> ~/.zshrc
source ~/.zshrc
```

**方法4: インタラクティブ入力**

上記の設定をしていない場合、実行時にパスワードの入力を求められます。

**⚠️ セキュリティ警告：**
- 推測しにくい強力なパスワードを使用してください
- パスワードファイルは必ず権限600に設定してください
- パスワードをバージョン管理システムにコミットしないでください
- パスワードを変更すると既存データが復号化できなくなります

### 🐛 トラブルシューティング

#### カメラが認識されない

```bash
# カメラの接続確認
poetry run python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# macOSの場合：システム環境設定でカメラ権限を確認
# システム環境設定 > セキュリティとプライバシー > プライバシー > カメラ
```

#### Dockerエラー

```bash
# Dockerの状態確認
docker --version
docker ps

# otpauthイメージの確認
docker images | grep otpauth

# イメージが無い場合は自動ビルドされます
./otp add --camera

# 手動でセットアップ
./otp setup
```

#### QRコードが読み取れない

- QRコードが鮮明で十分なサイズか確認
- カメラの焦点を調整
- 照明条件を改善
- QRコードの形式を確認（`otpauth-migration://offline?data=...`）

#### Poetry環境の問題

```bash
# 仮想環境の再作成
poetry env remove python
poetry install

# 依存関係の更新
poetry update
```

---

## 👨‍💻 開発者向け（アプリを開発する）

このセクションは、OneTimePasswordアプリケーションの**開発に参加したい方**向けです。

### 🛠️ 開発環境セットアップ

#### 必要なツール

- **Python 3.13以上**（推奨: 3.13.9）
- **Poetry**（依存関係管理）
- **Docker**（QRコード解析、テスト実行）
- **Git**（バージョン管理）
- **zbar**（QRコード読み取りライブラリ）

#### セットアップ手順

```bash
# 1. リポジトリをクローン
git clone https://github.com/your-username/OneTimePassword.git
cd OneTimePassword

# 2. Poetryをインストール
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"

# 3. 依存関係をインストール
poetry install

# 4. システムライブラリをインストール（macOS）
brew install zbar

# 5. Docker環境をセットアップ
poetry run python src/main.py setup

# 6. 動作確認
poetry run python src/main.py --help
```

#### 開発環境の確認

```bash
# Python バージョン確認
python --version  # 3.13以上

# Poetry 確認
poetry --version

# 仮想環境の確認
poetry env info

# Docker 確認
docker --version
docker ps
```

### 📂 プロジェクト構成

```
OneTimePassword/
├── 🚀 実行ファイル
│   ├── otp                       # ラッパーシェル（ユーザー用）
│   └── run_tests.sh              # テスト実行スクリプト
│
├── 📁 ソースコード
│   └── src/
│       ├── main.py               # メインアプリケーション（CLI）
│       ├── camera_qr_reader.py   # カメラQRコード読み取り
│       ├── otp_generator.py      # OTP生成・表示
│       ├── security_manager.py   # アカウント管理・暗号化
│       ├── crypto_utils.py       # 暗号化ユーティリティ
│       └── docker_manager.py     # Dockerコンテナ管理
│
├── 🧪 テストコード
│   └── tests/
│       ├── unit/                 # 単体テスト（163個）
│       ├── integration/          # 統合テスト（10個）
│       └── conftest.py           # pytest設定
│
├── 📚 ドキュメント
│   ├── README.md                 # このファイル（ユーザー向け）
│   ├── README.en.md              # 英語版
│   └── docs/
│       ├── README.md             # 開発者ドキュメント概要
│       ├── REQUIREMENTS_OVERVIEW.md
│       ├── REQUIREMENTS_SPECIFICATION.md
│       └── TEST_DESIGN.md        # テスト設計書
│
├── 🐳 Docker関連
│   └── docker/
│       ├── docker-compose.yml    # Docker Compose設定
│       ├── Dockerfile            # アプリケーション用
│       ├── Dockerfile.test       # テスト用
│       └── Dockerfile.lint       # Lint用
│
└── ⚙️ 設定ファイル
    ├── pyproject.toml            # Poetry設定
    ├── poetry.lock               # 依存関係ロック
    └── .gitignore                # Git除外設定
```

### 🔧 開発ツールとコマンド

#### コード品質チェック

```bash
# コードフォーマット（Black）
poetry run black src/ tests/

# フォーマットチェック（変更なし）
poetry run black --check --diff src/ tests/

# Lintチェック（Flake8）
poetry run flake8 src/ tests/ --count --statistics

# 型チェック（MyPy）
poetry run mypy src/ --ignore-missing-imports --show-error-codes
```

#### 一括実行（Docker使用）

```bash
# 全Lintチェック
docker-compose -f docker/docker-compose.yml run --rm black
docker-compose -f docker/docker-compose.yml run --rm flake8
docker-compose -f docker/docker-compose.yml run --rm mypy

# フォーマット適用
docker-compose -f docker/docker-compose.yml run --rm format
```

#### デバッグ実行

```bash
# Pythonデバッガー付き実行
poetry run python -m pdb src/main.py [コマンド]

# 詳細ログ出力
poetry run python src/main.py --verbose [コマンド]

# 環境情報の表示
poetry run python src/main.py status
```

#### 依存関係の管理

```bash
# 依存関係の追加
poetry add <package>

# 開発用依存関係の追加
poetry add --group dev <package>

# 依存関係の更新
poetry update

# 依存関係の確認
poetry show --tree
```

### 🧪 テスト実行とカバレッジ

#### テスト実行方法

**クイック実行（推奨）**

```bash
# 全テスト実行（最も簡単）
./run_tests.sh

# カバレッジ付き実行
./run_tests.sh coverage --html

# 単体テストのみ
./run_tests.sh unit

# 統合テストのみ
./run_tests.sh integration

# クイック実行（カバレッジなし）
./run_tests.sh quick

# テストキャッシュクリア
./run_tests.sh clean

# ヘルプ表示
./run_tests.sh --help
```

**詳細な実行オプション**

```bash
# 全テスト実行
poetry run pytest tests/ -v

# カバレッジ付き実行
poetry run pytest tests/ --cov=src --cov-report=html --cov-report=term

# 特定のモジュールのテスト
poetry run pytest tests/unit/test_crypto_utils.py -v

# 特定のテストクラス
poetry run pytest tests/unit/test_main.py::TestOneTimePasswordApp -v

# 特定のテスト関数
poetry run pytest tests/unit/test_main.py::test_add_account_success -v

# 並列実行（高速化）
poetry run pytest tests/ -n auto

# 失敗したテストのみ再実行
poetry run pytest tests/ --lf

# 詳細出力
poetry run pytest tests/ -vv

# テスト実行時間の表示
poetry run pytest tests/ --durations=10
```

**Docker環境でのテスト実行**

```bash
# 全テスト
docker-compose -f docker/docker-compose.yml run --rm test

# 単体テストのみ
docker-compose -f docker/docker-compose.yml run --rm test-unit

# 統合テストのみ
docker-compose -f docker/docker-compose.yml run --rm test-integration
```

#### テスト統計とカバレッジ

**現在のテスト統計**

- **総テスト数**: 173個
  - 単体テスト: 163個
  - 統合テスト: 10個
- **テスト成功率**: 100% ✅
- **実行時間**: 約2.8秒
- **現在のカバレッジ**: 67%
- **目標カバレッジ**: 90%

**モジュール別カバレッジ**

| モジュール | カバレッジ | テスト数 |
|-----------|----------|----------|
| `main.py` | 84% | 34個 |
| `crypto_utils.py` | 80% | 25個 |
| `docker_manager.py` | 73% | 32個 |
| `security_manager.py` | 67% | 23個 |
| `camera_qr_reader.py` | 52% | 30個 |
| `otp_generator.py` | 37% | 19個 |

**カバレッジレポートの確認**

```bash
# HTMLレポートを生成して表示
poetry run pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# ターミナルで詳細表示
poetry run pytest tests/ --cov=src --cov-report=term-missing
```

#### テストの書き方

新しいテストを追加する際は、以下のガイドラインに従ってください：

**1. 命名規則**
- ファイル名: `test_<module_name>.py`
- クラス名: `Test<ClassName>`
- メソッド名: `test_<functionality>_<scenario>`

**2. AAAパターン**
```python
def test_add_account_success(self, security_manager):
    """TC-SEC-001: アカウントの追加（成功）"""
    # Arrange（準備）
    account_data = {
        "account_id": "test_001",
        "account_name": "TestAccount",
        "issuer": "TestIssuer",
        "secret": "JBSWY3DPEHPK3PXP"
    }
    
    # Act（実行）
    result = security_manager.add_account(**account_data)
    
    # Assert（検証）
    assert result is not None
    assert len(result) > 0
```

**3. モック化のベストプラクティス**

```python
from unittest.mock import Mock, patch

# 外部依存のモック化
@patch('cv2.VideoCapture')
def test_camera_access(mock_camera):
    mock_camera.return_value.isOpened.return_value = True
    # テストコード
```

**4. テストの独立性**
- 各テストは独立して実行可能にする
- テスト間で状態を共有しない
- フィクスチャで初期化する

**5. ドキュメント**
- docstringでテストケースIDと目的を記載
- 複雑なテストにはコメントを追加

**テスト構造**

```
tests/
├── conftest.py              # 共通フィクスチャ
├── unit/                    # 単体テスト
│   ├── test_crypto_utils.py      # 暗号化（25個）
│   ├── test_otp_generator.py     # OTP生成（19個）
│   ├── test_security_manager.py  # セキュリティ（23個）
│   ├── test_camera_qr_reader.py  # カメラQR（30個）
│   ├── test_docker_manager.py    # Docker（32個）
│   └── test_main.py              # メイン（34個）
└── integration/             # 統合テスト
    └── test_integration.py       # 統合（10個）
```

**テスト実行時のトラブルシューティング**

**テストがハングする場合**
```bash
# タイムアウトを設定
timeout 120 poetry run pytest tests/ -v

# 特定のテストをスキップ
poetry run pytest tests/ -k "not test_problematic"
```

**カメラアクセスエラー**
- すべてのカメラテストは完全にモック化されています
- 実際のカメラは不要です
- 詳細は[TEST_DESIGN.md](docs/TEST_DESIGN.md)参照

**詳細なテスト設計**

完全なテスト設計については、**[docs/TEST_DESIGN.md](docs/TEST_DESIGN.md)**を参照してください。以下の情報が含まれています：
- テスト戦略とテストピラミッド
- 173個すべてのテストケースの詳細
- モック化のベストプラクティス
- トラブルシューティングガイド

### 📚 開発者ドキュメント

開発に必要な詳細ドキュメントは`docs/`ディレクトリにあります：

- **[docs/README.md](docs/README.md)** - ドキュメント概要とナビゲーション
- **[docs/REQUIREMENTS_OVERVIEW.md](docs/REQUIREMENTS_OVERVIEW.md)** - プロジェクトの初期要件
- **[docs/REQUIREMENTS_SPECIFICATION.md](docs/REQUIREMENTS_SPECIFICATION.md)** - 詳細な機能仕様
- **[docs/TEST_DESIGN.md](docs/TEST_DESIGN.md)** - テスト戦略と173個のテストケース

**推奨読書順序：**

1. **REQUIREMENTS_OVERVIEW.md** - プロジェクトの全体像を把握
2. **REQUIREMENTS_SPECIFICATION.md** - 詳細な仕様を理解
3. **TEST_DESIGN.md** - テスト方針を学習

---

## 📚 その他

### 🚀 主な機能

- **QRコード読み取り**: PCカメラまたは画像ファイルからQRコードを読み取り
- **複数アカウント管理**: 複数のアカウントのOTPを同時に管理・表示
- **リアルタイム表示**: 1秒間隔でOTPを自動更新（プログレスバー付き）
- **セキュアな保存**: セキュリティコードはPBKDF2で暗号化してローカル保存
- **コマンドライン操作**: 直感的なコマンドラインインターフェース
- **Docker連携**: otpauthコンテナを使用したQRコード解析
- **アカウント管理**: 一覧、検索、更新、削除機能

### 📋 システム要件

- **Python**: 3.13以上（推奨: 3.13.9）
- **Poetry**: 依存関係管理
- **Docker**: QRコード解析用
- **macOS**: カメラアクセス権限
- **システムライブラリ**: zbar（QRコード読み取り用）

#### 主要な依存関係

```toml
[tool.poetry.dependencies]
python = "^3.13"
pyotp = "^2.9.0"              # OTP生成
opencv-python = "^4.8.1"      # QRコード読み取り
cryptography = "^41.0.7"      # 暗号化
Pillow = "^10.0.1"            # 画像処理
docker = "^6.1.3"             # Dockerクライアント
numpy = "^1.24.0"             # 数値計算

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"             # テストフレームワーク
pytest-cov = "^4.0.0"         # カバレッジ
black = "^23.0.0"             # フォーマッター
flake8 = "^6.0.0"             # Linter
mypy = "^1.0.0"               # 型チェッカー
```

---

**開発環境**: macOS Sequoia 24.6.0 | Python 3.13.9 | Poetry 2.2.1
