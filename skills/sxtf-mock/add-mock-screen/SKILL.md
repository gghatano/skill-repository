---
name: add-mock-screen
description: sxtf-mock（鉄骨サプライチェーン真正性証明モック）に画面を1枚追加/実装するときの標準手順。Next.js App Router + TS + Tailwind + shadcn/ui で、共有の型・mock-store・provenance 契約を壊さず規約準拠で画面を作る。screen-inventory.md の T2〜T7 のいずれかの画面を担当する/モック画面を追加・実装するときは、明示的に "skill" と言われなくても必ずこのスキルを使うこと。
---

# add-mock-screen

sxtf-mock のモック画面を1枚、規約通り・共有契約を壊さずに追加するための手順。サブエージェントはこの手順に従えば他の画面と整合する。

## 前提：先に読むナレッジ（必須）

実装前に必ず `.claude/knowledge/` の以下を読むこと。ここに書かれた契約が唯一の真実：

1. `data-model.md` — 型定義（`lib/types.ts` の正）
2. `mock-ledger-api.md` — store / crypto-mock / provenance の関数シグネチャ。**これ以外の方法でデータを触らない。**
3. `screen-inventory.md` — 自分の担当パス・要件・対応機能番号
4. `demo-scenario.md` — シードデータ前提
5. `domain-glossary.md` — 用語・ロール・docType の正式表記

## 鉄則

- **データ操作は store の Actions と provenance / certificate の関数経由のみ。** コンポーネント内で台帳・ハッシュ・経路を組み立てない。
- **開示可否は必ず `canViewRoute` / `canViewVerdict` を呼ぶ（`canViewContent` は v2 で廃止）。** 画面に `if (role === ...)` を散らさない。
- **基盤は中身(PDF)を持たない（実ファイル非保存）。** 書類は外部ファイルのハッシュ＋最小メタで表す。中身(body)・`lotNo`・`quantity` は無い。検証は **ファイル取込→ハッシュ照合**（`verifyExternalFile` / `verifyWithCertificate`）。改ざんデモは「改変ファイル/別物の取り込み→ハッシュ不一致」で行う（`updateBody` は無い）。
- **型は `lib/types.ts` をimportして使う。** ローカルで別定義しない。フィールド不足を感じたら勝手に足さず、data-model.md の更新を提案する（契約変更）。
- 日本語UI。ロール名・docType表記は glossary に合わせる。
- 検証状態の表示は3状態統一：✓=green / ✗=red / －=gray(非開示)。

## 手順

### 1. 担当画面の確認
screen-inventory.md で自分のパス（例 `/inbox`）・要件・対応機能Noを確認。不明点はナレッジ内で解決し、契約に無いことは仮定しない。

### 2. ルート作成
App Router で `app/<path>/page.tsx` を作成。`'use client'` を付ける（store がクライアント状態のため）。ページ冒頭に「この画面が示す機能概要 No.X」の注記を入れる（デモ説明用）。

### 3. データ取得は契約経由
```ts
import { useAppStore, selectInbox } from '@/lib/mock-store';
import { verifyDocument, buildProvenance, canViewRoute, canViewVerdict, verifyExternalFile } from '@/lib/provenance';
import { issueCertificate, verifyWithCertificate } from '@/lib/certificate';
```
セレクタ／provenance／certificate関数で必要データを導出。変更は Actions（`signDocument`, `transfer`, `grantAccess` 等）で行う。

### 4. UI構築
- shadcn/ui のコンポーネント（Card, Table, Badge, Button, Dialog, Select 等）を使う。
- ロール切替で表示が変わる画面は、現在ユーザー（`selectCurrentUser`）基準で出し分け。
- 検証/開示状態は共通の3状態表示で。

### 5. ナビ登録
共通ナビ（T2のレイアウト）に自分の画面リンクを追加。現在ロールで意味がある画面のみ出すよう、必要なら可視ロールを指定。

### 6. ブランチ・隔離
`develop` から `feat/T<n>-<slug>` を切り、git worktree 内で作業する（並列タスクの競合回避）。Gitモデルの詳細は `.claude/knowledge/dev-workflow.md`。**main は触らない。**

### 7. DoD（完了の定義・全項目必須）
1. `npm run build` 成功・型エラーなし。
2. 担当画面の **Playwright E2Eテスト**を `tests/e2e/` に追加し green。
3. `demo-scenario.md` の該当シナリオを手で再現できる（例：受領者画面なら doc-0001 受領→真正性チェック全✓）。
4. 対応機能No（特に No.4 / No.9）が画面上で成立。
5. 契約ファイルを変更していない（した場合はエスカレーション済み）。

### 8. マージ・報告
DoD達成後、自ブランチを `develop` へマージ（`main`は人間のみ）。`.claude/progress.md` に1行追記。完了報告に：担当パス・実装機能No・使った契約関数・確認シナリオ・未対応点・契約変更の有無 を含める。コミット末尾に `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。

## やってはいけないこと

- 共有の `lib/types.ts` / `lib/mock-store.ts` / `lib/provenance.ts` のシグネチャを無断で変更する（他画面が壊れる）。
- localStorage や台帳を直接読み書きする（store経由でないと永続化・監査ログが漏れる）。
- 実暗号ライブラリを導入する（本モックは crypto-mock の疑似実装が前提）。
- 機能番号と無関係な独自機能を足す（デモの焦点 No.4/No.9 がぼやける）。
