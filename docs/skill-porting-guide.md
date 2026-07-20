# Skill Porting Guide（移植ガイド）

GitHub account `gghatano` のスキルを別プロジェクトへ持ち運ぶときに、解決が必要な外部前提をスキルごとにまとめた自動生成のチェックリストです。
このファイルは直接編集せず、`python3 scripts/sync_skills.py` で更新してください。

## 移植のしやすさ（tier）

- **そのまま (portable)**: 同梱物とパラメータ化済みパスのみ。フォルダをコピーすればほぼ動く。
- **同梱前提 (companions)**: `.claude/` `.agents/` などの兄弟ファイル（エージェント・知識）を一緒にコピーする必要がある。
- **要調整 (rework)**: 特定プロジェクトの具体パスを前提にしており、コピー先に合わせて読み替え・調整が必要。

| Tier | 件数 |
| --- | --- |
| そのまま (portable) | 16 |
| 同梱前提 (companions) | 18 |
| 要調整 (rework) | 57 |

## 要調整（57）

コピー先の構成に合わせて、以下のパスを読み替える必要があります。

### `0_input_prepare` — `pets-seminar-01`

[SKILL.md](https://github.com/gghatano/pets-seminar-01/blob/main/.claude/skills/0_input_prepare/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `examples/university_enrollment`, `source/raw_data/`, `source/table_definitions/`, `source/docs/`, `source/notes/`
- 参考（パラメータ化済み・調整不要）: `$ARGUMENTS/source/`, `$ARGUMENTS/input/`, `$ARGUMENTS/input/table_definition.csv`

### `1_spec_ingest` — `pets-seminar-01`

[SKILL.md](https://github.com/gghatano/pets-seminar-01/blob/main/.claude/skills/1_spec_ingest/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `examples/university_enrollment`, `input/table_definition.csv`, `input/sample_data.csv`
- **必要ツール**: Python, uv
- 参考（パラメータ化済み・調整不要）: `$ARGUMENTS/input/`, `input/*table_definition*`, `input/*sample_data*`, `input/<table>_table_definition.csv`, `input/<table>_sample_data.csv`

### `2_generation_plan` — `pets-seminar-01`

[SKILL.md](https://github.com/gghatano/pets-seminar-01/blob/main/.claude/skills/2_generation_plan/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `docs/spec.md`, `examples/customer/work/generation_plan.md`, `examples/customer_transactions/work/generation_plan.md`
- 参考（パラメータ化済み・調整不要）: `$ARGUMENTS/work/inferred_schema.json`, `$ARGUMENTS/work/constraint_plan.md`, `$ARGUMENTS/input/data_spec.md`, `$ARGUMENTS/input/*sample_data*`, `$ARGUMENTS/work/generation_plan.md`

### `3_generator_impl` — `pets-seminar-01`

[SKILL.md](https://github.com/gghatano/pets-seminar-01/blob/main/.claude/skills/3_generator_impl/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `examples/customer_transactions/src/generator.py`
- **必要ツール**: Python, uv
- 参考（パラメータ化済み・調整不要）: `$ARGUMENTS/work/generation_plan.md`, `$ARGUMENTS/work/inferred_schema.json`, `$ARGUMENTS/work/constraint_plan.md`, `$ARGUMENTS/input/*sample_data*`, `$ARGUMENTS/src/generator.py`, `$ARGUMENTS/output/synthetic_data.csv`, `$ARGUMENTS/output/<table>.csv`

### `add-asset` — `asset-management`

[SKILL.md](https://github.com/gghatano/asset-management/blob/develop/.claude/skills/add-asset/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `config/assets.yaml`, `config/initial_positions.yaml`, `config/monthly_purchases.yaml`, `docs/spec.md`, `src/fetch_prices.py`
- **必要ツール**: Python, uv
- 参考（パラメータ化済み・調整不要）: `feature/add-asset-<asset_id>`

### `add-mock-screen` — `sxtf-mock`

[SKILL.md](https://github.com/gghatano/sxtf-mock/blob/develop/.claude/skills/add-mock-screen/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `lib/types.ts`, `tests/e2e/`, `lib/mock-store.ts`
- **一緒にコピー（ハーネス同梱物）**: `.claude/knowledge/`, `.claude/knowledge/dev-workflow.md`, `.claude/progress.md`
- **必要ツール**: Claude Code, Git, npm
- 参考（パラメータ化済み・調整不要）: `app/<path>/page.tsx`, `feat/T<n>-<slug>`

### `case-create` — `privacy-incident-catalog`

[SKILL.md](https://github.com/gghatano/privacy-incident-catalog/blob/main/.claude/skills/case-create/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `src/constants/prompts.ts`, `src/constants/categories.ts`, `src/schemas/case.schema.ts`, `public/cases/`, `public/cases/index.json`
- 参考（パラメータ化済み・調整不要）: `public/cases/<id>/case.json`

### `case-enrich` — `privacy-incident-catalog`

[SKILL.md](https://github.com/gghatano/privacy-incident-catalog/blob/main/.claude/skills/case-enrich/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `src/constants/prompts.ts`

### `case-study` — `pets-seminar-01`

[SKILL.md](https://github.com/gghatano/pets-seminar-01/blob/main/.claude/skills/case-study/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `docs/stylesheets/extra.css`, `docs/references/README.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/skills/README.md`
- **必要ツール**: Claude Code, uv
- 参考（パラメータ化済み・調整不要）: `docs/<case>/`, `src/dummy_data/<case>.py`, `data/<case>/raw/*.csv`, `tests/test_<case>_dummy_data.py`, `notebooks/<case>.ipynb`

### `chart-quality-reviewer` — `ppdp-demo`

[SKILL.md](https://github.com/gghatano/ppdp-demo/blob/main/.claude/skills/chart-quality-reviewer/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `tools/check_chart_quality.py`, `tools/check_image_quality.py`
- **一緒にコピー（ハーネス同梱物）**: `.agents/skills/chart-quality-reviewer/SKILL.md`

### `consistency-reviewer` — `ppdp-demo`

[SKILL.md](https://github.com/gghatano/ppdp-demo/blob/main/.claude/skills/consistency-reviewer/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `output/consistency_review.md`
- **一緒にコピー（ハーネス同梱物）**: `.agents/skills/consistency-reviewer/SKILL.md`
- **必要ツール**: Claude Code

### `experiment-issue` — `202604-syntheticdata-survey`

[SKILL.md](https://github.com/gghatano/202604-syntheticdata-survey/blob/main/.claude/skills/experiment-issue/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `docs/templates/report_template.md`, `docs/review.md`
- **必要ツール**: GitHub CLI
- 参考（パラメータ化済み・調整不要）: `docs/report_{{NN}}_{{shortname}}.md`, `results/archive/<date>_exp{{NN}}/`

### `experiment-run` — `dpsynth-demo`

[SKILL.md](https://github.com/gghatano/dpsynth-demo/blob/main/.claude/skills/experiment-run/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `scripts/setup_env.sh`, `outputs/run_meta.json`, `scripts/10_experiments.py`, `content/engineering-notes.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/agents/implementer.md`, `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code, Git, Python, uv
- 参考（パラメータ化済み・調整不要）: `docs/plans/<ID>-<slug>.md`

### `experiment-run` — `synth-report-kit`

[SKILL.md](https://github.com/gghatano/synth-report-kit/blob/main/.claude/skills/experiment-run/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `outputs/run_meta.json`, `scripts/build_site.py`, `content/engineering.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/agents/implementer.md`, `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code, Git, Python, uv
- 参考（パラメータ化済み・調整不要）: `docs/plans/<ID>-<slug>.md`, `outputs/*_meta.json`, `scripts/<pkg>/`

### `experiment-run` — `tabular-sdg-skillset`

[SKILL.md](https://github.com/gghatano/tabular-sdg-skillset/blob/main/.claude/skills/experiment-run/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `scripts/setup_env.sh`, `outputs/run_meta.json`, `scripts/10_experiments.py`, `content/engineering-notes.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/agents/implementer.md`, `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code, Git, Python, uv
- 参考（パラメータ化済み・調整不要）: `docs/plans/<ID>-<slug>.md`

### `experiment-run` — `tpdp2026-binagg`

[SKILL.md](https://github.com/gghatano/tpdp2026-binagg/blob/main/.claude/skills/experiment-run/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `scripts/setup_env.sh`, `outputs/run_meta.json`, `scripts/10_experiments.py`, `content/engineering-notes.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/agents/implementer.md`, `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code, Git, Python, uv
- 参考（パラメータ化済み・調整不要）: `docs/plans/<ID>-<slug>.md`

### `experiment-run` — `tpdp2026-mst-aim-audit`

[SKILL.md](https://github.com/gghatano/tpdp2026-mst-aim-audit/blob/main/.claude/skills/experiment-run/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `scripts/setup_env.sh`, `outputs/run_meta.json`, `scripts/10_experiments.py`, `content/engineering-notes.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/agents/implementer.md`, `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code, Git, Python, uv
- 参考（パラメータ化済み・調整不要）: `docs/plans/<ID>-<slug>.md`

### `municipality-collaboration-scenario` — `ppdp-demo`

[SKILL.md](https://github.com/gghatano/ppdp-demo/blob/main/.claude/skills/municipality-collaboration-scenario/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `docs/success_cases_master_list.md`, `docs/success_cases_public_private_data.md`
- **一緒にコピー（ハーネス同梱物）**: `.agents/skills/municipality-collaboration-scenario/SKILL.md`
- **必要ツール**: Claude Code, Python, uv

### `pm-orchestrate` — `sxtf-mock`

[SKILL.md](https://github.com/gghatano/sxtf-mock/blob/develop/.claude/skills/pm-orchestrate/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `docs/ROADMAP.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/knowledge/autonomous-run-playbook.md`, `.claude/knowledge/`, `.claude/knowledge/dev-workflow.md`, `.claude/run-journal.md`, `.claude/progress.md`
- **必要ツール**: Claude Code, GitHub CLI
- 参考（パラメータ化済み・調整不要）: `feat/T<n>-<slug>`

### `publish-check` — `dpsynth-demo`

[SKILL.md](https://github.com/gghatano/dpsynth-demo/blob/main/.claude/skills/publish-check/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `scripts/03_build_html.py`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.github/workflows/deploy-pages.yml`
- **必要ツール**: Claude Code, Git, Python
- 参考（パラメータ化済み・調整不要）: `content/*.md`, `htmls/*.html`, `figures/*.png`, `content/<new>.md`

### `publish-check` — `pe-demo`

[SKILL.md](https://github.com/gghatano/pe-demo/blob/main/.claude/skills/publish-check/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `scripts/build_site.py`, `ark/build_html.py`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.github/workflows/deploy-pages.yml`
- **必要ツール**: Claude Code, Git, Python, uv
- 参考（パラメータ化済み・調整不要）: `content/*.md`, `htmls/*.html`, `figures/*.png`, `content/<new>.md`

### `publish-check` — `synth-report-kit`

[SKILL.md](https://github.com/gghatano/synth-report-kit/blob/main/.claude/skills/publish-check/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `scripts/build_site.py`, `ark/build_html.py`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.github/workflows/deploy-pages.yml`
- **必要ツール**: Claude Code, Git, Python, uv
- 参考（パラメータ化済み・調整不要）: `content/*.md`, `htmls/*.html`, `figures/*.png`, `content/<new>.md`

### `publish-check` — `tabular-sdg-skillset`

[SKILL.md](https://github.com/gghatano/tabular-sdg-skillset/blob/main/.claude/skills/publish-check/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `scripts/03_build_html.py`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.github/workflows/deploy-pages.yml`
- **必要ツール**: Claude Code, Git, Python
- 参考（パラメータ化済み・調整不要）: `content/*.md`, `htmls/*.html`, `figures/*.png`, `content/<new>.md`

### `publish-check` — `tpdp2026-binagg`

[SKILL.md](https://github.com/gghatano/tpdp2026-binagg/blob/main/.claude/skills/publish-check/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `scripts/03_build_html.py`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.github/workflows/deploy-pages.yml`
- **必要ツール**: Claude Code, Git, Python
- 参考（パラメータ化済み・調整不要）: `content/*.md`, `htmls/*.html`, `figures/*.png`, `content/<new>.md`

### `publish-check` — `tpdp2026-mst-aim-audit`

[SKILL.md](https://github.com/gghatano/tpdp2026-mst-aim-audit/blob/main/.claude/skills/publish-check/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `scripts/03_build_html.py`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.github/workflows/deploy-pages.yml`
- **必要ツール**: Claude Code, Git, Python
- 参考（パラメータ化済み・調整不要）: `content/*.md`, `htmls/*.html`, `figures/*.png`, `content/<new>.md`

### `related-info-review` — `dpsynth-demo`

[SKILL.md](https://github.com/gghatano/dpsynth-demo/blob/main/.claude/skills/related-info-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`
- 参考（パラメータ化済み・調整不要）: `content/method-*.md`

### `related-info-review` — `synth-report-kit`

[SKILL.md](https://github.com/gghatano/synth-report-kit/blob/main/.claude/skills/related-info-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`, `content/related-work.md`, `content/method.md`

### `related-info-review` — `tabular-sdg-skillset`

[SKILL.md](https://github.com/gghatano/tabular-sdg-skillset/blob/main/.claude/skills/related-info-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`
- 参考（パラメータ化済み・調整不要）: `content/method-*.md`

### `related-info-review` — `tpdp2026-binagg`

[SKILL.md](https://github.com/gghatano/tpdp2026-binagg/blob/main/.claude/skills/related-info-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`
- 参考（パラメータ化済み・調整不要）: `content/method-*.md`

### `related-info-review` — `tpdp2026-mst-aim-audit`

[SKILL.md](https://github.com/gghatano/tpdp2026-mst-aim-audit/blob/main/.claude/skills/related-info-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`
- 参考（パラメータ化済み・調整不要）: `content/method-*.md`

### `release` — `asset-management`

[SKILL.md](https://github.com/gghatano/asset-management/blob/develop/.claude/skills/release/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `docs/development.md`, `docs/spec.md`, `actions/deploy-pages`
- **必要ツール**: Git, GitHub CLI

### `report-review` — `dpsynth-demo`

[SKILL.md](https://github.com/gghatano/dpsynth-demo/blob/main/.claude/skills/report-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`, `content/EXPERIMENTS.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code
- 参考（パラメータ化済み・調整不要）: `content/method-*.md`

### `report-review` — `pe-demo`

[SKILL.md](https://github.com/gghatano/pe-demo/blob/main/.claude/skills/report-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`, `references/structures.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.claude/skills/stop-ai-slop-jp/`
- **必要ツール**: Claude Code
- 参考（パラメータ化済み・調整不要）: `content/*.md`

### `report-review` — `synth-report-kit`

[SKILL.md](https://github.com/gghatano/synth-report-kit/blob/main/.claude/skills/report-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`, `references/structures.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.claude/skills/stop-ai-slop-jp/`
- **必要ツール**: Claude Code
- 参考（パラメータ化済み・調整不要）: `content/*.md`

### `report-review` — `tabular-sdg-skillset`

[SKILL.md](https://github.com/gghatano/tabular-sdg-skillset/blob/main/.claude/skills/report-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`, `content/EXPERIMENTS.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code
- 参考（パラメータ化済み・調整不要）: `content/method-*.md`

### `report-review` — `tpdp2026-binagg`

[SKILL.md](https://github.com/gghatano/tpdp2026-binagg/blob/main/.claude/skills/report-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/index.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code
- 参考（パラメータ化済み・調整不要）: `content/*.md`

### `report-review` — `tpdp2026-mst-aim-audit`

[SKILL.md](https://github.com/gghatano/tpdp2026-mst-aim-audit/blob/main/.claude/skills/report-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`, `content/EXPERIMENTS.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code
- 参考（パラメータ化済み・調整不要）: `content/method-*.md`

### `report-skeleton` — `dpsynth-demo`

[SKILL.md](https://github.com/gghatano/dpsynth-demo/blob/main/.claude/skills/report-skeleton/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`

### `report-skeleton` — `pe-demo`

[SKILL.md](https://github.com/gghatano/pe-demo/blob/main/.claude/skills/report-skeleton/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`
- 参考（パラメータ化済み・調整不要）: `templates/*_TEMPLATE.md`

### `report-skeleton` — `synth-report-kit`

[SKILL.md](https://github.com/gghatano/synth-report-kit/blob/main/.claude/skills/report-skeleton/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`
- 参考（パラメータ化済み・調整不要）: `templates/*_TEMPLATE.md`

### `report-skeleton` — `tabular-sdg-skillset`

[SKILL.md](https://github.com/gghatano/tabular-sdg-skillset/blob/main/.claude/skills/report-skeleton/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`

### `report-skeleton` — `tpdp2026-binagg`

[SKILL.md](https://github.com/gghatano/tpdp2026-binagg/blob/main/.claude/skills/report-skeleton/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/index.md`

### `report-skeleton` — `tpdp2026-mst-aim-audit`

[SKILL.md](https://github.com/gghatano/tpdp2026-mst-aim-audit/blob/main/.claude/skills/report-skeleton/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/REPORT.md`

### `repro-engineering-review` — `dpsynth-demo`

[SKILL.md](https://github.com/gghatano/dpsynth-demo/blob/main/.claude/skills/repro-engineering-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/setup.md`, `content/usage.md`, `content/reproduce.md`, `content/engineering-notes.md`, `scripts/setup_env.sh`, `scripts/run_all.sh`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code, Git, Python

### `repro-engineering-review` — `pe-demo`

[SKILL.md](https://github.com/gghatano/pe-demo/blob/main/.claude/skills/repro-engineering-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/engineering.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code, Git, Python, uv

### `repro-engineering-review` — `synth-report-kit`

[SKILL.md](https://github.com/gghatano/synth-report-kit/blob/main/.claude/skills/repro-engineering-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/engineering.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code, Git, Python, uv

### `repro-engineering-review` — `tabular-sdg-skillset`

[SKILL.md](https://github.com/gghatano/tabular-sdg-skillset/blob/main/.claude/skills/repro-engineering-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/setup.md`, `content/usage.md`, `content/reproduce.md`, `content/engineering-notes.md`, `scripts/setup_env.sh`, `scripts/run_all.sh`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code, Git, Python

### `repro-engineering-review` — `tpdp2026-binagg`

[SKILL.md](https://github.com/gghatano/tpdp2026-binagg/blob/main/.claude/skills/repro-engineering-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/setup.md`, `content/usage.md`, `content/reproduce.md`, `content/engineering-notes.md`, `scripts/setup_env.sh`, `scripts/run_all.sh`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code, Git, Python

### `repro-engineering-review` — `tpdp2026-mst-aim-audit`

[SKILL.md](https://github.com/gghatano/tpdp2026-mst-aim-audit/blob/main/.claude/skills/repro-engineering-review/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `content/setup.md`, `content/usage.md`, `content/reproduce.md`, `content/engineering-notes.md`, `scripts/setup_env.sh`, `scripts/run_all.sh`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`
- **必要ツール**: Claude Code, Git, Python

### `research-cycle` — `dpsynth-demo`

[SKILL.md](https://github.com/gghatano/dpsynth-demo/blob/main/.claude/skills/research-cycle/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `docs/plans/`, `content/REPORT.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.claude/agents/`
- **必要ツール**: Claude Code, uv

### `research-cycle` — `synth-report-kit`

[SKILL.md](https://github.com/gghatano/synth-report-kit/blob/main/.claude/skills/research-cycle/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `docs/plans/`, `content/REPORT.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.claude/agents/`
- **必要ツール**: Claude Code, uv

### `research-cycle` — `tabular-sdg-skillset`

[SKILL.md](https://github.com/gghatano/tabular-sdg-skillset/blob/main/.claude/skills/research-cycle/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `docs/plans/`, `content/REPORT.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.claude/agents/`
- **必要ツール**: Claude Code, uv

### `research-cycle` — `tpdp2026-binagg`

[SKILL.md](https://github.com/gghatano/tpdp2026-binagg/blob/main/.claude/skills/research-cycle/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `docs/plans/`, `content/REPORT.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.claude/agents/`
- **必要ツール**: Claude Code, uv

### `research-cycle` — `tpdp2026-mst-aim-audit`

[SKILL.md](https://github.com/gghatano/tpdp2026-mst-aim-audit/blob/main/.claude/skills/research-cycle/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `docs/plans/`, `content/REPORT.md`
- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.claude/agents/`
- **必要ツール**: Claude Code, uv

### `start-feature` — `asset-management`

[SKILL.md](https://github.com/gghatano/asset-management/blob/develop/.claude/skills/start-feature/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `docs/development.md`, `feature/fetch-prices`, `fix/portfolio-calc-rounding`, `chore/bump-uv`, `docs/update-spec`, `~/work/asset-management/`, `~/work/asset-management.wt/`
- **必要ツール**: Git, uv
- 参考（パラメータ化済み・調整不要）: `feature/*`

### `synthesize` — `pets-seminar-01`

[SKILL.md](https://github.com/gghatano/pets-seminar-01/blob/main/.claude/skills/synthesize/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `examples/university_enrollment`, `output/quality_gate.json`, `input/data_spec.md`, `input/constraints.md`
- **一緒にコピー（ハーネス同梱物）**: `.agents/skills/<step>/SKILL.md`
- **必要ツール**: Claude Code, Python
- 参考（パラメータ化済み・調整不要）: `$ARGUMENTS/input/`, `input/*table_definition*`, `input/*sample_data*`

### `worktree-task-runner` — `synthetic-research-data-sharing`

[SKILL.md](https://github.com/gghatano/synthetic-research-data-sharing/blob/develop/.claude/skills/worktree-task-runner/SKILL.md)

- **要読み替え（外部プロジェクトのパス）**: `issue/12-pytest-foundation`
- **必要ツール**: Git, GitHub CLI, Python, uv
- 参考（パラメータ化済み・調整不要）: `issue/<issue-number>-<short-slug>`, `../worktrees/<repo-name>-issue-<issue-number>`

## 同梱前提（18）

スキル本体に加えて、以下の兄弟ファイルも一緒にコピーしてください。

### `company-data-analyzer` — `ppdp-demo`

[SKILL.md](https://github.com/gghatano/ppdp-demo/blob/main/.claude/skills/company-data-analyzer/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.agents/skills/company-data-analyzer/SKILL.md`

### `dist-zip-builder` — `ppdp-demo`

[SKILL.md](https://github.com/gghatano/ppdp-demo/blob/main/.claude/skills/dist-zip-builder/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.agents/skills/dist-zip-builder/SKILL.md`

### `doc-cycle` — `dpsynth-demo`

[SKILL.md](https://github.com/gghatano/dpsynth-demo/blob/main/.claude/skills/doc-cycle/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.claude/agents/`
- **必要ツール**: Claude Code, Git

### `doc-cycle` — `synth-report-kit`

[SKILL.md](https://github.com/gghatano/synth-report-kit/blob/main/.claude/skills/doc-cycle/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.claude/agents/`
- **必要ツール**: Claude Code, Git

### `doc-cycle` — `tabular-sdg-skillset`

[SKILL.md](https://github.com/gghatano/tabular-sdg-skillset/blob/main/.claude/skills/doc-cycle/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.claude/agents/`
- **必要ツール**: Claude Code, Git

### `doc-cycle` — `tpdp2026-binagg`

[SKILL.md](https://github.com/gghatano/tpdp2026-binagg/blob/main/.claude/skills/doc-cycle/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.claude/agents/`
- **必要ツール**: Claude Code, Git

### `doc-cycle` — `tpdp2026-mst-aim-audit`

[SKILL.md](https://github.com/gghatano/tpdp2026-mst-aim-audit/blob/main/.claude/skills/doc-cycle/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.claude/docs/documentation-conventions.md`, `.claude/agents/`
- **必要ツール**: Claude Code, Git

### `experiment-plan` — `dpsynth-demo`

[SKILL.md](https://github.com/gghatano/dpsynth-demo/blob/main/.claude/skills/experiment-plan/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.claude/agents/planner.md`
- **必要ツール**: Claude Code
- 参考（パラメータ化済み・調整不要）: `docs/plans/<ID>-<slug>.md`, `docs/plans/<ID>-...`

### `experiment-plan` — `synth-report-kit`

[SKILL.md](https://github.com/gghatano/synth-report-kit/blob/main/.claude/skills/experiment-plan/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.claude/agents/planner.md`
- **必要ツール**: Claude Code
- 参考（パラメータ化済み・調整不要）: `docs/plans/<ID>-<slug>.md`, `docs/plans/<ID>-...`

### `experiment-plan` — `tabular-sdg-skillset`

[SKILL.md](https://github.com/gghatano/tabular-sdg-skillset/blob/main/.claude/skills/experiment-plan/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.claude/agents/planner.md`
- **必要ツール**: Claude Code
- 参考（パラメータ化済み・調整不要）: `docs/plans/<ID>-<slug>.md`, `docs/plans/<ID>-...`

### `experiment-plan` — `tpdp2026-binagg`

[SKILL.md](https://github.com/gghatano/tpdp2026-binagg/blob/main/.claude/skills/experiment-plan/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.claude/agents/planner.md`
- **必要ツール**: Claude Code
- 参考（パラメータ化済み・調整不要）: `docs/plans/<ID>-<slug>.md`, `docs/plans/<ID>-...`

### `experiment-plan` — `tpdp2026-mst-aim-audit`

[SKILL.md](https://github.com/gghatano/tpdp2026-mst-aim-audit/blob/main/.claude/skills/experiment-plan/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.claude/agents/planner.md`
- **必要ツール**: Claude Code
- 参考（パラメータ化済み・調整不要）: `docs/plans/<ID>-<slug>.md`, `docs/plans/<ID>-...`

### `scenario-reviewer` — `ppdp-demo`

[SKILL.md](https://github.com/gghatano/ppdp-demo/blob/main/.claude/skills/scenario-reviewer/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.agents/skills/scenario-reviewer/SKILL.md`
- **必要ツール**: Claude Code
- 参考（パラメータ化済み・調整不要）: `docs/review_report_<company_short>.md`

### `uc-catalog-builder` — `ppdp-demo`

[SKILL.md](https://github.com/gghatano/ppdp-demo/blob/main/.claude/skills/uc-catalog-builder/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.agents/skills/uc-catalog-builder/SKILL.md`
- **必要ツール**: Claude Code

### `uc-catalog-reviewer` — `ppdp-demo`

[SKILL.md](https://github.com/gghatano/ppdp-demo/blob/main/.claude/skills/uc-catalog-reviewer/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.agents/skills/uc-catalog-reviewer/SKILL.md`
- **必要ツール**: Claude Code

### `uc-eval-reviewer` — `ppdp-demo`

[SKILL.md](https://github.com/gghatano/ppdp-demo/blob/main/.claude/skills/uc-eval-reviewer/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.agents/skills/uc-eval-reviewer/SKILL.md`
- **必要ツール**: Claude Code

### `uc-quickwin-evaluator` — `ppdp-demo`

[SKILL.md](https://github.com/gghatano/ppdp-demo/blob/main/.claude/skills/uc-quickwin-evaluator/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.agents/skills/uc-quickwin-evaluator/SKILL.md`

### `ui-value-design` — `sxtf-mock`

[SKILL.md](https://github.com/gghatano/sxtf-mock/blob/develop/.claude/skills/ui-value-design/SKILL.md)

- **一緒にコピー（ハーネス同梱物）**: `.claude/knowledge/`
- **必要ツール**: Claude Code
- 参考（パラメータ化済み・調整不要）: `feat/ui-*`

## そのまま（16）

特別な調整なしに持ち運べるスキルです。

### `4_evaluate_and_refine` — `pets-seminar-01`

[SKILL.md](https://github.com/gghatano/pets-seminar-01/blob/main/.claude/skills/4_evaluate_and_refine/SKILL.md)

- 参考（パラメータ化済み・調整不要）: `$ARGUMENTS/input/*sample_data*`, `$ARGUMENTS/output/synthetic_data.csv`, `$ARGUMENTS/output/<table>.csv`, `$ARGUMENTS/work/inferred_schema.json`, `$ARGUMENTS/work/constraint_plan.md`, `$ARGUMENTS/src/generator.py`, `$ARGUMENTS/src/evaluate.py`, `$ARGUMENTS/output/evaluation_report.md`

### `calibrate-params` — `sxtf-simulation`

[SKILL.md](https://github.com/gghatano/sxtf-simulation/blob/master/.claude/skills/calibrate-params/SKILL.md)


### `case-review` — `privacy-incident-catalog`

[SKILL.md](https://github.com/gghatano/privacy-incident-catalog/blob/main/.claude/skills/case-review/SKILL.md)

- **必要ツール**: npm
- 参考（パラメータ化済み・調整不要）: `public/cases/{ID}/case.json`

### `code-review` — `synthetic-research-data-sharing`

[SKILL.md](https://github.com/gghatano/synthetic-research-data-sharing/blob/develop/.claude/skills/code-review/SKILL.md)

- **必要ツール**: Git, npm

### `issue-driven-development` — `synthetic-research-data-sharing`

[SKILL.md](https://github.com/gghatano/synthetic-research-data-sharing/blob/develop/.claude/skills/issue-driven-development/SKILL.md)

- **必要ツール**: Claude Code, GitHub CLI, Make, Python, uv
- 参考（パラメータ化済み・調整不要）: `issue/<n>-<slug>`, `../worktrees/<repo>-issue-<n>`

### `issue-triage` — `synthetic-research-data-sharing`

[SKILL.md](https://github.com/gghatano/synthetic-research-data-sharing/blob/develop/.claude/skills/issue-triage/SKILL.md)

- **必要ツール**: GitHub CLI

### `make-report` — `sxtf-simulation`

[SKILL.md](https://github.com/gghatano/sxtf-simulation/blob/master/.claude/skills/make-report/SKILL.md)

- **必要ツール**: Make, uv

### `pr-from-issue` — `synthetic-research-data-sharing`

[SKILL.md](https://github.com/gghatano/synthetic-research-data-sharing/blob/develop/.claude/skills/pr-from-issue/SKILL.md)

- **必要ツール**: Claude Code, GitHub CLI
- 参考（パラメータ化済み・調整不要）: `issue/<n>-<slug>`

### `pr-prep` — `synthetic-research-data-sharing`

[SKILL.md](https://github.com/gghatano/synthetic-research-data-sharing/blob/develop/.claude/skills/pr-prep/SKILL.md)

- **必要ツール**: Claude Code, Git, Make, uv
- 参考（パラメータ化済み・調整不要）: `feature/<topic>`

### `refactor-safely` — `synthetic-research-data-sharing`

[SKILL.md](https://github.com/gghatano/synthetic-research-data-sharing/blob/develop/.claude/skills/refactor-safely/SKILL.md)

- **必要ツール**: Git, Make

### `review-prs` — `pseudonymize-webapp`

[SKILL.md](https://github.com/gghatano/pseudonymize-webapp/blob/main/.claude/skills/review-prs/SKILL.md)

- **必要ツール**: Claude Code, GitHub CLI

### `spec-implementation` — `synthetic-research-data-sharing`

[SKILL.md](https://github.com/gghatano/synthetic-research-data-sharing/blob/develop/.claude/skills/spec-implementation/SKILL.md)

- **必要ツール**: Make, uv

### `stop-ai-slop-jp` — `pe-demo`

[SKILL.md](https://github.com/gghatano/pe-demo/blob/main/.claude/skills/stop-ai-slop-jp/SKILL.md)


### `stop-ai-slop-jp` — `synth-report-kit`

[SKILL.md](https://github.com/gghatano/synth-report-kit/blob/main/.claude/skills/stop-ai-slop-jp/SKILL.md)


### `test-fix-loop` — `synthetic-research-data-sharing`

[SKILL.md](https://github.com/gghatano/synthetic-research-data-sharing/blob/develop/.claude/skills/test-fix-loop/SKILL.md)

- **必要ツール**: Make, uv

### `verify-sim` — `sxtf-simulation`

[SKILL.md](https://github.com/gghatano/sxtf-simulation/blob/master/.claude/skills/verify-sim/SKILL.md)

- **必要ツール**: Python, uv
