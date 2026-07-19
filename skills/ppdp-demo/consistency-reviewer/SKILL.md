---
name: consistency-reviewer
description: "Use when Claude needs to review cross-artifact consistency of a ppdp-demo company project that uses the multi-use-case model: checks that use_cases.md, org_data_master.md, the mapping diagram (build_mapping.py / figures), and analysis_scenarios.md agree on IDs (UC/ORG/DS), categories, 実在/仮説 labels, and synthetic-demo notes. Produces a structured pass/warn/fail review report so a PM does not have to verify consistency by hand."
---

# Consistency Reviewer

Read the canonical skill at `.agents/skills/consistency-reviewer/SKILL.md` and follow it.

このスキルは、複数ユースケースモデルで作られた企業プロジェクト
（`use_cases.md` / `org_data_master.md` / `build_mapping.py` / `analysis_scenarios.md`）の
**横断整合性**をレビューし、`output/consistency_review.md` に構造化レポートを出力する。
PMが手作業で整合性確認する負担を減らすのが目的。アーティファクト自体は書き換えない。

## チェック基準（概要）

| # | 基準 | 合格条件 |
|---|------|---------|
| C1 | ID規約の整合 | UC/ORG/DS が `*-<nn>-NNN` 形式・企業番号一致 |
| C2 | データID整合 | use_cases の DS-ID が master 表2に存在・双方向一致 |
| C3 | 組織ID整合 | use_cases の関係組織が master 表1に対応 |
| C4 | カテゴリ／区分 | UC/DS/ORG のカテゴリが矛盾しない |
| C5 | マッピング図整合 | build_mapping.py の埋め込みデータが master と一致 |
| C6 | 分析シナリオ整合 | scenarios の DS-ID・対象UC・実在/仮説が master と一致 |
| C7 | 合成・仮想注記 | 各成果物の冒頭に合成デモ注記 |
| C8 | 実在性・制約の一貫性 | master の実在/仮説が use_cases と矛盾しない |
| C9 | 旧版記述の不在 | 「暫定」「旧→新対応表」等の移行記述が残っていない |

## 総合判定
- `fail` 1件以上 → ❌ 不整合あり（要修正）
- `warn` 3件以上 → ⚠️ 要修正
- `warn` 2件以下 → ✅ 合格
