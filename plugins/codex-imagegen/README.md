# codex-imagegen — Codex 画像生成ループ

Codex に画像（スライドの図・インフォグラフィック・図解の PNG）を 1 枚ずつ生成させ、出来上がった PNG を Claude が目でレビューして、具体的な指摘を付けて再依頼するループの skill です。**生成そのものより「出来上がった画像をどう見て、何をどう指摘し直すか」が本体**。プロンプトの作り方・フォルダ構成・恒久ルール（`AGENTS.md`）・デザイン規約（`STYLE.md`）のテンプレートを同梱し、題材やデザインは差し替えて使います。

## 導入

```
/plugin marketplace add gghatano/skill-repository
/plugin install codex-imagegen@gghatano-skills
```

スキルは `/codex-imagegen:codex-imagegen` で呼び出せます。「Codex で画像を作りたい」「スライドの図を作り直したい」「インフォグラフィックの PNG を作って」などと話しかければ自動でも引かれます。

前提: ローカルに `codex` CLI が入っていること（非対話サブコマンド・自動承認フラグは Codex のバージョンで異なるため、`codex exec --help` で確認して `gen.sh` の `CODEX` / `CODEX_FLAGS` で上書きします）。

## 含まれるもの

```
codex-imagegen/
  skills/codex-imagegen/
    SKILL.md                     ← レビュー・再依頼ループの回し方（本体）
    references/
      review-checklist.md        ← PNG を開いて見る順と、見落としやすい粗
      feedback-patterns.md       ← 効いた指摘・効かなかった指摘の型
  scripts/
    gen.sh                       ← Codex に 1 枚ずつ依頼するバッチ
    make_prompts.py              ← prompts/ を生成する（文言の正本）テンプレート
  templates/
    AGENTS.md                    ← Codex が毎回読む恒久ルール（役割・出力規約・文体）テンプレート
    STYLE.md                     ← デザイン規約（配色・文字サイズ下限・日本語組版・出力チェック）テンプレート
    preview.html                 ← out/*.png を一覧してレビューするページ
```

## 含まれるスキル

codex-imagegen

## 導入後の調整

このスキルは**作業ディレクトリを scaffold してから**使います。`scripts/` と `templates/` を作業用ディレクトリ（例 `viz/`）へコピーし、次を自分のプロジェクトに合わせて埋めてください。

- **`AGENTS.md` / `STYLE.md` の `＜…＞`** — 配色とタイポグラフィだけがプロジェクト固有です。日本語組版・文字化け対策・レイアウト作法・出力チェックは領域非依存なのでそのまま使えます。
- **`reference.png`** — 手本にしたい 1 枚を作業ディレクトリに置きます。Codex はこれに寄せて作ります。
- **`make_prompts.py` の `AUDIENCE` / `HOUSE_STYLE` / `SLIDES`** — 想定読者・文体・題材を書きます。`prompts/*.md` は生成物なので手で編集しません。

手順の詳細は `SKILL.md` の「0. 作業ディレクトリを scaffold する」を参照してください。
