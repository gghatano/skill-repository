# 開発ワークフローの規約（汎用知見）

Issue を作業単位に、branch / worktree / 実装 / 検証 / レビュー / PR を一貫管理する
開発フローの共通規約。`.claude/skills/` の dev 系スキルはこの規約を前提に、具体的な
コマンド・パス・ドキュメントを**役割名**で参照する。別プロジェクトへ移植するときは、
下表の既定値だけを自プロジェクトに合わせて読み替えれば、スキル本文の編集は不要。

## 1. 検証コマンド（役割 → 既定コマンド）

スキルは「検証を通す」を役割で参照する。プロジェクトの実際のコマンドに読み替える
（無い役割は対象外）。

| 役割 | 既定コマンド（例） | 説明 |
| --- | --- | --- |
| format | `uv run ruff format --check .` | 整形チェック（自動修正は `ruff format .`） |
| lint | `uv run ruff check .` | 静的解析 |
| typecheck | `uv run mypy <package>` | 型チェック |
| test | `uv run pytest -q` | 単体テスト |
| build / 再現性 | `make build` 等 | 生成物を再生成し、再現性を確認するスモーク |

「**全検証を通す**」= 上記のうちプロジェクトに存在するものを通しで実行し、出力を控える
こと。生成物（ビルド出力）は手編集せず、必ずジェネレータ経由で再生成する。

## 2. ブランチ・worktree 方針

| 項目 | 既定 | 備考 |
| --- | --- | --- |
| 既定ブランチ | `develop`（無ければ `main`） | 直下では実装しない |
| branch 命名 | `issue/<n>-<slug>` | 1 Issue = 1 branch |
| worktree パス | `../worktrees/<repo>-issue-<n>` | 1 worktree = 1 Issue |

原則: **1 Issue = 1 branch = 1 worktree = 原則 1 PR**。詳細・コマンド例・既知の落とし穴
（スタック PR の親ブランチ削除など）はプロジェクトの**ブランチ方針**（既定
`docs/branch-worktree-policy.md`）に置く。

## 3. 参照ドキュメント（役割 → 既定パス）

| 役割 | 既定パス | 用途 |
| --- | --- | --- |
| 仕様書 | `docs/SPEC.md` | 唯一の正。実装・レビューの基準 |
| 実装計画 | `docs/implementation-plan.md` | Issue 候補一覧（起票前の計画） |
| レビュー基準 | `docs/review-checklist.md` | code-review の観点 |
| 受け入れ基準 | `docs/acceptance-criteria.md` | PR 前の充足確認 |
| Issue 運用 | `docs/issue-management.md` 等 | 進捗コメントのフォーマット |
| 粒度ガイド | `docs/task-granularity-guide.md` | Issue 分割の粒度 |

これらが無いプロジェクトでは、該当役割を「対象外」とするか、同等の運用に読み替える。

## 4. サブエージェント（同梱物・degrade 可能）

dev 系スキルは `code-reviewer` / `security-reviewer` / `spec-analyst` / `implementation-planner`
等のサブエージェントに委譲することがある。これらは移植先へ一緒にコピーする**同梱物**だが、
無い環境では**通常のサブエージェント（またはスキル呼び出し元自身）**でレビュー・分析を
行ってよい。プロジェクト固有のエージェント（フロント/バックエンド実装担当など）は
そのプロジェクトの `.claude/agents/` に置き、本バンドルには含めない。
