#!/bin/bash

# ワンタイムパスワードアプリケーション テスト実行ラッパー
# 作成日: 2025年1月26日
# バージョン: 1.0

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
    echo "║     🧪 ワンタイムパスワードアプリケーション テストラッパー      ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# ヘルプ表示
show_help() {
    echo -e "${YELLOW}使用方法:${NC}"
    echo "  $0 [オプション] [コマンド]"
    echo ""
    echo -e "${YELLOW}コマンド:${NC}"
    echo "  all         全テストを実行（デフォルト）"
    echo "  unit        単体テストのみ実行"
    echo "  integration 統合テストのみ実行"
    echo "  coverage    カバレッジ付きテスト実行"
    echo "  quick       クイックテスト実行（失敗時停止）"
    echo "  watch       ファイル変更監視モード"
    echo "  clean       テストキャッシュとレポートをクリア"
    echo "  report      テストレポートを表示"
    echo ""
    echo -e "${YELLOW}オプション:${NC}"
    echo "  -h, --help     このヘルプを表示"
    echo "  -v, --verbose  詳細出力"
    echo "  -q, --quiet   簡潔出力"
    echo "  -f, --fail-fast 最初の失敗で停止"
    echo "  -p, --parallel 並列実行"
    echo "  --no-cov      カバレッジ測定を無効化"
    echo "  --html        HTMLレポート生成"
    echo "  --xml         XMLレポート生成"
    echo ""
    echo -e "${YELLOW}例:${NC}"
    echo "  $0                    # 全テスト実行"
    echo "  $0 unit              # 単体テストのみ"
    echo "  $0 coverage --html    # カバレッジ付き+HTMLレポート"
    echo "  $0 quick -f           # クイックテスト+失敗時停止"
    echo "  $0 watch              # 監視モード"
}

# 環境チェック
check_environment() {
    echo -e "${BLUE}🔍 環境チェック中...${NC}"
    
    # Poetryの存在確認
    if ! command -v poetry &> /dev/null; then
        echo -e "${RED}❌ Poetryがインストールされていません${NC}"
        echo "  インストール方法: curl -sSL https://install.python-poetry.org | python3 -"
        exit 1
    fi
    
    # Pythonの存在確認
    if ! poetry run python --version &> /dev/null; then
        echo -e "${RED}❌ Python環境が正しく設定されていません${NC}"
        exit 1
    fi
    
    # pytestの存在確認
    if ! poetry run pytest --version &> /dev/null; then
        echo -e "${RED}❌ pytestがインストールされていません${NC}"
        echo "  インストール方法: poetry install"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 環境チェック完了${NC}"
}

# テスト実行前の準備
prepare_test() {
    echo -e "${BLUE}🔧 テスト準備中...${NC}"
    
    # テストディレクトリの存在確認
    if [ ! -d "tests" ]; then
        echo -e "${RED}❌ testsディレクトリが見つかりません${NC}"
        exit 1
    fi
    
    # 一時ディレクトリの作成
    mkdir -p .pytest_cache
    mkdir -p htmlcov
    
    echo -e "${GREEN}✅ テスト準備完了${NC}"
}

# 全テスト実行
run_all_tests() {
    echo -e "${PURPLE}🚀 全テスト実行中...${NC}"
    
    local args=""
    if [ "$VERBOSE" = true ]; then
        args="$args -v"
    fi
    if [ "$QUIET" = true ]; then
        args="$args -q"
    fi
    if [ "$FAIL_FAST" = true ]; then
        args="$args -x"
    fi
    if [ "$PARALLEL" = true ]; then
        args="$args -n auto"
    fi
    if [ "$NO_COV" = false ]; then
        args="$args --cov=src --cov-report=term-missing"
        if [ "$HTML_REPORT" = true ]; then
            args="$args --cov-report=html:htmlcov"
        fi
        if [ "$XML_REPORT" = true ]; then
            args="$args --cov-report=xml:coverage.xml"
        fi
    fi
    
    poetry run pytest tests/ $args
}

# 単体テスト実行
run_unit_tests() {
    echo -e "${PURPLE}🔬 単体テスト実行中...${NC}"
    
    local args=""
    if [ "$VERBOSE" = true ]; then
        args="$args -v"
    fi
    if [ "$QUIET" = true ]; then
        args="$args -q"
    fi
    if [ "$FAIL_FAST" = true ]; then
        args="$args -x"
    fi
    if [ "$PARALLEL" = true ]; then
        args="$args -n auto"
    fi
    if [ "$NO_COV" = false ]; then
        args="$args --cov=src --cov-report=term-missing"
        if [ "$HTML_REPORT" = true ]; then
            args="$args --cov-report=html:htmlcov"
        fi
        if [ "$XML_REPORT" = true ]; then
            args="$args --cov-report=xml:coverage.xml"
        fi
    fi
    
    poetry run pytest tests/unit/ $args
}

# 統合テスト実行
run_integration_tests() {
    echo -e "${PURPLE}🔗 統合テスト実行中...${NC}"
    
    local args=""
    if [ "$VERBOSE" = true ]; then
        args="$args -v"
    fi
    if [ "$QUIET" = true ]; then
        args="$args -q"
    fi
    if [ "$FAIL_FAST" = true ]; then
        args="$args -x"
    fi
    
    poetry run pytest tests/integration/ $args
}

# カバレッジ付きテスト実行
run_coverage_tests() {
    echo -e "${PURPLE}📊 カバレッジ付きテスト実行中...${NC}"
    
    local args="-v --cov=src --cov-report=term-missing"
    if [ "$HTML_REPORT" = true ]; then
        args="$args --cov-report=html:htmlcov"
    fi
    if [ "$XML_REPORT" = true ]; then
        args="$args --cov-report=xml:coverage.xml"
    fi
    if [ "$FAIL_FAST" = true ]; then
        args="$args -x"
    fi
    
    poetry run pytest tests/ $args
}

