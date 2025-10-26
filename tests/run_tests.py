#!/usr/bin/env python3
"""
テスト実行スクリプト
"""
import subprocess
import sys
import os


def run_tests():
    """テストを実行"""
    print("🧪 ワンタイムパスワードアプリケーション テスト実行")
    print("=" * 60)
    
    # テストディレクトリに移動
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 単体テスト実行
    print("\n📋 単体テスト実行中...")
    result = subprocess.run([
        "poetry", "run", "pytest", 
        "tests/unit/", 
        "-v", 
        "--cov=src", 
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print("❌ 単体テストが失敗しました")
        return False
    
    print("✅ 単体テスト完了")
    
    # 統合テスト実行
    print("\n🔗 統合テスト実行中...")
    result = subprocess.run([
        "poetry", "run", "pytest", 
        "tests/integration/", 
        "-v"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print("❌ 統合テストが失敗しました")
        return False
    
    print("✅ 統合テスト完了")
    
    # 全テスト実行
    print("\n🎯 全テスト実行中...")
    result = subprocess.run([
        "poetry", "run", "pytest", 
        "tests/", 
        "-v", 
        "--cov=src", 
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print("❌ テストが失敗しました")
        return False
    
    print("✅ 全テスト完了")
    print("\n📊 カバレッジレポートが生成されました:")
    print("   - HTML: htmlcov/index.html")
    print("   - XML: coverage.xml")
    
    return True


def run_specific_test(test_path):
    """特定のテストを実行"""
    print(f"🎯 特定テスト実行: {test_path}")
    
    result = subprocess.run([
        "poetry", "run", "pytest", 
        test_path, 
        "-v"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def run_with_markers(marker):
    """マーカー指定でテスト実行"""
    print(f"🏷️ マーカー指定テスト実行: {marker}")
    
    result = subprocess.run([
        "poetry", "run", "pytest", 
        "-m", marker,
        "-v"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--specific":
            if len(sys.argv) > 2:
                success = run_specific_test(sys.argv[2])
            else:
                print("❌ テストパスを指定してください")
                sys.exit(1)
        elif sys.argv[1] == "--marker":
            if len(sys.argv) > 2:
                success = run_with_markers(sys.argv[2])
            else:
                print("❌ マーカーを指定してください")
                sys.exit(1)
        else:
            print("❌ 無効なオプションです")
            print("使用法:")
            print("  python run_tests.py                    # 全テスト実行")
            print("  python run_tests.py --specific <path>  # 特定テスト実行")
            print("  python run_tests.py --marker <marker>  # マーカー指定実行")
            sys.exit(1)
    else:
        success = run_tests()
    
    if success:
        print("\n🎉 全てのテストが成功しました！")
        sys.exit(0)
    else:
        print("\n💥 テストが失敗しました")
        sys.exit(1)
