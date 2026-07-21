# research — 研究レポート作成ライフサイクル

実験レポートの骨子設計から実験の計画・実行、レビュー、公開までを一式で進める研究リポジトリ向けのスキル群。役割ベースのスキル本体・規約（`docs/`）・サブエージェント（`agents/`）を同梱しています。

## 導入

```
/plugin marketplace add gghatano/skill-repository
/plugin install research@gghatano-skills
```

スキルは `/research:<skill-name>`（例: `/research:report-review`）で呼び出せます。`agents/` の planner / implementer / reviewer もサブエージェントとして利用できます。

## 導入後の調整

`docs/documentation-conventions.md` の §1「パスの読み替え（役割→既定パス）」表を、対象リポジトリの実際のレイアウトに合わせて調整してください。役割ベースのスキル本体は編集不要です。

`writing` プラグインの `stop-ai-slop-jp` を併せて導入していると、`report-review` が自動で連携します。

## 含まれるスキル

research-cycle / report-skeleton / experiment-plan / experiment-run / doc-cycle / report-review / repro-engineering-review / related-info-review / publish-check
