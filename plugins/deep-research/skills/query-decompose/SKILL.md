---
name: query-decompose
description: 固定した調査依頼（Canonical Query）を、個別に調査できる原子論点へ分解し、Coverage Matrix と情報源計画を作る。research-router の次に実行する。何を調べれば依頼に答えたことになるかを先に決め、後工程の漏れと逸脱を防ぐ。
version: 0.1
---

# Purpose

Canonical Query を、**調査可能な原子論点（Atomic Item）**へ分解する。

「何を調べれば依頼に答えたことになるか」を先に確定させる。ここで漏れた論点は、
後工程では基本的に拾われない。逆に、ここに無い調査は範囲外である。

# Inputs

| 入力 | 説明 |
| --- | --- |
| `research/runs/<run-id>/query.md` | Canonical Query。**必ず再読する** |
| `research/runs/<run-id>/execution-contract.json` | 出力章・形式・範囲の制約 |

# Outputs

| ファイル | 内容 |
| --- | --- |
| `decomposition.json` | Atomic Item 一覧（`decomposition.schema.json` に適合） |
| `coverage-matrix.md` | 論点ごとの進捗表（人が読む正本） |
| `source-plan.json` | 論点ごとの探索方針（検索語・想定情報源種別） |

# Preconditions

- `query.md` と `execution-contract.json` が存在すること。

# Allowed Tools

`Read` / `Write`

# Prohibited Actions

- 情報源を探索・取得しない（それは `source-collect` の責務）。
- 依頼に無い論点を「あった方がよいから」で追加しない。
  関連するが範囲外のものは `open_questions` に退避する。
- 依頼にある論点を「調べにくいから」で落とさない。

# Procedure

1. `query.md` を再読する。会話の記憶や前工程の要約で代替しない。
2. 依頼を、**独立に検証できる単位**へ分解する。1 論点 = 1 つの答えられる問い。
   「AとBを比較して」は「Aの特性」「Bの特性」「比較軸」へ分ける。
3. 各 Atomic Item に付与する。
   - `id`: `Q-01` から連番
   - `question`: answerable な問いの形にする（名詞句で終わらせない）
   - `importance`: `high` / `medium` / `low`。**依頼の主目的に直接答えるものだけを `high`** にする
   - `evidence_required`: 必要な根拠種別（例 `official-doc`, `primary-paper`, `source-code`）
   - `output_section`: 最終レポートのどの章になるか
   - `status`: 初期値 `uncovered`
4. **曖昧語を洗い出す。** 「最新の」「主要な」「性能が良い」など、判定基準が定まらない語を
   `ambiguous_terms` に列挙し、どう解釈したかを `coverage-matrix.md` に書く。
5. **未確認事項を `open_questions` に書く。** 依頼だけでは決まらない前提。
6. `source-plan.json` に、論点ごとの検索語候補と当たるべき情報源の種別・優先順を書く。
   学術調査なら Web 検索より先に OpenAlex / Semantic Scholar / arXiv / Crossref を検討する。
7. `coverage-matrix.md` を作る。列は「Atomic Item / 必要根拠 / 予定情報源 / 取得状況 / 草稿反映 / 検証状況」。

# Validation

- `decomposition.json` が Schema に適合する。
- すべての `output_section` が `execution-contract.json` の `required_sections` を満たす
  （`required_sections` が指定されている場合）。

# Exit Criteria

- 依頼の主要要求がすべて Atomic Item に対応している。
- 各 Atomic Item に `evidence_required` が設定されている。
- 各 Atomic Item に出力章が対応づけられている。
- 曖昧語と未確認事項が明示されている。

# Failure Handling

- 依頼が広すぎて論点が 20 を超える場合: `high` を絞り込み、残りを `open_questions` へ移して
  ユーザーに範囲の確認を求める。無理に全件を `high` にしない。

# Next Skill

`source-collect`
