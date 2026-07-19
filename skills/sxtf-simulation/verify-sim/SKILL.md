---
name: verify-sim
description: モデル・KPI・config を変更した後の検証手順。シミュレーションコードを触ったら必ずこの手順で確認する。
---

# シミュレーション検証手順

仕様書 §9 の検証4項目を、変更内容に応じて実行する。

## 1. 常に実行(30秒)

```bash
uv run pytest -q
uv run ruff check src tests
```

テストには構造検証が含まれる:
- **理想極限**: 情報フロー遅延・エラー全ゼロで L0=L2 のリードタイムが一致(`test_ideal_limit_levels_equal`)。
  これが壊れた場合、レベル差以外の何か(材料フロー側)に情報パラメータが漏れている
- **方向**: L0 の間接工数 > L2 の5倍(`test_direction_l0_worse_than_l2`)

## 2. モデル・パラメータ変更時(1分)

```bash
uv run sxtf-sim matrix --reps 10
```

サニティチェック項目:
- 労務コスト: L0 > L1 > L2 の単調減少になっているか
- OTIF が全レベル 1.0 に張り付いていないか(張り付く場合は promised_leadtime_h が緩すぎ、
  納期差分の価値がゼロに見積もられてしまう)
- リードタイム: L0 と L2 の差が issue_delay + 照合・エラーループの合計と桁で整合するか

## 3. 総量検算(スケールアップ・キャリブレーション変更時)

```python
uv run python -c "
from sxtf_sim import model, kpi
from sxtf_sim.config import load_config
cfg = load_config('l0')
print(kpi.validate_cert_volume(kpi.compute_kpis(model.run(cfg, 42), cfg), cfg))
"
```

national_certs_per_year が「粗鋼生産量 × カバー率 ÷ 平均ロットサイズ」と桁一致すること。

## 4. 統計的な比較をするとき

- レベル間比較は同一シード(CRN)が前提。runner.py 以外から model.run を呼ぶ場合も
  反復番号→シードの対応をレベル間で揃えること
- 反復間のばらつきは outputs/matrix_*_raw.csv の std で確認。平均差が std より小さい KPI を
  レポートで主張しない
