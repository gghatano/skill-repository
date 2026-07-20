---
name: plan
description: 実装前に変更内容を構造化する設計パターン。要件・制約・影響範囲・実装ステップ・検証計画を implementation-plan へ落とす。コードは書かない。実装に着手する前、または変更が大きい・影響範囲が不明なときに使う。
---

# plan（実装前の変更の構造化）

実装に入る前に「何を・どこを・どの順で変え、どう検証するか」を計画へ落とす。
**実装コードは書かない**。

## Inputs
- project_spec: 要件・制約・完了条件（`spec.md`）
- research: 調査結果（`research.md`、任意）
- source_code: 現状のリポジトリ

## Outputs
- `plan.md`: `templates/implementation-plan.md` 形式の実装計画

## Preconditions
- `spec.md` が存在し、達成すべき要件と完了条件が読める

## Procedure

```
Requirements
  ↓
Constraints
  ↓
Affected Components   （変更が波及するファイル・モジュール）
  ↓
Implementation Steps  （小さく検証可能な単位に分割）
  ↓
Validation Plan       （各ステップをどう確かめるか）
```

1. Spec から要件と完了条件を抜き出す。
2. 制約（互換性・性能・依存・非機能）を明示する。
3. 影響を受けるコンポーネントを列挙する（`explore` の結果を使う）。
4. 実装を**小さく検証可能なステップ**へ分割する（1 ステップ＝ローカル検証可能）。
5. 各ステップの検証方法（どのテスト・チェックで確認するか）を計画に含める。

**この Skill がやらないこと**: 実装（→ `implement`）。計画に迷いが残る場合は `explore` へ戻す。

## Validation
- 各ステップが独立して検証可能な粒度か
- Spec の全要件がいずれかのステップでカバーされているか（トレーサビリティ）
- 検証計画（Validation Plan）が空でないか

## Stop conditions
- Spec の全要件がステップに割り付き、各ステップに検証手段がある

## Failure handling
- 要件が曖昧で計画に落とせない → **Escalate**（Spec の明確化を人間に要求）
- 影響範囲が不明 → **Request additional investigation**（`explore` へ差し戻し）
- 途中で計画外の事実が判明 → `plan` に戻って再計画（`implement` 側で計画を勝手に変えない）

## Adapter notes
判断が中心のため、上位ティア（推論重視）のエージェント/モデルへ委譲すると質が上がる。
複数案を出して比較する場合は `independent-review` で計画をレビューする。
