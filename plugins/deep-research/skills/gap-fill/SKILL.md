---
name: gap-fill
description: レビュー指摘のうち追加情報が必要なものだけを対象に、限定的な再調査を行う。multi-review の後、patch-apply の前に実行する。Finding ID に紐づく調査だけを行い、調査範囲を無制限に広げない。解消できなかった不足は unresolved として残す。
version: 0.1
---

# Purpose

Reviewer 指摘のうち、**追加情報が必要なものだけ**を対象に再調査する。

レビューで穴が見つかると、つい調査全体をやり直したくなる。この工程の役割は、
**穴の形に合わせて必要な分だけ**掘り、それ以外に手を広げないことである。

# Inputs

| 入力 | 説明 |
| --- | --- |
| `reviews/*.json` | `requires_additional_research: true` の Finding |
| `sources.json` | 既存の情報源（重複取得を避ける） |
| `claims.json` | 更新対象の主張 |
| `contradictions.json` | 任意。`additional_evidence_needed: true` の対立 |

# Outputs

| ファイル | 内容 |
| --- | --- |
| `gap-fill.json` | 追加調査の記録（`gap-fill.schema.json` に適合） |
| `gap-fill-report.md` | 何を探し、何が分かり、既存の主張がどう変わったか |
| `research/notes/<source-id>.md` | 追加した Source Note |
| `sources.json` / `claims.json` | 更新 |

# Preconditions

- `reviews/` に Finding が存在すること。

# Allowed Tools

`Read` / `Write` / `Edit` / `WebSearch` / `WebFetch`

# Prohibited Actions

- **Finding に紐づかない調査をしない。** 「ついでに調べておく」をしない。
- プロファイルの `gap_fill.max_queries` / `max_new_sources` を超えて広げない。
- 見つからなかったことを、見つかったかのように書かない。
- 既存の主張を、新情報と突き合わせずに書き換えない。

# Procedure

1. `reviews/*.json` から `requires_additional_research: true` の Finding を集める。
   これが**今回の調査対象のすべて**である。
2. Finding ごとに Gap を 1 件立てる（`gap_id`: `G-001` から連番）。
   - `finding_id`: 対応する Finding。**必ず実在する ID を書く**
   - `queries`: 実行する検索。何を探すのかを先に書く
3. `sources.json` を確認し、**既に取得済みの情報源を再取得しない**。
4. `source-collect` と同じ手順で Source Note を作る（優先順位・独立性クラスタ・取得日時）。
5. 新情報が既存の主張へ与えた影響を `impact` に書く。
   - 主張が**補強された** / **条件付きに限定された** / **覆された** / **変化なし**
   影響を受けた Claim は `affected_claim_ids` に記録し、`claims.json` を更新する。
6. `status` を決める。
   - `resolved`: 指摘が解消した
   - `partially-resolved`: 部分的に埋まったが不足が残る
   - `unresolved`: 追加調査でも埋まらなかった
7. `unresolved` は**消さずに残す**。`gap-fill-report.md` に、何を試して駄目だったかを書く。
   対応する Finding は `patch-apply` で `escalated` または理由付きの `accepted` にする。

# Validation

- `gap-fill.json` が Schema に適合する。
- 各 `finding_id` が `reviews/*.json` に実在する（Lint `gap-fill-scope`）。
- 新規 Source Note が `source-metadata` を満たす。

# Exit Criteria

- 各 Gap が対応する Finding ID を持つ。
- 新規情報が既存の主張へ与えた影響が記録されている。
- 解消できなかった不足が `unresolved` として残されている。

# Failure Handling

- 検索上限に達しても埋まらない場合: 打ち切って `unresolved` にする。
  上限を自分で引き上げない。
- 新情報が既存の結論を覆した場合: `patch-apply` の局所修正では収まらない可能性がある。
  影響範囲を `gap-fill-report.md` に明記し、`draft-compose` へ戻す判断を仰ぐ。

# Next Skill

`patch-apply`
