---
name: municipality-collaboration-scenario
description: "Use when Claude needs to read an existing ppdp-demo company data project (data_design.md, analysis_report.md) and generate concrete scenarios for combining that company's synthetic data with municipal government datasets (住民基本台帳, 課税所得, 福祉給付, 公共施設, 交通インフラ etc.). Produces a collaboration scenario document, data-generation scripts, analysis scripts, and a collaboration analysis report under the company's data_projects directory."
---

# Municipality Collaboration Scenario

Read the canonical skill at `.agents/skills/municipality-collaboration-scenario/SKILL.md` and follow it.

The canonical skill (v5) includes:

- ステージ④ positioning (non-invasive: do not touch ステージ②③)
- Correlated municipality master generation rules (MANDATORY) with explicit correlation bounds
- Industry-specific apportionment logic guide
- Extended column catalog (tourism_visitors_annual, inbound_foreign_visitors, etc.)
- IT/SaaS industry use-case catalog (S1–S5)
- Municipality count recommendations (demo: 100 / 都道府県代表: 47 / 本格: 1741)
- Workflow, output layout, standard schema, use-case catalog, acceptance criteria

## v3 改善点サマリー

### 相関許容範囲の明示（v2からの主な変更）

v2では相関係数が目標値より強すぎる問題（r≒0.95〜0.99）が発生していた。v3では許容範囲を明示し、生成後チェックを義務化した:

| 相関ペア | v3許容範囲 |
|---------|----------|
| 高齢化率 × 財政力 | -0.65 ≤ r ≤ -0.20 |
| 財政力 × 課税所得 | +0.50 ≤ r ≤ +0.80 |
| キャッシュレス率 × デジタル化率 | +0.35 ≤ r ≤ +0.70 |

### IT/SaaS業種ユースケースカタログの追加

S1〜S5のシナリオカタログとIT予算・オンライン手続き率・統合基幹業務システムフラグの業種拡張カラムを追加。

### 活用先3種の必須化

各シナリオの「活用先」に自治体担当部署名・企業部門名・政策立案機関名の3種を必ず記載すること。「自治体」「営業部門」のみの記載は不可。

## v7 改善点サマリー（v6からの変更）

### Windows環境エンコーディング対策を必須化

ANA実行時に発生したハマりポイントをスキルに明記:

1. **CSV書き出し**: `encoding='utf-8-sig'` を必ず指定
2. **stdout UTF-8固定**: `analyze_collaboration.py` 冒頭に `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')` を必ず記述
3. **Unicode文字禁止**: `≈` `→` `×` 等のUnicode特殊記号はcp932でエラーになるため使用禁止。`~=` `->` `x` 等のASCII代替を使う

## v5 改善点サマリー（v4からの変更）

3社レビュー（ANA・GMO・かんぽ）の結果を踏まえ、以下を強化:

### 「活用先」「分析仮説」の記載要件を強化
- 既存シナリオ更新時も「活用先」3種（自治体部署・企業部門・政策機関）の存在を必ず確認・補完
- 「分析仮説」には期待r値・差分値等の数値根拠を必須化
- 参考事例で同一PDFの重複引用を禁止

## v4 改善点サマリー

### 各シナリオへの「参考事例」セクション追加

各シナリオの末尾に実在する公開事例のURL・名称を2〜4件併記するルールを追加。
以下3つのナレッジソースを優先順位付きで参照する:
1. `docs/success_cases_master_list.md`（官民55件、A/B/C位置づけ付き）
2. `docs/success_cases_public_private_data.md`（詳細版7件）
3. https://github.com/pwscup/pets-usecase-catalog（PETs技術実装事例）

架空URLは禁止。位置づけB/C事例には「※成果の詳細は確認中」を付記すること。

## 最終ステップ: HTML変換

```powershell
uv run python tools/build_html.py
```
