---
name: citation-verify
description: 草稿の引用・数値・出典の対応を検査する。draft-compose の後に実行する。引用文が情報源に実在するか、数値の単位や対象が一致するか、推論を情報源の主張として書いていないかを確認し、citation-check.json に結果を残す。Critical な引用エラーがあれば ship-verify を通さない。
version: 0.1
---

# Purpose

引用文・数値・主張・情報源の結び付きを検証する。

「もっともらしいが情報源にはそう書いていない」記述を、出荷前に捕まえる工程である。

# Inputs

| 入力 | 説明 |
| --- | --- |
| `drafts/draft-01.md` | 検査対象（複数草稿なら採用予定のもの） |
| `sources.json` | 情報源一覧 |
| `research/notes/<source-id>.md` | 引用の照合先 |
| `claims.json` | 任意 |

# Outputs

| ファイル | 内容 |
| --- | --- |
| `verification/citation-check.json` | 検証結果（`verification.schema.json` に適合、`kind: citation`） |

# Preconditions

- 草稿と `sources.json` が存在すること。

# Allowed Tools

`Read` / `Write` / `WebFetch`（URL 到達性の確認のみ）/ `Bash`（lint の実行）

# Prohibited Actions

- 草稿を修正しない。**このスキルは検査のみ**を行う。修正は `patch-apply` の責務。
- 検証できなかった項目を `pass` にしない。`skipped` または `warn` として残す。
- URL が開けないことを理由に、引用の中身を推測で確認済みにしない。

# Procedure

草稿の引用・数値ごとに、次を確認して `checks` に 1 件ずつ記録する。

1. **引用の実在**: 逐語引用の文字列が、対応する Source Note の `# Quotable Passages`
   （または原文）に存在するか。存在しなければ `fail` / `severity: critical`。
2. **文脈の保存**: 引用が原文の主張を反転・拡大していないか。
   条件付きの結論を無条件に書いていないかを特に見る。
3. **数値の一致**: 値・単位・期間・対象（母集団）が情報源と一致するか。
   単位や期間の欠落は `warn` 以上。照合先が特定できない数値は `unverified_numbers` に列挙する。
4. **URL の到達性**: `WebFetch` で確認する。到達不能は `warn`（情報源が消えた可能性）。
5. **出典の同定**: タイトル・発行者が Source Note と一致するか。
6. **撤回・訂正**: 論文なら撤回・訂正・版更新の有無を確認する。確認できなければ `skipped`。
7. **独立性**: 同一 `independence_cluster` を複数の独立根拠として数えていないか。
   数えていれば `fail`。
8. **推論と引用の区別**: 情報源から導いた推論を、情報源自身の主張として書いていないか。
   書いていれば `fail` / `severity: critical`。

判定を `verdict` に入れる。

- `pass`: `fail` が 0 件
- `pass_with_warnings`: `fail` が 0 件で `warn` がある
- `block`: `severity: critical` の `fail` が 1 件以上

# Validation

`python3 <plugin>/scripts/research_lint.py research/runs/<run-id>` を実行し、
`quote-integrity` と `schema-valid` が通ることを確認する。

# Exit Criteria

- 草稿中のすべての引用が検査済みである（`checks` に対応する項目がある）。
- Critical な引用エラーが 0 件である。
- 未確認の数値が `unverified_numbers` に明示されている。
- 推論と引用事実が区別されている。

# Failure Handling

- Critical な `fail` がある場合: `verdict` を `block` にする。
  Phase 1（`patch-apply` 無し）では、該当箇所と理由をユーザーに提示して停止する。
  草稿を自分で書き直さない。

# Next Skill

`ship-verify`
