# deep-research — 調査ワークフロー（Deep Research）

記事・論文・OSS・制度資料などの調査を、単発の検索と要約ではなく、**再現可能で検査可能な工程**として実行するスキル群。依頼を正本として固定し、論点分解 → 情報源収集 → 初稿 → 引用検証 → 出荷判定までをファイル受け渡しで進めます。中断しても途中から再開できます。

現在は **Phase 1（最小実行ループ）と Phase 2（品質レビュー）** を提供します。

## 導入

```
/plugin marketplace add gghatano/skill-repository
/plugin install deep-research@gghatano-skills
```

スキルは `/deep-research:<skill-name>`（例: `/deep-research:research-router`）で呼び出せます。

## 使い方

調査を始めるときは `research-router` を呼ぶだけです。

```
/deep-research:research-router このリポジトリの設計思想を、READMEと実装から調べて
```

router が `research/runs/<run-id>/` を作り、依頼を `query.md` として固定します。以降は
`query-decompose` → `source-collect` → `evidence-organize` → `draft-compose` → `multi-review`
→ `patch-apply` → `citation-verify` → `ship-verify` の順に進みます（Quick Tier ではレビューを省いて
`draft-compose` から `citation-verify` へ）。各スキルは前工程が書いたファイルを読むので、
会話が長くなっても依頼が変質しません。

中断した調査は、同じ Run を指定して `research-router` を呼べば `run.json` から再開します。

## 何を得られるか

| | |
| --- | --- |
| 入力 | 調査したい問いと、任意の実行条件（形式・言語・引用方式・禁止事項） |
| すること | 依頼を固定し、論点へ分解し、公式・一次情報を優先して集め、主張と根拠を構造化し、その根拠だけで初稿を書き、4観点でレビューして局所修正し、引用を検証して出荷判定する |
| 得られるもの | 引用付きの `final-report.md` と、再利用できる Source Note 群、検証結果の記録 |

## 含まれるスキル

### Phase 1（最小実行ループ）

| スキル | 役割 |
| --- | --- |
| `research-router` | 依頼の固定、Run 初期化、Tier 判定、再開判断 |
| `query-decompose` | 論点分解、Coverage Matrix、情報源計画 |
| `source-collect` | 情報源の探索・取得・Source Note 化 |
| `draft-compose` | 収集済み根拠だけを使った初稿作成 |
| `citation-verify` | 引用・数値・出典対応の検査 |
| `ship-verify` | Ship Gate による出荷判定と `final-report.md` 出力 |

### Phase 2（品質レビュー）

| スキル | 役割 |
| --- | --- |
| `evidence-organize` | 主張・根拠・条件・限界の構造化（著者の主張と推論を区別） |
| `multi-review` | 根拠・網羅・反証・依頼適合の4観点で独立レビュー |
| `patch-apply` | Finding 単位の局所修正（全文再生成の禁止） |

Phase 3 以降で `contradiction-analyze` / `gap-fill` / `vault-maintain` を追加します。
設計は `docs/design/deep-research-skill-pack.md` を参照してください。

## 同梱物

- `docs/*.md` — 規約（Canonical Query / Evidence Provenance / Source Independence / Patch-only /
  Human Intervention / Sensitive Data）
- `schemas/*.json` — Run・実行契約・論点分解・情報源・主張・レビュー指摘・Patch・検証結果の JSON Schema
- `scripts/research_lint.py` — スキーマ検証と Lint 10 種（標準ライブラリのみ）
- `config/profiles/*.toml` — Quick / Standard / Extended の既定値

## 導入後の調整

`config/profiles/*.toml` の情報源件数や語数は目標値です。対象領域に合わせて調整してください。**件数の達成自体を目的にしない**でください。

作業領域の既定は `research/` です。別の場所に置く場合は `config/default.toml` の `vault_root` を変更してください。機密情報を含む調査では、`docs/sensitive-data.md` に従って Run ディレクトリを Git 管理対象外にしてください。

Lint は導入先で次のように実行できます。

```bash
python3 <plugin>/scripts/research_lint.py research/runs/<run-id>
```

## 設計上の約束

- **Canonical Query**: 原依頼を逐語で保存し、要約を正本にしない
- **File-based Handoff**: 工程間の受け渡しは会話ではなくファイル
- **Markdown as Source of Truth**: Source Note が正本、索引は派生物
- **Structural Enforcement**: 重要なルールは Lint と Schema で機械的に検査する
- **Patch-only**: 初稿の確定後は全文を書き直さず、Finding 単位で局所修正する
- **取得失敗を成功として扱わない**: 未取得・未検証は明示して残す