# クイックテスト実行
run_quick_tests() {
    echo -e "${PURPLE}⚡ クイックテスト実行中...${NC}"
    
    local args="-x --tb=short"
    if [ "$VERBOSE" = true ]; then
        args="$args -v"
    fi
    
    poetry run pytest tests/unit/test_crypto_utils.py tests/unit/test_main.py $args
}

# 監視モード実行
run_watch_mode() {
    echo -e "${PURPLE}👀 ファイル変更監視モード開始...${NC}"
    echo "  ファイル変更を監視してテストを自動実行します"
    echo "  Ctrl+C で終了"
    
    # pytest-watchがインストールされているかチェック
    if ! poetry run ptw --help &> /dev/null; then
        echo -e "${YELLOW}⚠️  pytest-watchがインストールされていません${NC}"
        echo "  インストール方法: poetry add --group dev pytest-watch"
        echo "  代替として、手動でテストを実行します"
        
        while true; do
            echo -e "${CYAN}🔄 テスト実行中...${NC}"
            poetry run pytest tests/unit/test_crypto_utils.py -v
            sleep 2
        done
    else
        poetry run ptw tests/ --runner "poetry run pytest -v"
    fi
}

# テストキャッシュとレポートをクリア
clean_test_artifacts() {
    echo -e "${BLUE}🧹 テストキャッシュとレポートをクリア中...${NC}"
    
    # pytestキャッシュをクリア
    if [ -d ".pytest_cache" ]; then
        rm -rf .pytest_cache
        echo "✅ .pytest_cache を削除"
    fi
    
    # HTMLカバレッジレポートをクリア
    if [ -d "htmlcov" ]; then
        rm -rf htmlcov
        echo "✅ htmlcov を削除"
    fi
    
    # XMLレポートをクリア
    if [ -f "coverage.xml" ]; then
        rm coverage.xml
        echo "✅ coverage.xml を削除"
    fi
    
    # Pythonキャッシュをクリア
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ クリーンアップ完了${NC}"
}

# テストレポート表示
show_test_report() {
    echo -e "${PURPLE}📋 テストレポート${NC}"
    echo ""
    
    # HTMLレポートの確認
    if [ -f "htmlcov/index.html" ]; then
        echo -e "${GREEN}📊 HTMLカバレッジレポート:${NC}"
        echo "   file://$(pwd)/htmlcov/index.html"
        echo ""
    fi
    
    # XMLレポートの確認
    if [ -f "coverage.xml" ]; then
        echo -e "${GREEN}📊 XMLカバレッジレポート:${NC}"
        echo "   $(pwd)/coverage.xml"
        echo ""
    fi
    
    # 最新のテスト結果を表示
    if [ -f ".pytest_cache/v/cache/lastfailed" ]; then
        echo -e "${RED}❌ 最後に失敗したテスト:${NC}"
        cat .pytest_cache/v/cache/lastfailed | head -10
        echo ""
    fi
    
    # テスト統計
    echo -e "${BLUE}📈 テスト統計:${NC}"
    echo "  テストファイル数: $(find tests -name "test_*.py" | wc -l)"
    echo "  テスト関数数: $(grep -r "def test_" tests/ | wc -l)"
    echo ""
}

# テスト結果の要約表示
show_test_summary() {
    local exit_code=$1
    
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                        テスト結果要約                        ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}🎉 全てのテストが成功しました！${NC}"
    else
        echo -e "${RED}💥 テストが失敗しました${NC}"
        echo -e "${YELLOW}💡 詳細なエラー情報は上記の出力を確認してください${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📊 レポート:${NC}"
    if [ -f "htmlcov/index.html" ]; then
        echo -e "   HTML: ${CYAN}file://$(pwd)/htmlcov/index.html${NC}"
    fi
    if [ -f "coverage.xml" ]; then
        echo -e "   XML:  ${CYAN}$(pwd)/coverage.xml${NC}"
    fi
    
    echo ""
}

# メイン処理
main() {
    # デフォルト値設定
    COMMAND="all"
    VERBOSE=false
    QUIET=false
    FAIL_FAST=false
    PARALLEL=false
    NO_COV=false
    HTML_REPORT=false
    XML_REPORT=false
    
    # 引数解析
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
            -q|--quiet)
                QUIET=true
                shift
                ;;
            -f|--fail-fast)
                FAIL_FAST=true
                shift
                ;;
            -p|--parallel)
                PARALLEL=true
                shift
                ;;
            --no-cov)
                NO_COV=true
                shift
                ;;
            --html)
                HTML_REPORT=true
                shift
                ;;
            --xml)
                XML_REPORT=true
                shift
                ;;
            all|unit|integration|coverage|quick|watch|clean|report)
                COMMAND="$1"
                shift
                ;;
            *)
                echo -e "${RED}❌ 不明なオプション: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # ロゴ表示
    show_logo
    
    # 環境チェック
    check_environment
    
    # テスト準備
    prepare_test
    
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
        coverage)
            run_coverage_tests
            ;;
        quick)
            run_quick_tests
            ;;
        watch)
            run_watch_mode
            ;;
        clean)
            clean_test_artifacts
            ;;
        report)
            show_test_report
            ;;
        *)
            echo -e "${RED}❌ 不明なコマンド: $COMMAND${NC}"
            show_help
            exit 1
            ;;
    esac
    
    # テスト結果要約
    show_test_summary $?
}

# スクリプト実行
main "$@"
