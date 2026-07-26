---
name: evidence-organize
description: 収集した情報源から、主張・根拠・引用位置・条件・限界を claims.json として構造化する。source-collect の後、draft-compose の前に実行する。情報源が述べている主張と、こちらが導いた推論を型で区別し、根拠のない主張を確定事項にしない。
version: 0.1
---

# Purpose

取得した情報から、**主張（Claim）とその根拠**を構造化する。

草稿はこの `claims.json` を材料にする。ここで「誰がどこで何を言っているか」を確定させておくと、
後段のレビューと引用検証が、文章ではなく**構造**に対して行えるようになる。

# Inputs

| 入力 | 説明 |
| --- | --- |
| `query.md` | Canonical Query。再読する |
| `decomposition.json` | 各 Claim を紐づける論点 |
| `sources.json` | 情報源一覧 |
| `research/notes/<source-id>.md` | Claim の抽出元 |

# Outputs

| ファイル | 内容 |
| --- | --- |
| `claims.json` | 構造化した主張（`claim.schema.json` に適合） |
| `evidence-digest.md` | 論点ごとに根拠を並べた人間向けの要約 |
| `coverage-matrix.md` | 更新（各論点の根拠の有無を反映） |

# Preconditions

- `sources.json` と Source Note が存在すること。

# Allowed Tools

`Read` / `Write` / `Edit`

# Prohibited Actions

- 新たな情報源を探索・取得しない（`source-collect` の責務）。
- 根拠のない主張を `fact` や `empirical` として登録しない。
- 情報源が述べていないことを `author-claim` にしない。
  自分で導いたものは必ず `inference` にする。
- 数値主張を、出典位置（`location`）なしで登録しない。

# Procedure

1. `query.md` と `decomposition.json` を再読する。
2. Source Note の `# Relevant Claims` と `# Evidence` から、主張を 1 件ずつ取り出す。
3. 各 Claim に付与する。
   - `claim_id`: `C-001` から連番
   - `statement`: 一文で書く。複数の主張を 1 件に詰めない
   - `claim_type`: 下記の型から選ぶ
   - `confidence`: `high` / `medium` / `low`
   - `supports`: `source_id` と **`location`（節・ページ・見出し）** と `evidence_type`
   - `conditions`: その主張が成り立つ前提（対象・期間・母集団）
   - `limitations`: 情報源自身が認めている限界
   - `related_atomic_items`: 対応する `Q-xx`
4. **型を厳密に使い分ける。**

| 型 | 使いどころ |
| --- | --- |
| `fact` | 検証可能な事実 |
| `definition` | 用語や範囲の定義 |
| `empirical` | 実験・観測にもとづく結果 |
| `causal` | 因果を主張するもの |
| `comparative` | 比較の結果 |
| `normative` | 「〜すべき」という規範 |
| `forecast` | 将来予測 |
| `author-claim` | **情報源の著者が述べている**主張 |
| `inference` | **こちらが情報源から導いた**推論 |

   `inference` には `derived_from` に根拠にした Claim ID を書く。
   `supports` が空でよいのは `inference` だけである。
5. **相関を因果として登録しない。** 情報源が相関しか示していないなら `empirical` にとどめる。
6. `evidence-digest.md` に、論点ごとに「主張 → 根拠 → 条件 → 限界」を並べる。
7. `coverage-matrix.md` の「草稿反映」列の手前まで（根拠の有無）を更新する。

# Validation

- `claims.json` が `claim.schema.json` に適合する。
- Lint `claim-provenance` が通る（`supports` があるか `inference` である）。
- `supports` の `source_id` が `sources.json` に実在する。

# Exit Criteria

- 主要な結論候補が Claim として構造化されている。
- Claim ごとに、情報源に基づくのか推論なのかが記録されている。
- 数値主張に出典位置が存在する。
- 根拠のない主張を確定事項として登録していない。

# Failure Handling

- 論点に対応する Claim が作れない場合: その論点の `status` を `unresolved` にし、
  `evidence-digest.md` に「根拠なし」と明記する。推測で Claim を作らない。

# Next Skill

Quick Tier では `draft-compose`。Standard 以上では `contradiction-analyze`。
