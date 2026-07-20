---
name: review
description: 実装を独立した視点から評価するパターン。正確性・保守性・セキュリティ・性能・整合性・仕様準拠の観点で点検し、重大度付きの指摘を review-report に出す。実装した本人とは別の視点で評価する段階で使う（修正はしない）。
---

# review（独立視点での評価）

実装を**独立した視点**から評価する。生成者と評価者を分離するため、可能なら
実装した Agent とは別の Agent が担当する。**修正はしない**（修正は `fix`）。

## Inputs
- changed_files: レビュー対象の実装
- project_spec: 仕様（`spec.md`）
- plan: 実装計画（`plan.md`、任意）

## Outputs
- `review.md`: 重大度付きの指摘一覧（`templates/review-report.md` 形式）

## Preconditions
- レビュー対象の変更が確定している

## Procedure

観点:

```
Correctness      正しく動くか・境界条件
Maintainability  可読性・重複・凝集/結合
Security         入力検証・権限・秘匿情報の扱い
Performance      計算量・不要な処理・リソース
Consistency      既存コードの慣習との一致
Spec Compliance  spec.md の要件を満たすか
```

各指摘に重大度を付ける:

```
Critical   これがあるとリリース不可（データ破壊・脆弱性・仕様未達）
Major      修正すべき重要な問題
Minor      直したほうがよい軽微な問題
Suggestion 改善提案（任意）
```

1. 上記観点を順に点検する。
2. 各指摘に「該当箇所・問題・根拠・想定される失敗シナリオ・重大度」を書く。
3. `review.md` にまとめる。

**この Skill がやらないこと**: 修正（→ `fix`）。指摘の verify（→ 深掘りは `adversarial-review`）。

## Validation
- 各指摘が具体的な箇所（ファイル:行）と失敗シナリオを持つ
- Critical/Major には根拠がある（憶測の指摘を混ぜない）
- 「問題なし」で終わらせず、確認した観点を明記する

## Stop conditions
- 全観点を点検し、指摘（無指摘も含む）を `review.md` に記録した

## Failure handling
- 仕様が不明で準拠を判断できない → **Escalate**
- 指摘の真偽が判断できない → 深掘りを `adversarial-review` へ **Request additional investigation**

## Adapter notes
独立性のため、実装 Agent と別プロセス/別 Context のレビュアーで実行する。
複数観点を別レビュアーに分けて並列化し `integrate` する構成は `independent-review` を使う。
LLM レビューは機械的検証（`test`）の**後**に置く（代替にしない）。詳細は `adapters/`。
