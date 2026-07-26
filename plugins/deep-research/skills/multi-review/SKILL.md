---
name: multi-review
description: 初稿を4つの観点（根拠・網羅・反証・依頼適合）で独立にレビューし、指摘を Finding として構造化する。draft-compose の後に実行する。一つの曖昧なレビューにまとめず、失敗モードごとに Reviewer を分けて、指摘対象を具体的に特定する。
version: 0.1
---

# Purpose

異なる観点の Reviewer を**独立に**実行し、指摘を構造化する。

「レビューして」と一度に頼むと、見つけやすい失敗（誤字・言い回し）に寄る。
失敗モードごとに Reviewer を分け、それぞれに**別の探し方**をさせるのがこのスキルの要点である。

# Inputs

| 入力 | 説明 |
| --- | --- |
| `query.md` | Canonical Query。Instruction Reviewer の基準 |
| `execution-contract.json` | 形式・禁止事項 |
| `decomposition.json` | Coverage Reviewer の基準 |
| `claims.json` | Evidence Reviewer の照合先 |
| `drafts/draft-01.md` | レビュー対象 |
| `contradictions.json` | 任意。Phase 3 以降 |

# Outputs

| ファイル | 内容 |
| --- | --- |
| `reviews/evidence-review.json` | 根拠と引用の対応（`review-finding.schema.json` に適合） |
| `reviews/coverage-review.json` | 論点の漏れ |
| `reviews/counterargument-review.json` | 反証・反対見解 |
| `reviews/instruction-review.json` | 依頼・形式・制約への適合 |

# Preconditions

- 草稿が存在すること。`claims.json` があれば Evidence Reviewer の精度が上がる。

# Allowed Tools

`Read` / `Write` / `Task`（Reviewer をサブエージェントとして独立実行する場合）

# Prohibited Actions

- 草稿を修正しない。**指摘するだけ**で、直すのは `patch-apply` の責務。
- 4 つの観点を 1 回の読みで済ませない。Reviewer ごとに独立して読む。
- 「もっと詳しく」「読みやすくすべき」だけの指摘を残さない。
  **対象箇所・問題・推奨アクション**が特定できないものは Finding にしない。
- 指摘が無いことを問題視して、無理に Finding を作らない。

# Procedure

Reviewer を 1 つずつ実行する。`Task` が使えるなら、各 Reviewer を独立したサブエージェントとして
起動し、他の Reviewer の結果を見せない（同じ結論に引きずられないようにする）。

## Evidence Reviewer

- 主張と根拠は対応しているか。`claims.json` に無い主張が本文にないか。
- 引用は文意を正しく表しているか。条件付きの結論を無条件に書いていないか。
- 数値の単位・対象・期間は正しいか。
- 二次情報を一次情報として扱っていないか。
- 同一 `independence_cluster` を複数の独立根拠として数えていないか。

## Coverage Reviewer

- `decomposition.json` の Atomic Item に、本文で触れられていないものはないか。
- 比較対象間で記述量が不均衡ではないか（片方だけ厚い比較は結論を歪める）。
- 重要な境界条件・前提が欠落していないか。

## Counterargument Reviewer

- 有力な反対意見を無視していないか。
- 成功事例だけを選択していないか。
- 現在の結論を覆す条件は何か。それが本文に書かれているか。
- 古い情報を現在にも当てはめていないか。

## Instruction Reviewer

- `query.md` の目的に答えているか。**情報源の紹介で終わっていないか。**
- `execution-contract.json` の形式・言語・必須セクションを満たしているか。
- `prohibitions` に違反していないか。
- 依頼に無い一般論が混入していないか。

## Finding の書き方

```json
{
  "finding_id": "F-001",
  "reviewer": "evidence",
  "severity": "critical",
  "target": { "file": "drafts/draft-01.md", "section": "3.2",
              "quote": "対象手法はすべてのケースで優位である" },
  "problem": "根拠論文は一つのベンチマークのみを対象としている",
  "evidence": ["src-004"],
  "recommended_action": "主張を対象条件付きに限定する",
  "requires_additional_research": false,
  "status": "open"
}
```

`severity` の目安。

| 値 | 基準 |
| --- | --- |
| `critical` | 事実として誤り、根拠がない、依頼に答えていない。**出荷を止める** |
| `major` | 条件が抜けている、重要な論点が欠落している |
| `minor` | 表現が不正確、出典の書き方が不統一 |
| `suggestion` | あると良い程度 |

# Validation

- 各 `reviews/*.json` が `review-finding.schema.json` に適合する。
- すべての Finding に `target.file` と `target.section` がある。

# Exit Criteria

- 4 つの Reviewer の出力が Schema に適合する。
- Critical と Major の指摘対象が具体的に特定されている。
- 抽象的な指摘だけを残していない。

# Failure Handling

- Critical が多数（目安 5 件以上）出た場合: 局所修正で直る規模を超えている可能性が高い。
  `patch-apply` へ進まず、構造問題として `draft-compose` の作り直しを提案する。

# Next Skill

追加調査が必要な Finding があれば `gap-fill`（Phase 3）。無ければ `patch-apply`。
