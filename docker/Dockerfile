# Python 3.13ベースイメージ
FROM python:3.13-slim

# 作業ディレクトリを設定
WORKDIR /app

# システム依存関係のインストール（OpenCV用）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    git \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Poetryのインストール
RUN pip install --no-cache-dir poetry==1.8.3

# Poetry設定（仮想環境を作成しない）
RUN poetry config virtualenvs.create false

# 依存関係ファイルのみを先にコピー（キャッシュ最適化）
COPY pyproject.toml poetry.lock ./

# 依存関係のインストール
RUN poetry install --no-interaction --no-ansi --no-root

# アプリケーションコードをコピー
COPY . .

# .venvディレクトリを削除（ホストから来た場合）
RUN rm -rf .venv

# プロジェクト自体をインストール
RUN poetry install --no-interaction --no-ansi --only-root

# デフォルトコマンド（テスト実行）
CMD ["poetry", "run", "pytest", "tests/", "-v"]

