#!/bin/bash

# ワンタイムパスワードアプリケーション テスト実行ラッパー (Docker版)
# 作成日: 2025年1月26日
# バージョン: 2.0 (Docker対応)

set -e  # エラー時に終了

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ロゴ表示
show_logo() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║   🐳 ワンタイムパスワードアプリケーション テストラッパー       ║"
    echo "║                     (Docker版)                               ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# ヘルプ表示
show_help() {
    echo -e "${YELLOW}使用方法:${NC}"
    echo "  $0 [コマンド] [オプション]"
    echo ""
    echo -e "${YELLOW}コマンド:${NC}"
    echo "  all         全テストを実行（デフォルト）"
    echo "  unit        単体テストのみ実行"
    echo "  integration 統合テストのみ実行"
    echo "  lint        Lintチェック（Black, Flake8, MyPy）"
    echo "  black       Black フォーマットチェック"
    echo "  flake8      Flake8 スタイルチェック"
    echo "  mypy        MyPy 型チェック"
    echo "  format      Black フォーマット適用"
    echo "  clean       Dockerイメージとキャッシュをクリア"
    echo "  build       Dockerイメージをビルド"
    echo ""
    echo -e "${YELLOW}オプション:${NC}"
    echo "  -h, --help     このヘルプを表示"
    echo "  -v, --verbose  詳細出力"
    echo "  --rebuild      イメージを強制再ビルド"
    echo ""
    echo -e "${YELLOW}例:${NC}"
    echo "  $0                # 全テスト実行"
    echo "  $0 unit          # 単体テストのみ"
    echo "  $0 lint          # 全Lintチェック"
    echo "  $0 black         # Blackチェックのみ"
    echo "  $0 format        # Blackフォーマット適用"
    echo "  $0 build         # Dockerイメージビルド"
    echo "  $0 clean         # クリーンアップ"
}

# 環境チェック
check_environment() {
    echo -e "${BLUE}🔍 環境チェック中...${NC}"
    
    # Dockerの存在確認
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Dockerがインストールされていません${NC}"
        echo "  インストール方法: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Docker Composeの存在確認
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Composeが利用できません${NC}"
        echo "  Docker Compose v2が必要です"
        exit 1
    fi
    
    # docker-compose.ymlの存在確認
    if [ ! -f "docker/docker-compose.yml" ]; then
        echo -e "${RED}❌ docker/docker-compose.ymlが見つかりません${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 環境チェック完了${NC}"
}

# Dockerイメージのビルド
build_images() {
    local rebuild=$1
    echo -e "${BLUE}🔨 Dockerイメージをビルド中...${NC}"
    
    if [ "$rebuild" = true ]; then
        echo -e "${YELLOW}  強制再ビルドモード${NC}"
        docker compose -f docker/docker-compose.yml build --no-cache test
        docker compose -f docker/docker-compose.yml build --no-cache lint
    else
        docker compose -f docker/docker-compose.yml build test
        docker compose -f docker/docker-compose.yml build lint
    fi
    
    echo -e "${GREEN}✅ Dockerイメージのビルド完了${NC}"
}

# 全テスト実行
run_all_tests() {
    echo -e "${PURPLE}🚀 全テスト実行中...${NC}"
    
    local args=""
    if [ "$VERBOSE" = true ]; then
        args="-v"
    fi
    
    docker compose -f docker/docker-compose.yml run --rm test poetry run pytest tests/ $args --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html
    
    echo -e "${GREEN}✅ 全テスト完了${NC}"
}

# 単体テスト実行
run_unit_tests() {
    echo -e "${PURPLE}🔬 単体テスト実行中...${NC}"
    
    local args=""
    if [ "$VERBOSE" = true ]; then
        args="-v"
    fi
    
    docker compose -f docker/docker-compose.yml run --rm test-unit
    
    echo -e "${GREEN}✅ 単体テスト完了${NC}"
}

