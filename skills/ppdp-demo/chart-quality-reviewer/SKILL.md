---
name: chart-quality-reviewer
description: "Use when asked to detect or fix rendering issues in charts/figures across ppdp-demo company projects. Runs static code analysis (check_chart_quality.py) and PNG image analysis (check_image_quality.py), interprets results, and reports actionable findings — covering label squish, heatmap whitespace, legend clipping, duplicate images, and X-axis bias."
---

# Chart Quality Reviewer

Read the canonical skill at `.agents/skills/chart-quality-reviewer/SKILL.md` and follow it.

このスキルは ppdp-demo 企業プロジェクトのグラフ・図品質問題を静的コード解析 + PNG 画像解析で
検出・報告する。修正が自明なものはその場で修正する。

## 使用ツール
- `tools/check_chart_quality.py` — analyze*.py のコードを静的解析（P1〜P5）
- `tools/check_image_quality.py` — output/figures/*.png を Pillow で解析（I1〜I2）

## 検出パターン（概要）

| コード | 深刻度 | 内容 |
|--------|--------|------|
| P1 | ERROR | Period型インデックスのまま bar plot → X軸ラベルずれ |
| P2 | WARN | 棒グラフで rotation 未設定 → ラベル重なり |
| P3 | WARN | figsize が小さすぎる棒グラフ |
| P4 | WARN | bbox_to_anchor + tight_layout なし → 凡例切れ |
| P5 | WARN | ヒートマップで bbox_inches='tight' なし → 余白大 |
| I1 | WARN | 異なる UC 間で近似重複画像（流用バグ） |
| I2 | WARN | X方向コンテンツ偏り ratio > 10x（ラベルズレ疑い） |
