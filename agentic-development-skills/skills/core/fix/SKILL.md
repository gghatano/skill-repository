---
name: fix
description: テスト結果またはレビュー指摘に基づいて修正するパターン。根本原因を特定し最小限の修正を当て、再検証する。新機能追加はしない。test 失敗や review 指摘を解消する段階で使う。
---

# fix（根本原因への最小修正）

`test-results.json` の失敗や `review.md` の指摘を解消する。**新しい機能追加はしない**。
根本原因を直し、最小限の変更に留める。

## Inputs
- issue: 対象の失敗/指摘（`test-results.json` の failure、または `review.md` の指摘）
- changed_files: 現状の実装
- plan: 実装計画（`plan.md`、任意）

## Outputs
- changed_files: 修正差分
- fix-notes（任意）: 根本原因と対処の要約

## Preconditions
- 対象の issue が再現手順 or 具体的箇所付きで特定されている

## Procedure

```
Issue
  ↓
Root Cause     （症状でなく原因を特定）
  ↓
Minimal Fix    （原因に対する最小の変更）
  ↓
Validation     （該当テスト/指摘が解消したか再検証）
```

1. issue の再現手順・箇所から根本原因を特定する（症状への対症療法を避ける）。
2. 原因に対する**最小限**の修正を当てる。
3. 該当するテスト/指摘が解消したことを再検証する。
4. 周辺への回帰が無いか確認する。

**この Skill がやらないこと**: 新機能追加、計画にない設計変更（必要なら `plan` へ差し戻し）。

## Validation
- 対象の失敗/指摘が解消している
- 回帰が発生していない（周辺テストが緑）
- 変更が最小（無関係なリファクタを混ぜていない）

## Stop conditions
- 対象 issue が解消し、回帰が無い

## Failure handling
- 根本原因が特定できない → **Request additional investigation**（`explore-root-cause`）
- 最小修正では直らず設計変更が要る → **Escalate** / `plan` へ差し戻し
- 修正が別の失敗を生む → **Rollback** して再検討

## Adapter notes
`test-and-fix` / `review-and-fix` の Composite からループの一手として呼ばれる。
1 修正 = 1 issue に対応させ、まとめて直さない（原因の切り分けを保つ）。詳細は `adapters/`。
