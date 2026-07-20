---
name: test
description: 実装を機械的に検証するパターン。既存テスト・新規テスト・エッジケース・回帰を走らせ、失敗は分類して証拠を返す（原則ここでは修正しない）。実装後の検証や、修正が有効か確かめる段階で使う。
---

# test（機械的検証と失敗の分類）

実装を **機械的に**検証する。失敗したら**分類して証拠を返す**のが仕事で、
**原則ここでは修正しない**（修正は `fix`）。生成と評価の分離を守る。

## Inputs
- changed_files: 検証対象の実装
- project_spec: テスト条件・完了条件（`spec.md`）
- plan: 検証計画（`plan.md`、任意）

## Outputs
- `test-results.json`: 各テストの pass/fail、失敗の分類、再現手順、証拠（ログ）

## Preconditions
- ビルド/実行できる状態のリポジトリ
- テストランナー（または実行手段）が利用可能

## Procedure

```
Existing Tests        （まず既存の回帰を確認）
  ↓
New Tests             （今回の変更に対応するテストを追加）
  ↓
Edge Cases            （境界・異常系）
  ↓
Regression Tests      （周辺機能が壊れていないか）
```

失敗時:

```
Test Failure
  ↓
Classify Failure   （実装バグ / テスト誤り / 環境問題 / 仕様不一致）
  ↓
Return Evidence    （再現手順・期待値・実測値・ログを test-results.json へ）
```

1. 既存テストを走らせ回帰の有無を確認する。
2. 変更に対応する新規テストを追加する。
3. エッジケース・異常系を追加する。
4. 失敗は原因カテゴリへ分類し、再現手順と証拠を添えて記録する。

**この Skill がやらないこと**: 失敗の修正（→ `fix`）。「問題なし」を最終完了条件にしない
（機械的検証を最優先）。

## Validation
- 失敗が「落ちた」だけでなく分類・再現手順付きで記録されている
- 新規テストが今回の変更の要件を実際に確認している（緑を得るためだけの空テストでない）

## Stop conditions
- 対象範囲のテストがすべて実行され、結果が `test-results.json` に記録された

## Failure handling
- テストランナーが動かない → **Escalate**（環境問題として報告）
- 仕様不一致が判明 → 分類して `verify` / 人間へ **Escalate**（実装バグと切り分ける）
- 修正が要る失敗 → `test-and-fix` ループで `fix` へ渡す（本 Skill では直さない）

## Adapter notes
機械的検証（Static → Unit → Integration → Property）を LLM レビューより優先する。
CI 相当のコマンドを adapter が用意し、結果を JSON へ正規化する。詳細は `adapters/`。
