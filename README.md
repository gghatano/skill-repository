# skill-repository

`gghatano` が所有する GitHub リポジトリから `.claude/skills/**/SKILL.md` を探索し、
スキル本体と概要カタログを集約するリポジトリです。

## 生成物

- `skills/<repository>/<skill>/`: 出典リポジトリから同期したスキル一式
- `docs/skill-catalog.md`: スキル名、概要、出典を**出典リポジトリ順**でまとめた一覧
- `docs/skill-purpose-catalog.md`: 同じスキルを**目的（カテゴリ）別**に整理した一覧
- `docs/skill-porting-guide.md`: 各スキルを別プロジェクトへ持ち運ぶときの**移植チェックリスト**
- `docs/skill-duplication.md`: スキルが**複数リポジトリに重複**している状況（`common/` 集約候補）
- `docs/index.html`: 目的・移植情報を検索できる GitHub Pages
- `catalog/manifest.json`: 同期元と blob SHA、目的分類、移植性分析を記録した機械可読マニフェスト
- `catalog/categories.json`: スキル名から目的カテゴリへの対応を定義するタクソノミー
- `common/`: 共通部分の**正本**（役割ベースに汎化したスキル・規約・サブエージェント）
- `bundles/*.json`: 新しいリポジトリへ一括で引き込むスキルの**バンドル**定義

同じリポジトリ内に複数の `.claude` ディレクトリがある場合も探索します。スキルの
`SKILL.md` と同じディレクトリ以下にある `scripts/`、`references/`、`assets/` なども
まとめて同期します。

## 目的別の整理

単なる収集にとどめず、各スキルが「どういう目的のものか」を横断的に把握できるよう、
`catalog/categories.json` でスキル名を目的カテゴリに対応づけています。同期時にこの
対応表を読み込み、`docs/skill-purpose-catalog.md` と `manifest.json` の各エントリに
カテゴリを付与します。

複数リポジトリで共通利用されるスキル（`report-review` や `experiment-plan` など）は
同名なので、対応表はスキル**名**単位で1回定義すれば全リポジトリに反映されます。
新しいスキルが未分類のまま同期されると `未分類` カテゴリにまとめられ、同期時に警告を
出力します。カテゴリを追加・変更したいときは `catalog/categories.json` を編集してから
再生成してください。

GitHub へアクセスせずカタログ類だけを再生成する場合は、既存マニフェストから組み立て
直せます。

```bash
python3 scripts/sync_skills.py --from-manifest
```

## 共通部分と引き込み（新しいリポジトリで使う）

同じスキルが複数リポジトリに**乱立**していたため、共通で使えるものを **共通部分**と
**リポジトリ固有**に分けて整理しています。

- **共通部分** = `common/`（正本）: 役割ベースに汎化したスキル本体・規約・サブエージェント。
  特定プロジェクトのパスを直接持たず、規約 §1「役割→パス」表の役割名で参照する。
- **リポジトリ固有** = 各リポジトリの `.claude/`: 役割→パス表に埋める実際の値、そのリポジトリ
  だけのスキル。

`docs/skill-duplication.md` に、どのスキルが何リポジトリに重複し内容が何種類あるか（乱立の
度合い）を自動集計します。共通化の対象把握に使います。

新しい研究リポジトリを作ったら、`common/` から必要なスキルを引き込みます。

```bash
# 新しいリポジトリのルートで
python3 <skill-repository>/scripts/install_skills.py --list                 # 一覧
python3 <skill-repository>/scripts/install_skills.py --bundle research --into .   # 研究一式を引き込む
python3 <skill-repository>/scripts/install_skills.py --skill report-review --with-companions --into .  # 個別
```

`--dry-run` で確認、`--force` で既存ファイルを上書き（既定は既存を温存してスキップ）。
引き込み後、`.claude/docs/documentation-conventions.md` の役割→パス表を自リポジトリに合わせて
編集すれば、スキル本体（共通部分）は無編集で動きます。

## 移植性（portability）の分析

各スキルが別プロジェクトへどれだけそのまま持ち運べるかを、`SKILL.md` から検出した
パスの性質で自動判定します。検出パスは次の4種に分類されます。

- **同梱物（bundled）**: スキル自身の `references/`・`scripts/` など。一緒に運ばれるので調整不要。
- **パラメータ化済み（parameterized）**: `<...>`・`{{...}}`・`$ARGUMENTS`・glob を含む汎用パス。
- **同梱前提（companions）**: `.claude/`・`.agents/` など、兄弟のエージェント・知識ファイル。
- **外部依存（external）**: `config/assets.yaml` のような特定プロジェクト前提の具体パス。

これをもとに移植のしやすさを3段階（tier）で表します。

- **そのまま（portable）**: 同梱物とパラメータ化済みパスのみ。
- **同梱前提（companions）**: 兄弟ファイルを一緒にコピーする必要がある。
- **要調整（rework）**: 外部依存パスがあり、コピー先に合わせた読み替えが必要。

`docs/skill-porting-guide.md` に、要調整・同梱前提のスキルごとの読み替え対象と必要
ツールをチェックリストとして出力します。`manifest.json` の各エントリには内訳を含む
`portability` オブジェクトが入り、`docs/index.html` では tier で絞り込めます
（旧来の `portability_review` は `portable→candidate`／それ以外→`required` として残しています）。

## 同期

Python 3.11 以降と、対象リポジトリを参照できる GitHub CLI 認証が必要です。

```bash
gh auth status
python3 scripts/sync_skills.py
python3 -m unittest discover -s tests -v
```

特定リポジトリだけを確認する場合は `--repo` を指定します。

```bash
python3 scripts/sync_skills.py --repo owner/repository --dry-run
```

同期は全件取得に成功してから生成物を置き換えます。権限不足や API エラーがあった
場合、途中までの不完全なカタログは保存しません。

## 定期更新

`.github/workflows/sync-skills.yml` が毎週月曜日と手動実行時に同期 PR を作成します。
public repository だけを対象にする場合は `GITHUB_TOKEN` で動作します。private
repository も対象にする場合は、読み取り権限を持つ fine-grained personal access token
を Actions secret `SKILL_SOURCE_TOKEN` に登録してください。

新しいスキルは各プロジェクトの `.claude/skills/<skill-name>/SKILL.md` に追加します。
次回同期時に自動でカタログへ反映されます。

`main` 更新時は `.github/workflows/deploy-pages.yml` が `docs/` を GitHub Pages に
デプロイします。HTML では、同梱ファイル、外部ツール、プロジェクト固有パス、
同名スキルのバリエーション、project/personal の配置コマンドを確認できます。
