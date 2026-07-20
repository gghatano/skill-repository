---
name: independent-review
description: 複数のレビュアーが相互に出力を共有せず独立に評価し、統合 Agent だけが全結果を受け取ってまとめる構造。設計・実装・技術選定を多観点で堅牢に評価したいときに使う。同じ前提への収束を防ぐ Context 隔離が要。review と integrate を組み合わせた Composite Skill。
---

# independent-review（独立多観点レビュー → 統合）

複数レビュアーを**互いに隔離**して走らせ、`integrate` が全結果を統合する。
「独立解生成（independent-solution）」の評価特化版。設計・実装・技術選定の堅牢な評価に使う。

## Inputs
- target: 評価対象（`plan.md` / 実装 / 技術選定候補）
- project_spec: `spec.md`
- config: `{ reviewers: <n | 観点リスト>, aggregation: judge|scoring|merge }`

## Outputs
- `review.md`: 統合済みレビュー（`integrate` の `integration.md` を兼ねる）

## Preconditions
- 評価対象が確定している
- レビュアーを独立 Context で複数動かせる（無い環境は逐次隔離で代替）

## Procedure

```
Reviewer A ─┐   （各レビュアーは互いの出力を見ない）
Reviewer B ─┼→ Integrator → review.md
Reviewer C ─┘   （統合 Agent だけが全結果を受け取る）
```

1. 観点をレビュアーへ割り当てる（例: Correctness / Security / Performance、または汎用 N 体）。
2. 各レビュアーに **`spec` と対象だけ**を渡し、**他レビュアーの結果は渡さない**。
3. 各レビュアーが独立に `review` を実施する。
4. `integrate` が全 `review` を統合（dedup・衝突解消・重大度整理）する。

**Context 共有範囲**: `shared = [project_spec, target]` / `isolated = [reviewer_outputs]`。

## Validation
- レビュアー間で Context が実際に隔離されている（同一前提への収束が無い）
- 統合で重複指摘が dedup され、重大度が整理されている
- 各採用指摘に出所（どのレビュアー・根拠）が残っている

## Stop conditions
- 全レビュアーが完了し、`integrate` が統合結果を確定した

## Failure handling
- レビュアーが同じ指摘に収束（独立性の欠如） → 観点を分け直して再実行
- 統合で優劣がつかない → `aggregation` を judge に切り替え、なお割れれば **Escalate**
- レビュアーを並列化できない環境 → 逐次だが Context を毎回リセットして隔離を保つ

## Adapter notes
- **Claude Code**: Task tool で N サブエージェントを 1 メッセージ内に並列起動 → バリア → 統合。
- **Codex**: sub-agent 機構で並列 → 統合。
- **Generic**: Context をリセットしながら逐次隔離実行 → 統合。
詳細は `adapters/`。並列 Agent の追加コストに見合う品質向上があるかを Workflow 評価で測る。
