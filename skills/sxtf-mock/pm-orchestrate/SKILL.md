---
name: pm-orchestrate
description: sxtf-mock を無人で前進させる PM オーケストレーション手順。未決Issueを仮置きで解決しつつ、サブエージェントを束ねて基盤〜画面〜検証まで実装し、develop まで自動マージする。サブエージェントを定期監視し、スタックしたら自動リトライ→再割当→skip で前進する。ユーザーが「自律的に動いてほしい」「PMとしてissueを順次解決」「10時間自律」「サブエージェントを監視して進めて」等を述べたら、明示的に "skill" と言われなくても必ずこのスキルを使うこと。
---

# pm-orchestrate

sxtf-mock を**無人でPM運転**するための手順。ルールの実体は `.claude/knowledge/autonomous-run-playbook.md`（必ず先に読む）。

## 起動前チェック

1. `autonomous-run-playbook.md` を読む（運転パラメータ・ガードレール・仮置きポリシー・フェーズ計画・停止条件）。
2. `docs/ROADMAP.md` と `gh issue list` で現在地・残Issueを把握。
3. `.claude/knowledge/` 5本（契約）と `CLAUDE.md`（作法）、SKILL `add-mock-screen` を前提として確認。
4. **人間側前提**：許可プロンプトが出ない権限モードが有効か（無人運転の必須条件）。未確認なら起動前に人間へ確認。

## 運転手順

### 1. P0 残区A確定（仮置き）
playbook の仮置き既定値（#2/#8/#18/#23）を契約（`.claude/knowledge/`）へ反映し、各Issueに `【仮決定 (autonomous run)】` をコメント。可逆性を保つ。

### 2. オーケストレーション・エンジン
**Workflow ツール**でフェーズ・パイプラインを組む（バックグラウンド実行・並列・検証ゲート・resume）。フェーズ順は playbook（P0→P1基盤凍結→P2→P3並列→P4統合検証）。**P1完了までP3を起動しない**（依存ゲート）。worktree 隔離で並列し、契約ファイルには触れさせない。

### 3. サブエージェントへの指示
各画面タスクは `add-mock-screen` の手順に従わせ、担当パス・機能No・DoD・ブランチ（`feat/T<n>-<slug>`）を明示（テンプレは `.claude/knowledge/dev-workflow.md`）。実装系はモデルを品質寄りに。

### 4. 監視・スタック対応
`TaskList`/`TaskOutput` で進捗監視。無進捗30分超 or タイムボックス超過で「指示送信→停止して再spawn→2回失敗で skip＋記録」。止まらず前進。

### 5. 検証ゲート（品質優先）
各タスク DoD 必須。P4 で敵対的レビュー（契約/スコープ逸脱・No.4/No.9 成立・限界注記）。NG は修正タスクへ差し戻し。

### 6. ログ・節目要約
`.claude/run-journal.md` にフェーズ要約・仮決定・スタック対応・skip・コスト概況を追記。`.claude/progress.md` にタスク1行。

### 7. 停止・総括
playbook の停止条件で停止し、達成/未達/skip/要人間判断/develop状態/次の一手を総括。

## 厳守（ガードレール再掲）

- `main` 直接禁止（develop 止まり）。契約変更は仮置き＋Issue記録、重大論点は skip＋`要人間判断`。
- スコープ厳守（現物真正性スコープ外・検証は拡張フックのみ・実暗号禁止）。
- DoD 未達を develop へマージしない。既存決定を勝手に覆さない。
