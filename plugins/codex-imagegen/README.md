# codex-imagegen — Codex 画像生成パイプライン

Codex に画像（スライドの図・インフォグラフィック・図解の PNG）を作らせるための、**3 工程のパイプライン**をスキルにまとめたプラグインです。**生成そのものより「骨子をどう整え、どう生成用へ変換し、出来上がった画像をどう見て指摘し直すか」が本体**。プロンプトのフォーマット・フォルダ構成・恒久ルール（`AGENTS.md`）・デザイン規約（`STYLE.md`）のテンプレートを同梱し、題材やデザインは差し替えて使います。

```
slide-skeleton（骨子）  →  prompt-build（生成用構造へ変換）  →  generate-review（生成・レビュー）
    outline.md                      prompts/*.md                        out/*.png
```

## 導入

```
/plugin marketplace add gghatano/skill-repository
/plugin install codex-imagegen@gghatano-skills
```

「Codex で画像を作りたい」「スライドの図を作りたい／作り直したい」と話しかければ、まず `slide-skeleton` が引かれます。各工程は `/codex-imagegen:slide-skeleton` → `/codex-imagegen:prompt-build` → `/codex-imagegen:generate-review` で明示的にも呼べます。

前提: ローカルに `codex` CLI が入っていること（非対話サブコマンド・自動承認フラグは Codex のバージョンで異なるため、`codex exec --help` で確認して `gen.sh` の `CODEX` / `CODEX_FLAGS` で上書きします）。

## 含まれるスキル

- **slide-skeleton** — 各画像の骨子（キッカー・ヘッドライン・最重要・構造・強調・素材・数値）とデッキ全体の想定読者・文体を `outline.md` に整える。パイプラインの入口。
- **prompt-build** — 骨子を、固定の生成ルール（AGENTS.md 参照・組版・出力仕様）を添えた生成用プロンプト `prompts/<stem>.md` へ変換する。**大事なのはこのフォーマット**で、変換手段は問わない。
- **generate-review** — `gen.sh` で Codex に生成させ、PNG を 1 枚ずつ目でレビューし、画面の文字列を引用した指摘で再依頼する。3 巡で収束させ、そろった PNG を Claude Code 側で取り込む。

## 同梱物

```
codex-imagegen/
  skills/
    slide-skeleton/SKILL.md
    prompt-build/SKILL.md
    generate-review/
      SKILL.md
      references/
        review-checklist.md       PNG を開いて見る順と、見落としやすい粗
        feedback-patterns.md      効いた指摘・効かなかった指摘の型
  scripts/
    gen.sh                        Codex に 1 枚ずつ依頼するバッチ
  templates/
    outline.md                    骨子のフォーマット（＝文言の正本）
    prompt.md                     生成用プロンプトのフォーマット（骨子 1 → prompts 1）
    AGENTS.md                     Codex が毎回読む恒久ルール（役割・出力規約・文体）
    STYLE.md                      デザイン規約（配色・文字サイズ下限・日本語組版・出力チェック）
    preview.html                  out/*.png を一覧してレビューするページ
    reference.png                 サンプル手本画像（design vocabulary を示す 16:9 の 1 枚）
```

## 導入後の調整

このパイプラインは**作業ディレクトリを scaffold してから**使います（手順は `slide-skeleton` の「0. 作業ディレクトリを scaffold する」）。`scripts/` と `templates/` を作業用ディレクトリ（例 `viz/`）へコピーし、次を自分のプロジェクトに合わせて埋めてください。

- **`AGENTS.md` / `STYLE.md` の `＜…＞`** — 配色とタイポグラフィだけがプロジェクト固有です。日本語組版・文字化け対策・レイアウト作法・出力チェックは領域非依存なのでそのまま使えます。
- **`reference.png`** — 手本にしたい 1 枚に差し替えます。Codex はこれに寄せて作ります。同梱サンプルは design vocabulary（白地・角丸カード・2 段組の比較・ラインアイコン・強調 1 色）を示す手本画像です。
- **`outline.md` の audience / house-style / 各スライドの骨子** — 想定読者・文体・題材を書きます。ここが正本で、`prompts/*.md` は `prompt-build` が生成します（手で編集しません）。
