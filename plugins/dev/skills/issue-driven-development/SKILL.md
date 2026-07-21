---
name: issue-driven-development
description: GitHub Issue を作業単位として branch/worktree/PR/検証記録を一貫管理する。実装作業を始めるときに必ず使う。
---

# Issue Driven Development

> コマンド・パス・ブランチ・参照ドキュメントは規約 `.claude/docs/dev-workflow-conventions.md`
> の役割に従う（既定値はそのまま例示）。別プロジェクトでは §1 検証コマンド・§2 ブランチ方針・
> §3 参照ドキュメントを読み替える。サブエージェント（code-reviewer 等）が無ければ通常の
> レビューで代替してよい。

すべての実装作業を GitHub Issue 単位で管理する。
Issue 本文を Claude Code への**作業指示書**として扱う。

## 原則
- 1 Issue = 1 branch = 1 worktree = 原則 1 PR
- Issue 未作成の実装に着手しない
- Issue 本文（スコープ）にない作業を勝手に実装しない
- 非スコープに書かれた内容を実装しない
- スコープ外の発見事項は実装せず、Issue コメントまたは別 Issue 候補として記録する
- 検証していない内容を完了と主張しない
- 作業完了時は Issue と PR の双方に検証結果を残す

## 作業開始
1. Issue 番号を確認する
2. `gh issue view <n> --comments` で本文とコメントを読む
3. 背景 / 対象仕様 / スコープ / 非スコープ / 完了条件 / 検証方法 を読み取り要約する
4. 現在の branch / worktree がその Issue 専用であることを確認する
   （branch-worktree-policy.md。`issue/<n>-<slug>` / `../worktrees/<repo>-issue-<n>`）
5. 実装方針を 3〜5 行で整理する

## 実装
1. 関連ファイルを確認し、既存パターンに合わせて実装する（spec-implementation SKILL）
2. 必要なテストを `tests/` に追加・更新する
3. 仕様にない拡張をしない

## 検証（規約 §1 検証コマンドに従う。既定例）
1. `uv run ruff format --check .`（format）
2. `uv run ruff check .`（lint）
3. `uv run mypy <package>`（typecheck）
4. `uv run pytest -q`（test）
5. `make build` 等（build / 再現性スモーク）

プロジェクトに存在する検証を通しで実行し、実行できないものは理由を記録する。

## レビュー
1. code-reviewer でレビューする
2. セキュリティ影響（入力・依存・テンプレ出力・隔離前提）があれば security-reviewer も
3. 指摘を修正し、再検証する

## 完了
1. PR を作成する（pr-from-issue SKILL）。PR 本文に Issue 番号・変更・検証結果・レビュー観点
2. Issue へ進捗コメントを残す（issue-management.md の Progress Update フォーマット）
3. PR と Issue を相互リンクし、未対応事項・スコープ外発見を明記する
