---
name: draft-compose
description: 収集済みの情報源と根拠だけを使って調査レポートの初稿を書く。source-collect の後に実行する。新たな検索は行わず、Source Note にある内容のみで構成し、主張が追跡できる形で出典を付ける。根拠のない数値や、不明点を埋める自然な文章を書かない。
version: 0.1
---

# Purpose

構造化された根拠を用いて**初稿**を作成する。

草稿は情報源を直接探索しない。前工程で保存した Source Note（と、あれば `claims.json`）だけを
材料にする。ここで新たに検索を始めると、根拠のない記述が混入する経路になる。

# Inputs

| 入力 | 説明 |
| --- | --- |
| `query.md` | Canonical Query。再読する |
| `execution-contract.json` | 出力形式・言語・章構成・禁止事項 |
| `decomposition.json` | 反映すべき論点 |
| `sources.json` | 使える情報源 |
| `research/notes/<source-id>.md` | 引用元 |
| `claims.json` | `evidence-organize` の出力。主張と根拠の構造 |

# Outputs

| ファイル | 内容 |
| --- | --- |
| `drafts/draft-01.md` | 初稿 |
| `drafts/draft-02.md` | 任意。Standard 以上で異なる論証構造を試す場合のみ |

# Preconditions

- `sources.json` が存在し、`high` の論点に根拠がある。

# Allowed Tools

`Read` / `Write`

`WebSearch` と `WebFetch` は使用しない。

# Prohibited Actions

- **新たな検索・取得を行わない。** 材料が足りないなら、足りないと書いて戻す。
- 根拠に存在しない数値を追加しない。概数への丸めも、出典と単位を保ったまま行う。
- 不明事項を自然な文章で埋めない。「〜と考えられる」で未確認を既定事実にしない。
- 内部 Scaffold（`scaffold.md`、TODO、作業メモ、ファイルパス）を本文へ混入しない。
- 出典数を水増ししない。同一 `independence_cluster` を複数根拠として数えない。

# Procedure

1. `query.md` と `execution-contract.json` を再読する。**依頼に答える**ことが目的で、
   情報源を紹介することが目的ではない。
2. `execution-contract.json` の `required_sections` と `decomposition.json` の
   `output_section` から章立てを決める。
3. 章ごとに、対応する Atomic Item の根拠だけを使って書く。
4. 主張には出典を付ける。`citation_style` に従う。
   - `inline-url`: 該当箇所に `[<title>](<url>)` を置く
   - `numbered`: 本文に `[1]` を置き、末尾に `## 参考文献` を作る
   逐語引用は Source Note の `# Quotable Passages` にある文字列と**一致させる**。
5. 未解決・未確認は、断定せずに明示する。
   「取得できなかった」「情報源間で見解が分かれる」を書くのは失敗ではなく品質である。
6. 複数草稿を作る場合は、言い換えではなく**異なる論証構造**にする。
   例: 結論先行型 / 比較評価型 / 課題・反証中心型。

# Validation

- `high` の Atomic Item がすべて本文のいずれかの章に現れる。
- 本文の逐語引用が Source Note に存在する。
- TODO・プレースホルダー・内部パスが残っていない。

# Exit Criteria

- すべての High Importance Atomic Item が本文に反映されている。
- 主要主張が出典（または Claim ID）に追跡可能である。
- 未解決事項を断定していない。

# Failure Handling

- 材料不足で章が書けない場合: その章に「未取得」と明記し、
  `coverage-matrix.md` の該当行を `unresolved` にして、`source-collect` へ戻す判断を仰ぐ。
  **空欄のまま先へ進めない。**

# Next Skill

Quick Tier では `citation-verify`。Standard 以上では `multi-review`。
