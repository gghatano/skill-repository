---
name: ship-verify
description: 調査レポートを提出してよいか最終判定し、合格したら final-report.md を出力する。citation-verify の後に実行する。論点の網羅・根拠・引用検証・内部メモの混入・出力契約の充足を Ship Gate として検査し、block なら最終成果物を出さない。
version: 0.1
---

# Purpose

成果物をユーザーへ提出可能か判定する。**最後の関門**であり、ここを通らないものは出さない。

# Inputs

| 入力 | 説明 |
| --- | --- |
| `query.md` | Canonical Query。依頼に答えているかの基準 |
| `execution-contract.json` | 出力契約 |
| `decomposition.json` / `coverage-matrix.md` | 論点の網羅状況 |
| `drafts/draft-01.md` | 出荷候補 |
| `verification/citation-check.json` | 引用検証の結果 |
| `reviews/*.json` | 任意。Phase 2 以降 |

# Outputs

| ファイル | 内容 |
| --- | --- |
| `verification/ship-check.json` | 判定結果（`verification.schema.json` に適合、`kind: ship`） |
| `final-report.md` | 出荷物。**`verdict` が `block` の場合は作成しない** |

# Preconditions

- `citation-check.json` が存在すること。引用検証を飛ばして出荷しない。

# Allowed Tools

`Read` / `Write` / `Bash`（lint の実行）

# Prohibited Actions

- `block` 判定のまま `final-report.md` を作らない。
- 判定を通すために基準を緩めない。落ちた項目は落ちたまま報告する。
- 草稿の内容を書き換えない（体裁の抽出とヘッダ付与のみ）。

# Procedure

Ship Gate の 5 群を順に検査し、`checks` に記録する。

1. **Query Coverage**
   - `importance: high` の Atomic Item がすべて `covered` 以上、または `unresolved` として明示されている。
   - 未処理（`uncovered`）の `high` が残っていれば `fail` / `critical`。
2. **Evidence**
   - 主要主張に根拠がある。
   - `citation-check.json` の `verdict` が `block` でない。`block` ならここで `fail` / `critical`。
3. **Review**（Phase 2 以降。`reviews/` が無ければ `skipped`）
   - 未解決の Critical Finding が無い。
   - Major Finding は解消済み、または受容理由が記録されている。
4. **Hygiene**
   - Scaffold・内部メモ・作業ログが本文に混入していない。
   - `TODO` / `FIXME` / `<...>` / `{{...}}` 等のプレースホルダーが残っていない。
   - 内部ファイルパスが不要に露出していない。
5. **Output Contract**
   - `execution-contract.json` の `output_format` / `language` / `required_sections` を満たす。
   - `target_words` が指定されていれば、著しい過不足がない（±50% を目安に `warn`）。

判定:

- `pass`: `fail` なし
- `pass_with_warnings`: `fail` なし、`warn` あり。**警告内容をユーザーに明示して**出荷する
- `block`: `fail` が 1 件以上

`pass` または `pass_with_warnings` の場合のみ `final-report.md` を作る。
`drafts/draft-01.md` の本文をそのまま用い、必要なら `execution-contract.json` の
`required_sections` に沿ってヘッダを整える。内容は変更しない。

最後に `run.json` を更新する。`status` を `shipped`（または `blocked`）、
`completed_steps` に `ship-verify` を追加する。

# Validation

`python3 <plugin>/scripts/research_lint.py research/runs/<run-id>` が
`internal-leak` / `placeholder-check` / `coverage-complete` を含めて通ること。

# Exit Criteria

- `ship-check.json` が Schema に適合し、`verdict` が記録されている。
- `verdict` が `pass` / `pass_with_warnings` なら `final-report.md` が存在する。
- `verdict` が `block` なら `final-report.md` が存在せず、`run.json` が `blocked` である。

# Failure Handling

- `block` の場合: 落ちた `checks` を、対象箇所つきでユーザーに提示する。
  どの工程へ戻るべきか（`source-collect` / `draft-compose` / `citation-verify`）を示す。
  自動で書き直して再判定しない。

# Next Skill

なし（Run の終端）。Phase 4 以降は `vault-maintain` で情報源を再利用可能な状態にする。
