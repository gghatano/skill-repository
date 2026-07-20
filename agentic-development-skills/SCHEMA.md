# SKILL.md 標準スキーマ

すべての Skill は同じ形式を持つ。これにより Skill を **交換可能な部品**として扱え、
Workflow から機械的に組み合わせられる。

## 設計上の制約

- **Frontmatter は最小限**（`name` + `description` のみ）。Claude Code など `SKILL.md` を
  そのまま読む環境で invoke できるようにするため、標準インターフェースは **本文の見出し**として
  持つ（frontmatter を拡張しない）。
- Skill 本体に **特定エージェント製品の API を書かない**。実行方法は `adapters/` に分離する。
- Skill 本体に **プロジェクト固有のパス・ドメイン知識を書かない**。それらは Project Spec 側。

## Frontmatter

```yaml
---
name: <skill-id>            # ディレクトリ名と一致。kebab-case
description: <いつ使うか＋何をするか>   # 製品非依存・1〜3 文。トリガー条件を含める
---
```

## 本文セクション（この順序・見出しで統一）

````markdown
# <Skill 名>（<一行の目的>）

一行〜数行で目的を述べる。

## Inputs
Skill が受け取る成果物・情報。`- name: 型/出典` 形式。

## Outputs
Skill が生成する成果物。ファイル名を明示する（成果物駆動）。

## Preconditions
実行前に満たすべき条件。満たさない場合は `failure_handling` へ。

## Procedure
基本ループ（ASCII 図）と手順。**この Skill がやらないこと**も明記する。

## Validation
生成した成果物の検証方法。可能なら機械的検証を優先で並べる。

## Stop conditions
Skill を正常終了する条件（`max_iterations` など数値化できるものは数値で）。

## Failure handling
失敗時の処理。次のいずれかへ分類する:
- **Retry** … 同じ手順を再試行
- **Escalate** … 人間 or 上位 Workflow に判断を委ねる
- **Rollback** … 変更を戻す
- **Request additional investigation** … `explore` 系へ差し戻す

## Adapter notes
Claude Code / Codex / Generic での実行方法の要点（詳細は `adapters/`）。

## Derived skills
（Core のみ・任意）この作業パターンの特化版。
````

## 命名規約

- Skill id は動詞（作業パターン）: `explore` `plan` `implement` `test` `review` `fix` `verify` `integrate`。
- 役割名（`frontend-agent` 等）は禁止。
- Composite Skill は「Core をどう回すか」を表す名前: `test-and-fix` `review-and-fix` `independent-review`。

## 成果物の受け渡し規約

Skill 間は自然言語ではなく **成果物ファイル**で受け渡す。標準ファイル名:

| 成果物 | ファイル名 | 生成 Skill |
| --- | --- | --- |
| 要件定義 | `spec.md` | （Project Spec / 人間） |
| 調査結果 | `research.md` | `explore` |
| 実装計画 | `plan.md` | `plan` |
| 変更差分 | （リポジトリの diff） | `implement` / `fix` |
| テスト結果 | `test-results.json` | `test` |
| レビュー結果 | `review.md` | `review` |
| 統合結果 | `integration.md` | `integrate` |
| 最終検証 | `verification.md` | `verify` |
