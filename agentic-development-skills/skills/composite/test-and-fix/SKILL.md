---
name: test-and-fix
description: test と fix を、全テストが通るか上限回数に達するまで回すループ構造。実装後に機械的検証を緑にする段階で使う。test（検証）と fix（修正）を分離したまま反復する Composite Skill。
---

# test-and-fix（テスト緑化ループ）

`test` と `fix` を組み合わせたループ。**検証と修正を分離したまま**反復する。
Core の `test` / `fix` 単体でも使えるよう、ループ構造は Skill 内に埋め込まず本 Composite に置く。

## Inputs
- changed_files: 対象の実装
- project_spec: `spec.md`
- config: `{ max_iterations: <n> }`（既定 5）

## Outputs
- changed_files: 修正後の実装
- `test-results.json`: 最終テスト結果

## Preconditions
- 実装が存在し、テストが実行可能

## Procedure

```
Test
 ↓
Fail?
├─ No  → Done
└─ Yes
     ↓
    Fix        （失敗 1 件 = 修正 1 件）
     ↓
    Test       （回帰確認を含む）
     ↓ (loop)
```

1. `test` を実行し `test-results.json` を得る。
2. 失敗が無ければ完了。あれば分類済みの失敗を `fix` へ渡す。
3. `fix` 後にもう一度 `test`（回帰含む）。
4. 停止条件まで繰り返す。

## Validation
- 各反復で失敗件数が単調に減っている（増えたら回帰。原因を切り分ける）
- 最終的に対象範囲のテストが緑

## Stop conditions
- `all tests pass`、または
- `max_iterations reached`（上限到達時は未解決を明示して終了）

## Failure handling
- 上限到達で未解決が残る → 残失敗を列挙して **Escalate**
- 失敗が振動する（直すと別が落ちる） → **Escalate**（設計問題の可能性、`plan` へ）
- 同じ失敗が減らない → `explore-root-cause` へ **Request additional investigation**

## Adapter notes
`test` と `fix` は別 Context で回すのが理想（評価と生成の分離）。
上限回数は Workflow の `config.max_iterations` で外から与える。詳細は `adapters/`。
