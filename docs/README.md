# OneTimePassword 開発者向けドキュメント

このディレクトリには、OneTimePasswordアプリケーションの開発に関連するドキュメントが含まれています。

## 📚 ドキュメント一覧

### [REQUIREMENTS_OVERVIEW.md](./REQUIREMENTS_OVERVIEW.md)
**初期要件概要**

プロジェクトの初期段階で作成された要件の概要です。
- プロジェクトの目的と背景
- 基本的な機能要件
- 技術スタックの選定理由

### [REQUIREMENTS_SPECIFICATION.md](./REQUIREMENTS_SPECIFICATION.md)
**詳細要件定義書**

REQUIREMENTS_OVERVIEW.mdを元に詳細化した、完全な要件定義書です。
- 機能要件の詳細仕様
- 非機能要件（セキュリティ、パフォーマンス等）
- システムアーキテクチャ
- ファイル構成
- コマンドラインインターフェース仕様
- データ構造の定義

### [TEST_DESIGN.md](./TEST_DESIGN.md)
**テスト設計書**

品質保証のための包括的なテスト戦略とテストケースの定義です。
- テスト戦略とテストピラミッド
- 各モジュールの単体テストケース
- 統合テストケース
- テスト実行方法
- トラブルシューティングガイド
- 現在のテストカバレッジ状況

## 🔄 ドキュメントの関係性

```
REQUIREMENTS_OVERVIEW.md
         ↓
  (詳細化・整理)
         ↓
REQUIREMENTS_SPECIFICATION.md
         ↓
   (テスト設計)
         ↓
   TEST_DESIGN.md
```

## 📖 推奨読書順序

### 新規開発者向け
1. **REQUIREMENTS_OVERVIEW.md** - プロジェクトの全体像を把握
2. **REQUIREMENTS_SPECIFICATION.md** - 詳細な仕様を理解
3. **TEST_DESIGN.md** - テスト方針と実装方法を学習

### 既存開発者向け
- 機能追加時: **REQUIREMENTS_SPECIFICATION.md** → **TEST_DESIGN.md**
- テスト追加時: **TEST_DESIGN.md**
- 仕様確認時: **REQUIREMENTS_SPECIFICATION.md**

## 🔗 関連リンク

- [ユーザー向けドキュメント (README.md)](../README.md)
- [英語版ドキュメント (README.en.md)](../README.en.md)
- [Dockerファイル](../docker/)
- [ソースコード](../src/)
- [テストコード](../tests/)

## 📝 ドキュメントの更新

ドキュメントは常に最新の状態を保つことが重要です：

1. **機能追加時**: REQUIREMENTS_SPECIFICATION.mdを更新
2. **仕様変更時**: REQUIREMENTS_SPECIFICATION.mdとTEST_DESIGN.mdを更新
3. **テスト追加時**: TEST_DESIGN.mdを更新

## ❓ 質問やフィードバック

ドキュメントに関する質問やフィードバックがある場合は、Issueを作成してください。

