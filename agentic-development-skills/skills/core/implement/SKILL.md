---
name: implement
description: 与えられた実装計画に従ってコードを書く実行パターン。小さな変更ごとにローカル検証しながら進める。計画は変更しない（変更が必要なら plan へ戻す）。plan.md が確定していて実装に着手する段階で使う。
---

# implement（計画に基づく実装）

確定した `plan.md` に従って実装する。**計画は変えない**。計画変更が必要になったら
`plan` Skill へ差し戻す（実装の途中で勝手に設計を変えない）。

## Inputs
- plan: 実装計画（`plan.md`）
- source_code: 現状のリポジトリ

## Outputs
- changed_files: 変更差分（リポジトリの diff）
- implementation-notes（任意）: 計画からの逸脱・保留事項があれば記録

## Preconditions
- `plan.md` が存在し、ステップに分割されている
- リポジトリが clean（未コミットの無関係な変更が無い）

## Procedure

```
Read Plan
  ↓
Implement Small Change   （計画の 1 ステップ分だけ）
  ↓
Run Local Validation     （lint / 型 / 該当ユニットテスト）
  ↓
Continue                 （次のステップへ。失敗が続くなら止める）
```

1. 計画のステップを 1 つ読む。
2. そのステップ分だけを実装する（小さく保つ）。
3. ローカル検証（静的チェック・該当ユニットテスト）を回す。
4. 通ったら次のステップへ。全ステップ完了まで繰り返す。

**この Skill がやらないこと**: 計画の変更、網羅的なテスト設計（→ `test`）、
完了判定（→ `verify`）。計画に無い機能追加をしない。

## Validation
- 各ステップ後に静的チェック（lint / 型）が通る
- 変更が計画のステップに対応している（計画外の変更が混ざっていない）

## Stop conditions
- 計画の全ステップを実装し、ローカル検証が通った

## Failure handling
- ローカル検証が繰り返し失敗 → 小さくして **Retry**、それでも駄目なら **Escalate**
- 計画通りに実装できない事実が判明 → **Rollback** して `plan` へ差し戻し
- 前提（依存・環境）が壊れている → **Request additional investigation**（`explore`）

## Adapter notes
確定作業のため、下位ティア（高速・低コスト）のエージェント/モデルでよい。
worktree/サンドボックス単位で 1 実装タスクを隔離すると並行実装が安全。詳細は `adapters/`。
