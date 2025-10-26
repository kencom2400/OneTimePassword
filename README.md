# ワンタイムパスワード生成アプリケーション

Google Authenticatorと同様の機能を持つワンタイムパスワード（OTP）生成アプリケーションです。PCカメラを使用してQRコードを読み取り、複数のアカウントのOTPを同時に管理・表示できます。

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
- **ローカル保存**: 機密データはGitHubにコミットされません
- **メモリクリア**: 使用後の機密データは即座にクリア
- **権限管理**: 適切なファイル権限設定
- **カメラアクセス**: 最小限の権限でカメラにアクセス

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
├── data/                         # データディレクトリ
│   └── accounts.json            # アカウントデータ（暗号化）
├── pyproject.toml               # Poetry設定ファイル
├── poetry.lock                  # Poetry依存関係ロックファイル
├── requirements.txt             # 従来の依存関係（参考用）
├── .gitignore                   # Git除外設定
├── LICENSE                      # ライセンスファイル
├── README.md                    # このファイル
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
black = "^23.0.0"
flake8 = "^6.0.0"
mypy = "^1.0.0"
```

### 開発環境情報

- **Python**: 3.13.9（pyenv管理）
- **Poetry**: 2.2.1
- **仮想環境**: `/Users/kencom/Library/Caches/pypoetry/virtualenvs/onetimepassword-78G70__u-py3.13`
- **OS**: macOS Sequoia 24.6.0

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