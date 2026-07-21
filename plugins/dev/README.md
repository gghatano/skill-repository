# dev — 開発ワークフロー（Git / Issue / PR）

GitHub Issue を作業単位に、branch / worktree / 実装 / 検証 / レビュー / PR を一貫管理する開発フローのスキル群。どのリポジトリ種別にも適用できる汎用ワークフローです。

## 導入

```
/plugin marketplace add gghatano/skill-repository
/plugin install dev@gghatano-skills
```

スキルは `/dev:<skill-name>`（例: `/dev:code-review`）で呼び出せます。

## 導入後の調整

`docs/dev-workflow-conventions.md` の §1 検証コマンド・§2 ブランチ方針・§3 参照ドキュメントを、対象リポジトリの実際のコマンド・パスに合わせて調整してください。`code-reviewer` / `security-reviewer` 等のサブエージェントを使う場合は、そのプロジェクトの `.claude/agents/` に用意してください（無ければ通常のレビューで代替されます）。

## 含まれるスキル

issue-driven-development / issue-triage / worktree-task-runner / spec-implementation / test-fix-loop / refactor-safely / code-review / pr-prep / pr-from-issue
