---
name: research-router
description: 調査依頼を受け取り、原依頼を正本として固定し、Run を初期化して調査規模（Tier）を決める入口スキル。「〜について調べて」「〜を比較したい」「このリポジトリ／論文／制度を調査して」といった調査の開始時に使う。調査そのものは行わず、query.md・execution-contract.json・run.json を作って次のスキルへ渡す。中断した調査の再開判断もここで行う。
version: 0.1
---

# Purpose

調査の**正本入力を固定**し、Run を初期化し、Tier と実行経路を決める。

このスキルは調査を実行しない。以後のすべての工程が同じ問いを見続けられるようにするための、
唯一の入口である。会話が長くなっても、要約されても、別のエージェントに引き継がれても、
`query.md` を読めば元の依頼がわかる状態を作る。

# Inputs

| 入力 | 説明 |
| --- | --- |
| ユーザーの原依頼 | 会話上の依頼文。**そのまま**保存する |
| `research/config/default.toml` | 任意。既定プロファイル |
| 既存の `research/runs/<run-id>/run.json` | 任意。再開時のみ |

# Outputs

| ファイル | 内容 |
| --- | --- |
| `research/runs/<run-id>/query.md` | Canonical Query（原依頼の逐語保存） |
| `research/runs/<run-id>/execution-contract.json` | 実行条件（`execution-contract.schema.json` に適合） |
| `research/runs/<run-id>/run.json` | Run 状態（`run.schema.json` に適合） |
| `research/runs/<run-id>/scaffold.md` | 内部用の作業メモ。最終成果物には出さない |

# Preconditions

- 書き込み可能な `research/` を作成できること。
- 依頼が調査（外部情報の収集・比較・統合）であること。実装作業やコード修正はこのスキルの対象外。

# Allowed Tools

`Read` / `Write` / `Bash`（ディレクトリ作成のみ）/ `AskUserQuestion`

# Prohibited Actions

- 調査本体（検索・取得・要約）を実行しない。
- 元の質問を要約版に置き換えない。言い換えて保存しない。
- Extended Tier を自動選択しない。ユーザーが明示した場合のみ。
- 不明点を推測で補完しない。判断が必要なら `AskUserQuestion` で聞くか、
  `execution-contract.json` の `scope_note` に前提として明記する。

# Procedure

1. **原依頼を逐語で保存する。** `query.md` に、ユーザーの依頼文をそのまま書く。
   要約・整形・翻訳をしない。補足が必要なら本文の下に `## 補足（router による注記）` として分ける。
2. **問いと条件を分離する。** 依頼文のうち、保存先・出力形式・言語・引用方式・禁止事項・期限・
   調査範囲は `execution-contract.json` へ移す。`query.md` には解くべき問いだけを残す。
3. **モダリティを分類する。** `collect` / `compare` / `synthesize` / `evaluate` / `forecast` / `design`。
4. **Tier を判定する。**
   - `quick`: 事実確認、単純比較、URL 一件の分析。情報源 3〜10 件程度。
   - `standard`: 技術調査、OSS 調査、制度比較、研究動向整理。情報源 10〜40 件程度。
   - `extended`: **ユーザーが明示的に指定した場合のみ。** サーベイ、大規模比較。
   判断がつかないときは `standard` を選ばず、`quick` から始めて必要になったら上げる。
5. **Run ID を発行する。** `<slug>-<YYYYMMDD>-<6桁英数>`。
   `<slug>` は依頼から作った英小文字・数字・ハイフンのみの短い識別子（最大 40 文字）。
6. **Run ディレクトリを作成する。** `research/runs/<run-id>/` と `drafts/` `verification/` `temp/`。
7. **次に実行する Skill を決める。** `run.json` の `next_step` に書く。
   - Phase 1 の quick / standard: `query-decompose`

## 再開する場合

既存の Run を指定された、または未完了 Run を見つけたときは、新しい Run を作らない。

1. `run.json` を読む。
2. `completed_steps` と現在 Step の成果物の有無を確認する。
3. `status` が `needs_human` なら、`human_actions_required` をユーザーに提示して止まる。
4. 完了条件を満たした Step は再実行しない。`next_step` から再開する。

# Validation

- `execution-contract.json` が `schemas/execution-contract.schema.json` に適合する。
- `run.json` が `schemas/run.schema.json` に適合する。
- `query.md` の本文がユーザーの依頼文を含む。

`python3 <plugin>/scripts/research_lint.py research/runs/<run-id>` で確認できる。

# Exit Criteria

- `query.md` が存在し、原依頼が逐語で保存されている。
- `execution-contract.json` が Schema に適合する。
- `run.json` に `tier` と `next_step` が記録されている。

# Failure Handling

- 依頼が曖昧で Tier も範囲も決められない場合: `AskUserQuestion` で 1 回だけ確認する。
  それでも決まらないなら `quick` で開始し、`scope_note` に前提を明記する。
- 書き込みに失敗した場合: 部分的な Run ディレクトリを残さず、失敗を報告して停止する。

# Next Skill

`query-decompose`
