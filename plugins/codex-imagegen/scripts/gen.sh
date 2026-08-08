#!/usr/bin/env bash
# Codex に画像を 1 枚ずつ依頼するバッチ。**作業ディレクトリを cwd にして実行する**
# （Codex は cwd の AGENTS.md を読むため）。テンプレートを scaffold した先で使う。
#
#   ./gen.sh 01-overview                 # 1 枚（第1巡）
#   ./gen.sh 01-overview "$(cat fb.txt)" # 1 枚（前回の出力への指摘を付けて再依頼）
#   ./gen.sh 01-overview 02-detail       # 指定した順に複数枚（指摘なし）
#   ./gen.sh                             # prompts/*.md 全部
#
# 第2引数に改行を含む文字列を渡すと「前回の出力への修正指示」として末尾に足す。
# 指摘の書き方は skill の references/feedback-patterns.md を見ること。
#
# 完全自動（承認・サンドボックスをバイパス）で回す。フラグ名は Codex のバージョン依存なので、
# 動かないときは `codex exec --help` で確認して CODEX_FLAGS を上書きする。
#   例: CODEX_FLAGS="--sandbox workspace-write" ./gen.sh
set -uo pipefail
cd "$(dirname "$0")"

CODEX="${CODEX:-codex}"
CODEX_FLAGS="${CODEX_FLAGS:---dangerously-bypass-approvals-and-sandbox}"

# 毎回添える念押し。AGENTS.md / STYLE.md に書いてあっても実測で守られないことが多い、
# **領域非依存で必ず効く項目だけ**をここに置く（多くしすぎると効きが薄れる）。
# 配色など各プロジェクト固有のルールはここに書かず STYLE.md に置く。
BASE='
## 徹底事項（AGENTS.md / STYLE.md の再確認）
- 文字を大きく。STYLE.md の文字サイズ下限を必ず満たす。入らないなら文字を縮めず要素を減らす。
- 日本語を助詞や 1 文字で折らない。文節ごとに inline-block で包むか <br> を自分で置く。要素間に空白を出さない。
- 絵文字・装飾記号・アイコンフォント・私用領域の文字を使わない（□ 豆腐が出る）。図形は SVG か罫線で描く。
- 中身の無い枠を並べない（文字化けに見える）。カードの高さは中身に合わせ、空洞を作らない。
- 同じ文言を 2 箇所に出さない。「最重要メッセージ」を図の中にそのまま貼らない。
- 枠から中身をはみ出させない（クリッピング禁止）。
- 線は 1 関係 1 本。端点はカードの縁に接続する。宙に浮いた線・二重の矢印を作らない。並列の列挙に矢印を使わない。
- 書き出したあと PNG を開いて、STYLE.md の「出力チェック」の項目を自分で確認する。'

run() {
  local stem="$1"
  local extra="${2:-}"
  local f="prompts/${stem}.md"
  [ -f "$f" ] || { echo "[失敗] prompt が無い: $f" >&2; return 1; }
  echo "=== $stem ==="

  local prompt
  prompt="$(cat "$f")${BASE}"
  if [ -n "$extra" ]; then
    prompt="${prompt}

## 前回の出力への修正指示（最優先。必ず反映する）
${extra}"
  fi

  rm -f "out/${stem}.png"
  "$CODEX" exec $CODEX_FLAGS "$prompt" >/dev/null 2>&1
  # codex の終了直後はファイルが見えないことがあるので少し待って確かめる
  for _ in 1 2 3; do
    [ -f "out/${stem}.png" ] && { echo "[ok] out/${stem}.png"; return 0; }
    sleep 2
  done
  echo "[失敗] $stem（PNG が出ていない）" >&2
  return 1
}

# 第2引数が改行を含む＝指摘テキスト、とみなす。それ以外は stem の並びとして扱う。
if [ "$#" -eq 2 ] && [ "${2}" != "${2%$'\n'*}" ]; then
  run "$1" "$2"
elif [ "$#" -ge 1 ]; then
  for s in "$@"; do run "$s"; done
else
  # 引数なし＝prompts/ 全部をファイル名順に。
  # 主役の 1〜2 枚を先に作りたいときは、その stem を先頭に引数で渡すこと（例: ./gen.sh 05-key 11-proof）。
  for f in prompts/*.md; do
    run "$(basename "$f" .md)"
  done
fi
echo "完了。preview.html をブラウザで開いて一覧を確認。"
