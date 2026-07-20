# Adapter: Claude Code

Skill/Workflow を Claude Code 上で実行するための対応づけ。

## 抽象操作 → Claude Code

| 抽象操作 | Claude Code での実行 |
| --- | --- |
| 独立サブエージェント N 体を並列起動 | `Agent` tool（Task）を **1 メッセージ内に複数**呼び出す |
| Context 隔離 | 各サブエージェントは独立 Context。親が共有物（`spec.md` 等）だけを渡す |
| バリア（全完了を待つ） | 並列サブエージェントの結果が揃ってから統合ステップへ |
| 並行実装の衝突回避 | `isolation: "worktree"` で 1 タスク = 1 worktree |
| モデルティア | サブエージェント `model` 指定（planner=上位 / implementer=下位 等）|
| 成果物受け渡し | リポジトリ上の `spec.md` / `plan.md` / `review.md` / `verification.md` |
| Skill の invoke | `SKILL.md` を配置し `Skill` tool から名前で呼ぶ |

## independent-review の実行例（概念）

```
親（オーケストレータ）
  ├─ Agent: reviewer(correctness)  ← spec.md + 対象のみ渡す（他レビュー結果は渡さない）
  ├─ Agent: reviewer(security)     ← 同上（並列・相互非共有）
  └─ Agent: reviewer(performance)  ← 同上
        ↓ 全完了を待つ（バリア）
  親が integrate を実行 → review.md
```

- 3 レビュアーは **同一メッセージ内の複数 `Agent` 呼び出し**で並列化する。
- 各レビュアーには対象と `spec.md` だけを渡し、**他レビュアーの出力を渡さない**（隔離）。
- 統合は親（または専用 judge サブエージェント）だけが全結果を受け取って行う。

## test-and-fix / review-and-fix ループ

- ループ制御（`max_iterations`）は**親**が持つ。
- `test`/`review`（評価）と `fix`（生成）を別サブエージェント/別 Context に分けると
  生成と評価の分離が保てる。

## 配置

- Skill: `.claude/skills/<skill>/SKILL.md`（core/composite をそのままコピー可）
- サブエージェント定義が要る場合: `.claude/agents/*.md`
