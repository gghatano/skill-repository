---
name: dependency-graph
description: タスクディレクトリ ($ARGUMENTS) の inferred_schema.json と constraint_plan.md をもとに、列間の依存関係を DAG としてモデル化し work/dependency_graph.json を作成する。generation-design（線形版）の DAG 版の代替。 例:「列間の依存を DAG で設計して」「依存グラフを作って」
---

# dependency-graph

> 「仕様駆動 生成・評価サイクル」（規約 `.claude/docs/generation-cycle-conventions.md`）の
> **生成設計**フェーズの DAG プロファイル。`generation-design`（線形版）の代替であり、両者は
> 排他的に選択する。以下は合成データ プロファイルの中身。

合成データの生成方針を、列間の条件付き依存を DAG（有向非巡回グラフ）として設計するステップ。
`spec-ingest` の後に実行する。`generation-design`（線形版）の代替であり、両者は排他的に選択する。

方針は**ハイブリッド**: DAG の構造（ノード・エッジ）は spec/アナリストが宣言し、`estimate:"from_source"` のノードのパラメータは source データ（サンプル）から推定する（明示 `params` があればそれを優先）。

## 引数

`$ARGUMENTS` にタスクのルートディレクトリを受け取る。

## 入力

- `$ARGUMENTS/work/inferred_schema.json`
- `$ARGUMENTS/work/constraint_plan.md`
- `$ARGUMENTS/input/data_spec.md`
- `$ARGUMENTS/input/*sample_data*`（単一: `sample_data.csv` / 複数: `<table>_sample_data.csv`）

## 出力

- `$ARGUMENTS/work/dependency_graph.json`
- 必要に応じて `$ARGUMENTS/work/dependency_params.json`（`estimate:"from_source"` の推定パラメータを分離する場合）

## dependency_graph.json のスキーマ

トップレベル:
```json
{
  "version": "1.0",
  "tables": ["<table1>", "<table2>"],
  "keys": {
    "<table>": {"pk": "<PK列>", "fk": {"<FK列>": "<親table>.<親PK列>"}}
  },
  "cardinality": {
    "<child>_per_<parent>": {"type": "empirical_counts", "estimate": "from_source"}
  },
  "nodes": [ ... ],
  "generation_order": ["列 id をトポロジカル順に列挙（省略可、省略時は parents から自動トポソート）"],
  "notes": "..."
}
```

ノード（`nodes[]`）共通形:
```json
{"id": "<table>.<column>", "table": "<table>", "column": "<column>",
 "parents": ["<parent node id>", ...],
 "model": {"type": "<型>", "estimate": "from_source|explicit", "...": "型別フィールド"}}
```

- `parents` は同一レコード内の他列、または FK で結ばれた**親行の確定列**を参照できる。
- グラフは DAG（巡回禁止）。生成はトポロジカル順で行う。

モデル型（`model.type`）:
1. `marginal_categorical` — 親なしカテゴリ。params: `{value: prob}`。
2. `marginal_numeric` — 親なし数値。params: `{method: "empirical_bins|normal", ...}`（欠損率も保持）。
3. `cpt` — カテゴリ｜親（条件付き確率表）。params: 親キー→`{value: prob}`。**バックオフ必須**: セル件数が `min_count`（既定50）未満なら親を1つ落として粗い CPT へ後退し、最終的に周辺分布に到達する。`backoff` 情報を保持する。
4. `conditional_numeric` — 数値｜親。method: `binned_empirical`（親群ごとの経験分位サンプリング）または `normal_by_group`（群ごと mean/std）。群が小さい場合は親バックオフする。
5. `presence_gate` — 付与有無を親で条件化（例: 部位特異マーカー）。`gate`: `nonnull_prob_by_parent` またはルール `nonnull_when`、`value_model`: 非null時の値モデル（cpt 等）。null 表現は空文字。
6. `deterministic` — 複製/導出。`rule`: `"copy:<parent>"` | `"expr:<式>"`。
7. `date_offset` — 日付を基準列＋オフセットで生成。`base`: `<parent date col>`、`offset_days`: 分布（`from_source` の場合は実データの `(この日付 − base)` 日数分布を推定）。範囲・欠損も保持する。
8. `constant` / `passthrough` — 固定値、またはそのまま。

## タスク

1. **列を棚卸しし DAG 構造（親子関係）を宣言する**: 全対象列を洗い出し、業務的な依存（部位×病期/悪性度、部位特異マーカー、日付の前後、予後の勾配など）を親子エッジとして表現する。
2. **各ノードにモデル型を割当てる**: 上記モデル型（`marginal_*` / `cpt` / `conditional_numeric` / `presence_gate` / `deterministic` / `date_offset` / `constant`）から適切なものを選ぶ。
3. **`estimate:"from_source"` のパラメータ推定方針を決める**: バックオフ規則（`min_count`）、高カーディナリティ親の集約（`collapse_top`）、欠損の扱い（欠損も一状態として保持し、条件依存があれば残す）を明記する。
4. **`work/dependency_graph.json`（必要なら `dependency_params.json`）を出力する**。
5. **必須制約を DAG 構造で保証する設計にする**: PK/FK、値域、重複防止、日付の前後関係などが、ノードの親子関係とモデル型の組み合わせで自然に満たされるように設計する（post sampling に頼らないことを優先し、やむを得ない場合のみ post sampling を明記する）。

## ルール

- 生成ロジックは説明可能であること。
- 実データの特定レコードを再現しないこと。
- サンプルデータの分布を過度にコピーしないこと（`from_source` はバックオフ・集約を経た統計量に限る）。
- 乱数 seed により再現可能にすること。
- 仕様が不明な依存は、親を持たない保守的なモデル型（`marginal_*`）を選ぶ。

## Acceptance Criteria

- `work/dependency_graph.json` が生成され、有効な DAG（非巡回）であること。
- 対象となる全列がノード化されていること。
- 各ノードにモデル型（`model.type`）が割当てられていること。
- `parents` からトポロジカルな生成順が一意に導出可能であること（`generation_order` が省略される場合も含む）。
- 既知の依存関係（例: 部位×病期/悪性度、部位特異マーカー、日付オフセット、予後の勾配）がエッジとして表現されていること。

## 参考

後続の `generate` は `work/dependency_graph.json` を読み、トポロジカル順の条件付き生成器にコンパイルする。
dependency_graph.json スキーマの正本は本 SKILL.md の「dependency_graph.json のスキーマ」節とする。
依存関係を宣言しない従来の線形設計は `generation-design` を使う。
