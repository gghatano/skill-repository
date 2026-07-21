# generation — 仕様駆動 生成・評価サイクル

仕様から成果物を作り、評価して直す汎用サイクル（input-prepare → spec-ingest → generation-design → generate → evaluate-refine）。骨格は領域非依存で、現在の中身は合成データ生成プロファイル（ルール/統計/モデル/差分プライバシーの生成方式、忠実性・有用性・プライバシーの評価）です。

## 導入

```
/plugin marketplace add gghatano/skill-repository
/plugin install generation@gghatano-skills
```

スキルは `/generation:<skill-name>`（例: `/generation:generate`）で呼び出せます。

## 導入後の調整

汎用の生成・評価サイクルです。骨格（フェーズ）は領域非依存で、`docs/generation-cycle-conventions.md` にプロファイルの考え方をまとめています。各スキルはタスクディレクトリ（`$ARGUMENTS`）配下の `input/ work/ output/ src/` を読み書きします。別の生成領域を扱うときは、骨格・スキル名はそのままに、各フェーズの中身を差し替えたプロファイルを用意してください。

## 含まれるスキル

generation-cycle / input-prepare / spec-ingest / generation-design / generate / evaluate-refine
