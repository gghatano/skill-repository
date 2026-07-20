---
name: integrate
description: 複数 Agent の成果物（候補・レビュー・解）を 1 つに統合するパターン。比較し、衝突を解消し、選択・マージ・投票・スコアリング・ジャッジのいずれかで統合する。並列 Agent の出力をまとめる段階で使う。統合 Agent だけが全候補を受け取る。
---

# integrate（複数成果物の統合）

複数 Agent が独立に生成した候補やレビューを 1 つに統合する。
**統合 Agent だけが全候補を受け取る**（生成側は互いの出力を見ない = Context 隔離）。

## Inputs
- candidates: 統合対象の成果物群（解 A/B/C、または複数レビュー）
- criteria: 統合基準（`spec.md` の要件・評価軸）
- method: 統合方法（selection / merge / voting / scoring / judge）

## Outputs
- `integration.md`: 統合結果と、その選択理由・破棄した候補・残存衝突

## Preconditions
- 2 つ以上の候補が独立に（相互非共有で）生成されている

## Procedure

```
Candidate A ─┐
Candidate B ─┼→ Compare → Resolve Conflict → Merge/Select
Candidate C ─┘
```

統合方法（用途で切り替え）:

```
Selection            最良候補を 1 つ選ぶ
Merge                各候補の良い部分を統合する
Voting               多数決
Weighted Voting      重み付き多数決
Scoring              基準ごとにスコア化して合算
Pairwise Comparison  総当たり比較で順位付け
Judge                ジャッジ Agent が根拠付きで裁定
```

1. 候補を評価基準に沿って比較する。
2. 矛盾・衝突を洗い出し、解消方針を決める。
3. 指定 `method` で統合する（設計・技術選定は judge/scoring、レビュー統合は merge+dedup が向く）。
4. 破棄した候補と理由、残った衝突を `integration.md` に残す。

**この Skill がやらないこと**: 候補の生成（生成 Skill 側）、修正の実装（→ `fix`）。

## Validation
- 採用理由と破棄理由が根拠付きで書かれている
- 重複指摘の dedup がされている（レビュー統合の場合）
- 残存する衝突・未解決点が隠されず明示されている

## Stop conditions
- 全候補を比較し、統合結果を根拠付きで確定した

## Failure handling
- 候補が優劣つけがたい → 追加基準で再評価、なお割れるなら **Escalate**
- 候補が実は同一前提に収束していた → 独立性の欠如を報告し `explore`/生成を **Request additional investigation**

## Adapter notes
生成 Agent と統合 Agent を分離する。並列生成 → バリア → 統合、が基本形。
`independent-review` はこの Skill をレビュー統合に特化して使う。詳細は `adapters/`。
