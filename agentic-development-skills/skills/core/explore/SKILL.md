---
name: explore
description: 問題領域・既存コード・関連技術を独立探索して統合する調査パターン。実装や設計判断の前に事実を集める段階で使う。複数の独立調査を走らせ一次情報を優先し、矛盾を抽出してから統合する。何を調べるか（対象）は Project Spec 側、どう調べるか（手順）が本 Skill。
---

# explore（独立探索と統合による調査）

問題領域・既存コード・関連技術を調査し、根拠付きの調査結果に統合する。
**何を調べるか**は Project Spec が与える。本 Skill は**どう調べるか**だけを定義する。

## Inputs
- question: 調査したい問い（Project Spec / 上位 Workflow から）
- source_code: リポジトリ（任意）
- constraints: 探索範囲・時間・情報源の制約（任意）

## Outputs
- `research.md`: 問い・調査方法・根拠（出典付き）・矛盾点・結論を含む統合結果

## Preconditions
- 調査したい問いが 1 文で言語化されている

## Procedure

```
Question
  ↓
Independent Exploration   （複数の切り口を相互に共有せず並行して調べる）
  ↓
Evidence Collection       （一次情報を優先し、出典を必ず記録）
  ↓
Comparison                （切り口ごとの結論を突き合わせる）
  ↓
Synthesis                 （矛盾を抽出し、確度付きで統合）
```

1. 問いを 2〜4 個の独立した切り口に分解する（例: コードベース内 / 公式ドキュメント / 代替手段）。
2. 各切り口を**相互の結果を共有せず**に調べる（同じ前提への早期収束を防ぐ）。
3. 収集した根拠に必ず出典（ファイル:行 / URL / 一次情報か二次情報か）を付ける。
4. 切り口間で結論を比較し、一致点・**矛盾点**・未解決点を分ける。
5. 確度（高/中/低）を付けて `research.md` に統合する。

**この Skill がやらないこと**: 実装・設計の決定（→ `plan`）、コードの変更。

## Validation
- 主要な主張それぞれに出典があるか
- 一次情報を最低 1 件参照しているか
- 矛盾点・未解決点が「無い」ではなく明示的に列挙されているか

## Stop conditions
- 問いに答えるのに十分な根拠が集まり、矛盾が解消 or 明示された
- これ以上調べても新しい根拠が出ない（収穫逓減）

## Failure handling
- 一次情報に到達できない → **Escalate**（人間に情報源を確認）
- 切り口間の矛盾が解消できない → 矛盾を `research.md` に残したまま **Escalate**
- 情報が皆無 → 問いの再定義を **Request additional investigation**

## Adapter notes
独立探索は並列サブエージェントで実行すると効果が高い（`independent-review` と同じ隔離原則）。
サブエージェントが無い環境では、切り口ごとに Context を分けて逐次実行する。詳細は `adapters/`。

## Derived skills
- `explore-codebase`: 既存コードの構造・依存を調べる
- `explore-web`: 外部ドキュメント・技術記事を調べる
- `explore-alternatives`: 代替手段・技術選定肢を比較する
- `explore-root-cause`: 不具合の根本原因を切り分ける
