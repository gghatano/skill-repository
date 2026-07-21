# 仕様駆動 生成・評価サイクルの規約（汎用フレームワーク）

「仕様から成果物を作り、評価して直す」を段階的に進める汎用サイクル。特定の領域
（合成データ・文書・設定など）に依存しない**骨格**と、領域ごとの**プロファイル**（各
フェーズの中身）を分けて考える。`.claude/skills/` の生成系スキルはこの骨格に沿う。

## 骨格（フェーズ）

```
generation-cycle（オーケストレーター）
 ├ input-prepare    入力整備   原資料 → 後続が読める入力を整える
 ├ spec-ingest      仕様化     入力 → 機械可読な仕様（schema・制約）
 ├ generation-design 生成設計  仕様 → 生成方式の設計（方式は領域プロファイルで選ぶ）
 ├ generate         生成実装   設計 → 生成器の実装・実行
 └ evaluate-refine  評価・改善 成果物 → 仕様・サンプルに照らして評価し、必要なら再生成
```

各フェーズは前段の出力を入力に取り、`generation-cycle`（PM）が Acceptance Criteria の
充足を確認しながら順次進める。改善ループ（生成 → 評価 → 再生成）の打ち切り判断も PM が持つ。

## この骨格は他系統と共通

「仕様 → 設計/計画 → 実装/実行 → 評価/レビュー → 反復」は、生成に限らない汎用パターン。
本リポジトリの他バンドルも同じ骨格の別プロファイルにあたる。

| 系統 | 仕様 | 設計/計画 | 実装/実行 | 評価/レビュー |
| --- | --- | --- | --- | --- |
| 生成（本サイクル） | spec-ingest | generation-design | generate | evaluate-refine |
| 開発（dev） | 仕様書(SPEC) | issue-triage | spec-implementation | code-review / test-fix-loop |
| 研究（research） | report-skeleton | experiment-plan | experiment-run | report-review |

## プロファイル（領域ごとの中身）

骨格は共通で、各フェーズの**中身**が領域で変わる。現在の正本は **合成データ プロファイル**:

| フェーズ | 合成データ プロファイルでの中身 |
| --- | --- |
| input-prepare | 原データ・仕様書から table_definition / sample_data / data_spec / constraints を整える |
| spec-ingest | 列型・分布・列間関係・制約を推定して schema・constraint を機械可読化 |
| generation-design | 生成方式を選ぶ（**ルール・統計分布・モデル(CTGAN 等)・差分プライバシー**） |
| generate | 生成器を実装・実行し、合成データを出力 |
| evaluate-refine | 忠実性（分布の一致）・有用性（下流タスク=TSTR）・プライバシー（MIA 等）で評価 |

別の領域（文書生成・設定生成など）を扱うときは、同じ骨格・同じスキル名のまま、各フェーズの
中身を差し替えたプロファイルを用意すればよい。

## パス（タスク相対）

生成系スキルはタスクディレクトリ（`$ARGUMENTS`）配下を読み書きする。既定レイアウト:
`input/`（整形済み入力）・`work/`（中間生成物）・`output/`（成果物）・`src/`（生成器・評価器）。
別プロジェクトではタスクディレクトリの構成に読み替える。
