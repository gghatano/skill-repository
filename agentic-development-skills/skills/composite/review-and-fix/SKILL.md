---
name: review-and-fix
description: review と fix を、Critical/Major の指摘が無くなるか上限回数に達するまで回すループ構造。実装をレビュー品質基準まで引き上げる段階で使う。review（評価）と fix（修正）を分離したまま反復する Composite Skill。
---

# review-and-fix（レビュー指摘解消ループ）

`review` と `fix` を組み合わせたループ。**評価と修正を分離したまま**反復する。

## Inputs
- changed_files: 対象の実装
- project_spec: `spec.md`
- config: `{ max_iterations: <n>, block_on: [Critical, Major] }`（既定 3 / Critical・Major）

## Outputs
- changed_files: 修正後の実装
- `review.md`: 最終レビュー結果

## Preconditions
- レビュー対象の実装が確定している

## Procedure

```
Review
 ↓
Critical / Major issue?
├─ No  → Done
└─ Yes
     ↓
    Fix        （指摘 1 件 = 修正 1 件）
     ↓
    Review     （再レビュー）
     ↓ (loop)
```

1. `review` で重大度付き指摘を得る。
2. `block_on`（既定 Critical/Major）が無ければ完了。あれば `fix` へ渡す。
3. `fix` 後に再 `review`。
4. 停止条件まで繰り返す。Minor/Suggestion は残してよい（記録する）。

## Validation
- ブロッキング指摘（Critical/Major）が解消している
- 修正で新たな Critical/Major を作っていない
- 残した Minor/Suggestion が `review.md` に記録されている

## Stop conditions
- ブロッキング指摘が 0、または
- `max_iterations reached`（残指摘を明示して終了）

## Failure handling
- 上限到達で Critical/Major が残る → 列挙して **Escalate**
- 指摘の妥当性に争いがある → `adversarial-review` で深掘り、または **Escalate**
- 修正が指摘を解消しない → `explore-root-cause` へ **Request additional investigation**

## Adapter notes
`review` は実装 Agent と別 Agent が担当する（独立性）。並列多観点レビューは
`independent-review` を `review` の代わりに差し込む。詳細は `adapters/`。
