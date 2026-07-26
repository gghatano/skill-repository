---
name: patch-apply
description: レビュー指摘にもとづき、草稿を局所的に修正する。multi-review の後に実行する。文書全体を書き直さず、Finding 単位の Patch として対象箇所だけを直し、どの指摘をどう直したかを追跡できる形で残す。規模上限を超える修正は自動適用せずエスカレーションする。
version: 0.1
---

# Purpose

Reviewer 指摘にもとづき、草稿を**局所修正**する。

全文を書き直すと、指摘を直したかどうかが確認できなくなり、直っていた箇所が壊れる。
このスキルは「どの指摘に対して、どこを、どれだけ変えたか」を残しながら直す。

# Inputs

| 入力 | 説明 |
| --- | --- |
| `reviews/*.json` | 直す対象の Finding |
| `drafts/draft-01.md` | 修正対象 |
| `claims.json` | 修正の根拠 |
| `gap-fill.json` / `gap-fill-report.md` | `gap-fill` の結果。追加根拠と未解消の不足 |

# Outputs

| ファイル | 内容 |
| --- | --- |
| `patches/patch-plan.json` | 修正計画（`patch.schema.json`、`kind: plan`） |
| `patches/applied-patches.json` | 適用結果（`patch.schema.json`、`kind: applied`） |
| `drafts/draft-01.md` | **Edit による局所修正**。作り直さない |
| `reviews/*.json` | 各 Finding の `status` を更新 |

# Preconditions

- `reviews/` に Finding が存在すること。

# Allowed Tools

`Read` / `Edit`

**`Write` は使用しない。** 草稿の全文置換を構造的に防ぐための制約である。

# Prohibited Actions

- 草稿を `Write` で書き直さない。全文再生成は `docs/patch-only.md` 違反。
- Patch 対象外の箇所を変更しない。ついでの表現改善をしない。
- 引用番号・見出し・他の正しい主張を壊さない。
- 規模上限を超える修正を自動適用しない。
- 根拠を伴わずに主張を弱めて「指摘を消す」ことをしない。

# Procedure

1. `reviews/*.json` を読み、`severity` の順（`critical` → `major` → `minor`）に並べる。
2. **修正計画を先に書く。** Finding ごとに Patch を 1 件立て、`patches/patch-plan.json` に保存する。
   - `patch_id`: `P-001` から連番
   - `finding_ids`: 対応する Finding（**1 Patch = 1 論理修正**。複数 Finding をまとめない）
   - `target_file` / `target_section`
   - `operation`: `replace` / `insert` / `delete`
   - `before_summary` / `after_summary`: 何が何になるか
   - `max_changed_lines`: プロファイルの `patch.max_lines_per_patch`（既定 20）
3. **規模を見積もる。** 見積もりが `max_changed_lines` を超える Patch は適用しない。
   `status` を `escalated` にし、`escalation_reason` を書く。
   → 章の構成自体を変える必要があるということなので、`draft-compose` へ戻す判断を仰ぐ。
4. `Edit` で 1 Patch ずつ適用する。適用のたびに、対象節以外が変わっていないことを確認する。
5. `patches/applied-patches.json` に結果を書く。`changed_lines` に実際の変更行数を入れる。
6. **Finding の状態を更新する。**
   - 直した → `resolved`
   - 直さずエスカレーション → `escalated`
   - 直さないと決めた → `accepted` にし、**`accepted_reason` を必ず書く**
   - `critical` を `accepted` にしてよいのは、ユーザーが明示的に受容した場合のみ

# Validation

- `patches/*.json` が `patch.schema.json` に適合する。
- Lint `patch-scope` が通る（各 Patch が上限内、変更総量が比率上限内）。
- Lint `critical-findings` が通る（未解決の `critical` が無い）。

# Exit Criteria

- Critical Finding がすべて `resolved` / `escalated` / （明示受容された）`accepted` になっている。
- 適用 Patch と Finding の対応が `applied-patches.json` から追跡できる。
- 修正対象外の差分が許容範囲内である。

# Failure Handling

- `escalated` が出た場合: 出荷へ進まず、どの Finding が構造問題かをユーザーに提示する。
- Patch を当てたら別の箇所が壊れた場合: その Patch を戻し、`escalated` として扱う。
  壊れたまま次の Patch を重ねない。

# Next Skill

`citation-verify`
