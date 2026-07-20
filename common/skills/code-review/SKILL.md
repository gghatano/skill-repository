---
name: code-review
description: 実装差分を docs/review-checklist.md に沿ってレビューする手順。実装完了前に必ず使う。
---

# Code Review Workflow

> レビュー観点・参照ドキュメントは規約 `.claude/docs/dev-workflow-conventions.md` の役割に
> 従う（レビュー基準の既定は `docs/review-checklist.md`）。別プロジェクトでは基準ファイルと
> 「プロジェクト固有の観点」を自プロジェクトのものに読み替える。

1. レビュー対象の差分を取得する（`git diff` / `git diff --staged`）
2. **レビュー基準**（規約 §3。既定 `docs/review-checklist.md`）の各観点で評価する:
   仕様適合性 / 設計整合性 / 品質 / セキュリティ / 保守性
3. **プロジェクト固有の観点**を必ず確認する（そのプロジェクトの不変条件。例:
   純関数性・生成物を手編集していないか・シード固定＝再現性・依存方針・核となる設計契約）
4. 指摘は深刻度（blocker / major / minor / nit）と該当 `file:line` を添えて列挙する
5. 推測でなく根拠（コード引用・再現手順）を示す
6. レビュアーは**コードを直さない**。指摘のみ返す（修正は実装担当の責務）

## 出力フォーマット

```
## サマリ
（承認可否と理由を 1〜2 行）

## 指摘
- [blocker] file:line — 何が問題か / なぜ / 期待される修正
- [minor]   file:line — ...
```
