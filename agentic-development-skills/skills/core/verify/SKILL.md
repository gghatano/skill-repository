---
name: verify
description: Project Spec と成果物の整合性を最終確認するパターン。要件カバレッジ・テストカバレッジ・未解決課題・既知の制約を突き合わせ、完了判定を出す。LLM の「問題ありません」を完了条件にしない。作業サイクルの最後に使う。
---

# verify（Spec との最終整合確認・完了判定）

Project Spec と成果物（実装・テスト）の整合を最終確認し、**完了判定**を出す。
実装・レビューとは独立させる（自己評価で完了を宣言しない）。

## Inputs
- project_spec: 要件・完了条件（`spec.md`）
- changed_files: 実装
- test_results: `test-results.json`
- review: `review.md`（任意）

## Outputs
- `verification.md`: `templates/verification-report.md` 形式の完了判定レポート

## Preconditions
- `spec.md` が存在する
- `test-results.json` が存在する（機械的検証が実施済み）

## Procedure

```
Spec  vs  Implementation  vs  Tests
```

確認対象:

```
Requirements Coverage   spec の各要件が実装・テストで満たされているか
Test Coverage           要件に対しテストが存在し緑か
Unresolved Issues       未解消の Critical/Major 指摘・失敗が残っていないか
Known Limitations       既知の制約・未対応範囲を明示できているか
```

1. Spec の要件を 1 つずつ、実装とテストへ突き合わせる（トレーサビリティ表）。
2. 未解決の Critical/Major が残っていないか確認する。
3. 既知の制約・未対応を明示する（隠さない）。
4. `verification.md` に **PASS / FAIL** と根拠を記す。

**この Skill がやらないこと**: 修正（→ `fix`）、新規実装。判定のみ。

## Validation
- 全要件が「実装 + テスト」の両方に紐づいている（片方だけは未達扱い）
- 機械的検証（`test`）の結果に基づく（LLM の主観的 OK を根拠にしない）
- FAIL の場合、何が不足かが具体的に書かれている

## Stop conditions
- 全要件を突き合わせ、PASS/FAIL を根拠付きで確定した

## Failure handling
- 要件未達（FAIL） → 不足を列挙し `plan` / `fix` へ差し戻し（**Request additional investigation**）
- 判定に必要な情報が欠落 → **Escalate**（人間に完了基準を確認）

## Adapter notes
完了判定は独立性が重要。実装 Agent とは別の Agent/Context で実行する。
機械的検証（Static → Unit → Integration → Property）を人間/LLM 判断より優先する。詳細は `adapters/`。
