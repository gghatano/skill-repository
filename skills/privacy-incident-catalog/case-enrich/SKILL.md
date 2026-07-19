---
name: case-enrich
description: 追加文献で既存事例の case.json を補完・改善
argument-hint: "<case-id> <URL or description>"
user-invocable: true
---

追加文献をもとに既存の case.json を補完・改善する。

## 手順

### 1. 引数の解析

$ARGUMENTS の最初のトークンを事例 ID、残りを文献ソースとして扱う。

### 2. 既存 case.json の読み込み

```
public/cases/<case-id>/case.json
```

ファイルが存在しない場合はエラーを報告して終了する。

### 3. 追加文献の取得・読み取り

URL が指定された場合は WebFetch で取得する。テキストが直接与えられた場合はそのまま使用する。

### 4. case.json の更新

`src/constants/prompts.ts` の `generateEnrichPrompt()` に定義された作業ルールに従い、既存の case.json を更新する。主なルール:

- **すべての項目が改善対象**: 「調査中」の項目だけでなく、より正確・詳細・具体的にできる項目も更新する
- **summary と impact の役割分担**: summary は事件の経緯（何が起こったか）、impact は影響・被害（どう影響したか）を記述する
- **sources の追加**: 追加文献を sources 配列に追記する（既存の source は削除しない）
- **推測しない**: 文献に明記されていない情報は既存の記載を維持する

詳細なガイドラインは `src/constants/prompts.ts` を正とする。

### 5. バリデーション

```bash
npx tsx scripts/validate-cases.ts
```

エラーがあれば修正して再度バリデーションを実行する。

### 6. レビュー

更新した事例に対して /case-review を実行し、公開情報との整合性を検証する。
