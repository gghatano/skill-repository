# Adapters — HOW TO EXECUTE

Skill は **WHAT TO DO**（作業パターン）だけを定義し、特定エージェント製品の API を持たない。
Adapter は各実行環境で Workflow/Skill を **どう実行するか**を埋める層。

これにより、Coding Agent 製品が変わっても Skill Library / Workflow Library はそのまま使える。

## Adapter が解決する主な差分

| 抽象操作（Skill/Workflow 側の要求） | Adapter が対応づける実行手段 |
| --- | --- |
| 独立サブエージェントを N 体並列起動 | 製品ごとの sub-agent 起動 API |
| Context 隔離（レビュアー間で出力非共有） | 別プロセス/別セッション/Context リセット |
| バリア（全並列完了を待って統合） | 製品の待ち合わせ機構、または逐次化 |
| ループの上限回数（max_iterations） | オーケストレータ側のループ制御 |
| モデルティア（planner=上位 / implementer=下位） | 製品のモデル指定 |
| 成果物ファイルの受け渡し | リポジトリ上の実ファイル（共通・製品非依存） |

## 収録 Adapter

- [`claude-code/`](./claude-code/) — Task tool のサブエージェント、worktree 隔離、モデル指定
- [`codex/`](./codex/) — sub-agent 機構での並列/逐次実行
- [`generic/`](./generic/) — サブエージェントを持たない環境向けの逐次隔離実行

## 原則

- Adapter は Skill の**手順を変えない**。起動・隔離・待ち合わせの**実行方法だけ**を埋める。
- 並列 Agent が使えない環境でも、Context をリセットしながら逐次実行すれば独立性は保てる
  （速度は落ちるが構造は同じ）。
- 成果物駆動なので、途中まで別 Adapter で実行し、続きを別 Adapter で回すこともできる。