# 統合テスト実行
run_integration_tests() {
    echo -e "${PURPLE}🔗 統合テスト実行中...${NC}"
    
    local args=""
    if [ "$VERBOSE" = true ]; then
        args="-v"
    fi
    
    docker compose -f docker/docker-compose.yml run --rm test-integration
    
    echo -e "${GREEN}✅ 統合テスト完了${NC}"
}

# Lintチェック（全て）
run_lint_all() {
    echo -e "${PURPLE}🔍 Lintチェック実行中...${NC}"
    
    echo -e "${BLUE}  → Black フォーマットチェック${NC}"
    docker compose -f docker/docker-compose.yml run --rm black
    
    echo -e "${BLUE}  → Flake8 スタイルチェック${NC}"
    docker compose -f docker/docker-compose.yml run --rm flake8
    
    echo -e "${BLUE}  → MyPy 型チェック${NC}"
    docker compose -f docker/docker-compose.yml run --rm mypy
    
    echo -e "${GREEN}✅ 全Lintチェック完了${NC}"
}

# Blackチェック
run_black() {
    echo -e "${PURPLE}🎨 Black フォーマットチェック中...${NC}"
    docker compose -f docker/docker-compose.yml run --rm black
    echo -e "${GREEN}✅ Black チェック完了${NC}"
}

# Flake8チェック
run_flake8() {
    echo -e "${PURPLE}📏 Flake8 スタイルチェック中...${NC}"
    docker compose -f docker/docker-compose.yml run --rm flake8
    echo -e "${GREEN}✅ Flake8 チェック完了${NC}"
}

# MyPyチェック
run_mypy() {
    echo -e "${PURPLE}🔎 MyPy 型チェック中...${NC}"
    docker compose -f docker/docker-compose.yml run --rm mypy
    echo -e "${GREEN}✅ MyPy チェック完了${NC}"
}

# Blackフォーマット適用
apply_format() {
    echo -e "${PURPLE}✨ Black フォーマット適用中...${NC}"
    docker compose -f docker/docker-compose.yml run --rm lint poetry run black src/ tests/
    echo -e "${GREEN}✅ フォーマット適用完了${NC}"
}

# クリーンアップ
clean_up() {
    echo -e "${BLUE}🧹 クリーンアップ中...${NC}"
    
    # Dockerイメージの削除
    echo -e "${YELLOW}  Dockerイメージを削除中...${NC}"
    docker compose -f docker/docker-compose.yml down --rmi local 2>/dev/null || true
    
    # テストキャッシュの削除
    echo -e "${YELLOW}  テストキャッシュを削除中...${NC}"
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -f coverage.xml
    rm -f .coverage
    
    echo -e "${GREEN}✅ クリーンアップ完了${NC}"
}

# オプション解析
VERBOSE=false
REBUILD=false
COMMAND="all"

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_logo
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --rebuild)
            REBUILD=true
            shift
            ;;
        all|unit|integration|lint|black|flake8|mypy|format|clean|build)
            COMMAND=$1
            shift
            ;;
        *)
            echo -e "${RED}❌ 不明なオプション: $1${NC}"
            echo "ヘルプを表示: $0 --help"
            exit 1
            ;;
    esac
done

# メイン処理
main() {
    show_logo
    
    # クリーンとビルド以外は環境チェック
    if [ "$COMMAND" != "clean" ] && [ "$COMMAND" != "build" ]; then
        check_environment
    fi
    
    # コマンド実行
    case $COMMAND in
        all)
            run_all_tests
            ;;
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        lint)
            run_lint_all
            ;;
        black)
            run_black
            ;;
        flake8)
            run_flake8
            ;;
        mypy)
            run_mypy
            ;;
        format)
            apply_format
            ;;
        build)
            check_environment
            build_images $REBUILD
            ;;
        clean)
            clean_up
            ;;
        *)
            echo -e "${RED}❌ 不明なコマンド: $COMMAND${NC}"
            show_help
            exit 1
            ;;
    esac
    
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✨ 処理が完了しました！${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# スクリプト実行
main
