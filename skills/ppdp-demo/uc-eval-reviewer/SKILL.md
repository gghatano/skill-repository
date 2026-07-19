---
name: uc-eval-reviewer
description: "Use when Claude needs to review the UC評価 (実現容易性 × インパクト) section that stage ③ (uc-quickwin-evaluator) inserted at the top of a ppdp-demo company use_cases.md, before stage ④ synthesis/analysis: checks 実現容易性 rationale, インパクト completeness (no placeholders/TODO), Quick Win 判定妥当性, 代表分析可能性, ラベル語彙, トーン, 配置 against docs/uc_evaluation_framework.md. When C1 fail (upward adjustment) is detected, immediately corrects input/use_cases.md to the machine-computed value and records the before/after in the report."
---

# UC Eval Reviewer

正本は `.agents/skills/uc-eval-reviewer/SKILL.md`。それを読んで従うこと。
