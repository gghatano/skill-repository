---
name: contradiction-analyze
description: 情報源間の矛盾・条件差・定義差を整理し、結論を覆す反証を明示的に探す。evidence-organize の後、draft-compose の前に実行する。見かけ上の矛盾と実質的な矛盾を区別し、未解決の対立を成果物から隠さない。
version: 0.1
---

# Purpose

情報源間の**矛盾**を整理し、現在の結論に対する**反証を明示的に探す**。

放っておくと、調査は「最初に見つけた結論を補強する材料集め」になる。
この工程は、結論を**壊しに行く**ために存在する。反証が見つからなかったこと自体も記録に残す。

# Inputs

| 入力 | 説明 |
| --- | --- |
| `query.md` | Canonical Query。再読する |
| `claims.json` | 突き合わせる主張 |
| `sources.json` | 情報源の種別・独立性クラスタ |
| `research/notes/<source-id>.md` | 条件・限界の確認先 |

# Outputs

| ファイル | 内容 |
| --- | --- |
| `contradictions.json` | 矛盾と反証探索の記録（`contradiction.schema.json` に適合） |
| `source-tensions.md` | 対立の要約（人が読む） |

# Preconditions

- `claims.json` が存在すること。

# Allowed Tools

`Read` / `Write` / `WebSearch` / `WebFetch`（反証の探索に限る）

# Prohibited Actions

- 見かけ上の矛盾を、確認せずに「実質的な矛盾」として登録しない。
- 対立を「どちらも一理ある」でまとめて済ませない。**何が違うから食い違うのか**を書く。
- 未解決の対立を成果物から隠さない。都合の悪い情報源を落とさない。
- 反証を探していないのに「反証は見つからなかった」と書かない。
  探していないなら `outcome: not-searched` と記録する。

# Procedure

## 1. 矛盾の抽出

`claims.json` の主張を突き合わせ、食い違う組を見つける。各組に型を付ける。

| 型 | 意味 |
| --- | --- |
| `direct-contradiction` | 同一条件下で両立しない。**実質的な矛盾** |
| `scope-difference` | 対象範囲が違う |
| `definition-difference` | 用語の定義が違う |
| `time-difference` | 時期が違う（古い情報と新しい情報） |
| `population-difference` | 母集団が違う |
| `method-difference` | 測定・実験方法が違う |
| `measurement-difference` | 指標が違う |
| `unresolved` | 差の理由を特定できない |

`direct-contradiction` と `unresolved` 以外は、**見かけ上の矛盾**である。
`resolution` に「なぜ食い違って見えるのか」を書く。

## 2. 反証探索（この工程の本体）

`confidence: high` の主張と、結論に直結する主張について、次を**明示的に実行**する。

- 現時点の結論を覆す情報源は存在するか。
- 反対の結論を支持する**一次情報**はあるか（二次的な反論記事で済ませない）。
- 成功条件が成立しない境界条件は何か。
- 古い情報を現在にも当てはめていないか。**情報源の発行日を確認する。**
- 相関を因果として扱っていないか。
- 否定的な結果が報告されていないだけではないか（публикationバイアス）。

各主張について `counterargument_search` に記録する。
**探した結果見つからなかった**（`none-found`）と、**探していない**（`not-searched`）を区別する。

反証が見つかったら、その情報源を `source-collect` の手順で Source Note 化し、
`claims.json` に Claim として追加してから、矛盾として登録する。

## 3. 整理

`source-tensions.md` に、対立ごとに「何と何が / なぜ食い違うか / 現時点でどう扱うか」を書く。
追加の根拠がないと決着しないものは `additional_evidence_needed: true` にする。

# Validation

- `contradictions.json` が Schema に適合する。
- `claim_a` / `claim_b` が `claims.json` に実在する。
- `confidence: high` の主張が `counterargument_search` に登場する。

# Exit Criteria

- 重要な主張について反対証拠の探索を実施し、結果を記録している。
- 見かけ上の矛盾と実質的な矛盾を区別している。
- 未解決の対立を成果物から隠していない。

# Failure Handling

- 決着しない対立が残る場合: 消さずに `unresolved` として残し、
  `draft-compose` が本文で「見解が分かれている」と書けるようにする。

# Next Skill

`draft-compose`
