# Examples

`default-development` Workflow を小さな課題で回すための最小例を置く場所。

## 使い方（雛形）

1. 対象リポジトリで `templates/project-spec.md` を埋めて `spec.md` を作る。
2. 実行環境に合った `adapters/<agent>/` を選ぶ。
3. `workflows/default-development.yaml` の順に Skill を回す:
   `explore → plan → independent-review(plan) → implement → test-and-fix →
   independent-review(code) → review-and-fix → verify`
4. 各 Skill が成果物ファイル（`research.md` / `plan.md` / `review.md` /
   `test-results.json` / `verification.md`）を生成し、次へ引き渡す。

## 予定している例（未実装）

- `cli-app/` — 小さな CLI ツールを spec から一周させる例
- `web-app/` — Web API を high-assurance 寄りの構成で回す例

> MVP ではまず Core/Composite Skill と `default-development` の構造を提供する。
> 具体例は初期検証（README の「初期検証」節）と合わせて追加する。
