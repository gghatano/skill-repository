# Source Independence Rule

「根拠が多い」ように見えて実は一つ、という状態を防ぐための規約。

- 同一原情報に由来する転載・プレスリリース再掲・翻訳・要約記事は、独立した根拠として数えない。
- 各情報源に `independence_cluster` を付与する。同一原情報に由来するものは同じ ID にする。
- 根拠の数を示す場合は、**情報源件数**と**独立クラスタ数**を区別して書く。
- 一次情報が同一で二次情報が複数ある場合、一次情報を優先して引用する。

## 判定

Lint `independence-count`（Phase 3 以降）が対応する。Phase 1 では
`sources.json` の `independence_cluster` を記録するところまでを必須とする。
