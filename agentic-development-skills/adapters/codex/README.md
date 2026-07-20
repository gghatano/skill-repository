# Adapter: Codex

Skill/Workflow を Codex（sub-agent 機構を持つ Coding Agent）上で実行するための対応づけ。

## 抽象操作 → Codex

| 抽象操作 | Codex での実行 |
| --- | --- |
| 独立サブエージェント N 体 | sub-agent 機構で複数エージェントを起動 |
| Context 隔離 | sub-agent ごとに独立 Context。共有物のみ親から渡す |
| バリア | 全 sub-agent の完了を待って統合 |
| 並行実装の衝突回避 | 作業ディレクトリ/ブランチを分ける |
| モデルティア | sub-agent ごとのモデル指定（可能な範囲で） |
| 成果物受け渡し | リポジトリ上の成果物ファイル（製品非依存で共通） |

## 実行方針

- `independent-review` は sub-agent を観点数だけ起動し、相互に出力を渡さず並列実行 → 統合。
- sub-agent の並列度に制限がある場合は、Context を分けたまま**逐次**実行しても
  独立性（同一前提への非収束）は保てる。
- ループ（`test-and-fix` / `review-and-fix`）の反復制御は親エージェントが持つ。

## 配置

- Skill 本体（`SKILL.md`）は製品非依存なのでそのまま利用する。
- 実行手順のうち Codex 固有の部分（sub-agent 起動方法）だけをこの Adapter が担う。

> 注: Codex の sub-agent API 名は製品バージョンに依存する。本 Adapter は
> 「並列/逐次の隔離実行 → バリア → 統合」という**構造**を対応づける層であり、
> 具体的な API 呼び出しは利用中のバージョンに合わせて埋める。
