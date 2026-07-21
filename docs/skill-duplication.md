# Skill Duplication Report（重複状況）

GitHub account `gghatano` のスキルのうち、**複数リポジトリに同名で存在**するものを集計した自動生成レポートです。共通部分として `plugins/` のプラグインに集約する候補を把握するために使います。
このファイルは直接編集せず、`python3 scripts/sync_skills.py` で更新してください。

スキル総数: **91** ／ ユニーク名: **50** ／ 複数リポジトリに重複する名前: **10**

「内容バージョン数」は SKILL.md の内容ハッシュの種類数です。**1 なら全リポジトリで内容一致**（共通化しやすい）、2 以上なら差分があり収束前にレビューが要ります。

| Skill | リポジトリ数 | 内容バージョン数 | リポジトリ |
| --- | --- | --- | --- |
| `publish-check` | 6 | 2 ⚠ | `dpsynth-demo`, `pe-demo`, `synth-report-kit`, `tabular-sdg-skillset`, `tpdp2026-binagg`, `tpdp2026-mst-aim-audit` |
| `report-review` | 6 | 5 ⚠ | `dpsynth-demo`, `pe-demo`, `synth-report-kit`, `tabular-sdg-skillset`, `tpdp2026-binagg`, `tpdp2026-mst-aim-audit` |
| `report-skeleton` | 6 | 4 ⚠ | `dpsynth-demo`, `pe-demo`, `synth-report-kit`, `tabular-sdg-skillset`, `tpdp2026-binagg`, `tpdp2026-mst-aim-audit` |
| `repro-engineering-review` | 6 | 2 ⚠ | `dpsynth-demo`, `pe-demo`, `synth-report-kit`, `tabular-sdg-skillset`, `tpdp2026-binagg`, `tpdp2026-mst-aim-audit` |
| `doc-cycle` | 5 | 3 ⚠ | `dpsynth-demo`, `synth-report-kit`, `tabular-sdg-skillset`, `tpdp2026-binagg`, `tpdp2026-mst-aim-audit` |
| `experiment-plan` | 5 | 3 ⚠ | `dpsynth-demo`, `synth-report-kit`, `tabular-sdg-skillset`, `tpdp2026-binagg`, `tpdp2026-mst-aim-audit` |
| `experiment-run` | 5 | 2 ⚠ | `dpsynth-demo`, `synth-report-kit`, `tabular-sdg-skillset`, `tpdp2026-binagg`, `tpdp2026-mst-aim-audit` |
| `related-info-review` | 5 | 3 ⚠ | `dpsynth-demo`, `synth-report-kit`, `tabular-sdg-skillset`, `tpdp2026-binagg`, `tpdp2026-mst-aim-audit` |
| `research-cycle` | 5 | 3 ⚠ | `dpsynth-demo`, `synth-report-kit`, `tabular-sdg-skillset`, `tpdp2026-binagg`, `tpdp2026-mst-aim-audit` |
| `stop-ai-slop-jp` | 2 | 1 | `pe-demo`, `synth-report-kit` |
