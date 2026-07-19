---
name: case-create
description: 文献URL・テキストから新規 case.json を作成
argument-hint: "<URL or description of literature>"
user-invocable: true
---

提供された文献（URL またはテキスト）からデータ活用・プライバシー炎上事例の case.json を新規作成する。

## 手順

### 1. 文献の取得・読み取り

$ARGUMENTS で指定された URL を WebFetch で取得する。テキストが直接与えられた場合はそのまま使用する。

### 2. 事例情報の抽出

`src/constants/prompts.ts` の `generateCreatePrompt()` に定義されたガイドラインに従い、文献から以下の情報を抽出する:

- title, summary, impact, root_cause, response, lessons_learned
- region, domain, domain_sub, organization
- incident_category（選択肢は `src/constants/categories.ts` を参照）
- severity
- tags, sources
- figures（data_flow のノードとエッジ）

**重要**:
- フィールドごとの記入ガイドラインは `src/constants/prompts.ts` を正とする
- 文献から読み取れない項目は「調査中」と記入し、推測で埋めない
- **summary と impact の役割分担**:
  - summary: 何が起こったか、事件の経緯を記述する
  - impact: どのような影響・被害があったかを記述する

### 2.5. スコープ判定

事例を作成する前に、カタログの対象範囲内かを判定する。以下に該当する場合は **作成しない**:

- **単なる情報漏洩・セキュリティインシデント**: 不正アクセスや標的型攻撃による情報流出など、データ活用の文脈がないもの
- **従業員個人の不正行為**: SNSへの情報投稿など、組織のデータ活用方針と無関係な個人の行為

判断に迷う場合はユーザーに確認する。

### 2.6. 出典の関連性確認

各 source URL が当該事例に **直接関連する記事** であることを確認する。同じメディアの別記事や、類似テーマだが別の事例を扱う記事は出典に含めない。

### 2.7. 用語の正確性

ドメイン固有の用語は正確に使い分ける:
- **顔識別** (1対N照合): データベースとの照合で人物を特定 → 監視カメラ、万引き防止等
- **顔認証** (1対1照合): 本人確認 → スマートフォンのロック解除等

### 3. case.json の生成

スキーマは `src/schemas/case.schema.ts` に定義されている。スキーマに適合する JSON を生成する。

**注意事項**:
- 新規作成時は `review_status` を `"ai_generated"` に設定する
- タイトルに「【未レビュー】」を付与する

事例 ID は既存の `public/cases/` 配下の ID を確認し、連番で次の ID を採番する。

### 4. ファイルの保存

```bash
mkdir -p public/cases/<id>
```

生成した JSON を `public/cases/<id>/case.json` に保存する。

### 5. index.json の更新

`public/cases/index.json` に新しい事例 ID を追加する。

### 6. バリデーション

```bash
npx tsx scripts/validate-cases.ts
```

エラーがあれば修正して再度バリデーションを実行する。

### 7. レビュー

生成した事例に対して /case-review を実行し、公開情報との整合性を検証する。
