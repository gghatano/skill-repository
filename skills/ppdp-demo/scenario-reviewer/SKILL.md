---
name: scenario-reviewer
description: "Use when Claude needs to review a municipality_collaboration_scenario.md file in ppdp-demo to check quality, completeness, and compliance with v4 skill standards. Reviews 参考事例 URLs, データ実在性 notes, 他社データ制約 warnings, 活用先 completeness, and hypothesis quality. Produces a structured review report with pass/fail per criterion and improvement suggestions."
---

# Scenario Reviewer

Read the canonical skill at `.agents/skills/scenario-reviewer/SKILL.md` and follow it.

このスキルは `municipality_collaboration_scenario.md` を7基準でレビューし、
`docs/review_report_<company_short>.md` として構造化レポートを出力する。

## チェック基準（概要）

| # | 基準 | 合格条件 |
|---|------|---------|
| C1 | 参考事例セクションの存在 | 各シナリオに2件以上のURL |
| C2 | URLの実在性 | success_cases_master_list.md 掲載またはgo.jp/lg.jp |
| C3 | B/C事例への注記 | 「※成果の詳細は確認中」が付記されている |
| C4 | データ実在性コメント | 主要カラムにオープンデータ対応言及あり |
| C5 | 他社データ制約注記 | 懸念度「高」カラムに制約注記あり |
| C6 | 活用先の完全性 | 自治体部署・企業部門・政策機関の3種 |
| C7 | 分析仮説の具体性 | 因果仮説＋数値的根拠 |

## 総合判定
- `fail` 1件以上 → ❌ 再作成推奨
- `warn` 3件以上 → ⚠️ 要修正
- `warn` 2件以下 → ✅ 合格
