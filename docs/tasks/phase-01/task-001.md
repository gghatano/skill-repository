# Task 001: GitHub 上の Claude Skills を継続的に集約する

## 背景

`gghatano` が所有する複数の GitHub リポジトリに `.claude` が配置され、プロジェクト
ごとのスキルが分散している。利用可能なスキルと用途を横断的に把握しづらく、新規
追加や更新の見落としが発生する。

## 提供価値

- 利用者が、所有リポジトリに存在するスキルと用途を一つの一覧から把握できる
- 保守者が、定期同期によって追加・更新・削除を継続的に反映できる
- 各スキルの出典と同期元 SHA を追跡できる

## スコープ

- `gghatano` 所有リポジトリの列挙
- `.claude/skills/**/SKILL.md` の探索
- `SKILL.md` と同一スキルディレクトリ配下のファイルの集約
- frontmatter の `name` と `description` を使った一覧生成
- GitHub Actions による週次・手動同期 PR
- 選定・移植情報を確認できる HTML カタログと GitHub Pages 配信
- 認証エラーや API エラー時の既存生成物保護

## スコープ外

- スキル本文の自動編集、品質評価、重複統合
- `.claude/commands`、`.claude/agents` の集約
- 出典リポジトリへのスキルの逆同期

## 成功条件

- 対象リポジトリの各スキルが `skills/<repository>/` に同期される
- 一覧に名称、説明、出典リンクが表示される
- HTML で同梱物、依存ツール、固有パス、同名バリエーション、配置方法を確認できる
- 同期元に変更がなければ tracked file に差分が生じない
- 途中失敗時に既存の同期結果が変更されない
- fixture を使ったテストが GitHub 認証なしで通る

## 運用

原則として週次 Actions が同期 PR を作成する。新規スキルをすぐ反映したい場合は
workflow_dispatch を実行する。private repository を含める場合は
`SKILL_SOURCE_TOKEN` を設定する。
