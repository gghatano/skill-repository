# skill-repository

**汎用的に使える Claude Skills を、目的別プラグインとして配布するリポジトリ。**
必要なスキルを `/plugin` の2コマンドで、どのリポジトリにも引き込めます。

複数リポジトリに散らばっていたスキルのうち再利用できるものを役割ベースに汎化し、
スキル本体・規約・サブエージェントを**自己完結**でまとめた4つのプラグインにしています。

- 🔌 目的別に選べる **4プラグイン**（dev / generation / research / writing）
- ⚡ `/plugin` の**2コマンド**で導入、必要なものだけ
- 🔎 一覧・検索できる Pages → **https://gghatano.github.io/skill-repository/**

---

## 使い方

Claude Code のプロンプトで、マーケットプレイスを追加し、欲しいプラグインを入れるだけ。

```
/plugin marketplace add gghatano/skill-repository   # 初回のみ
/plugin install research@gghatano-skills            # 目的のプラグインを導入
```

導入後、スキルは名前空間付き **`/<plugin>:<skill>`**（例 `/research:report-review`）で呼び出せます。
規約付きのプラグインは、`docs/*-conventions.md` の「役割 → パス」表を自リポジトリに合わせて
調整すれば、スキル本体は無編集で動きます。

### プラグイン

| プラグイン | 用途 | 導入コマンド |
| --- | --- | --- |
| `dev` | 開発ワークフロー（Git / Issue / PR） | `/plugin install dev@gghatano-skills` |
| `generation` | 仕様駆動 生成・評価サイクル | `/plugin install generation@gghatano-skills` |
| `research` | 研究レポート作成ライフサイクル（規約・サブエージェント同梱） | `/plugin install research@gghatano-skills` |
| `writing` | 文章・日本語ライティング（自己完結） | `/plugin install writing@gghatano-skills` |

各プラグインの詳細は `plugins/<name>/README.md` を参照してください。

---

## 仕組み（メンテナンス向け）

普段の利用には不要です。スキルの収集・カタログ生成・配布物のメンテナンスに関する説明です。

### 構成

- `plugins/<name>/`: 配布用の**プラグイン**（`.claude-plugin/plugin.json` ＋ `skills/` ＋ 任意で `docs/`・`agents/`）
- `.claude-plugin/marketplace.json`: 4プラグインを掲載する**マーケットプレイス** `gghatano-skills`
- `skills/<repository>/<skill>/`: 出典リポジトリから同期したスキル一式（横断カタログの素材）
- `docs/`: 横断カタログと GitHub Pages（下記）
- `catalog/manifest.json` / `catalog/categories.json`: 機械可読マニフェストと目的タクソノミー
- `catalog/skill-details.json`: 各スキルの詳細ページ（できること・使いどころ・入出力）用の要約

### スキルの収集とカタログ

`gghatano` が所有する GitHub リポジトリから `.claude/skills/**/SKILL.md` を探索し、スキル本体と
横断カタログを集約します（`SKILL.md` と同ディレクトリの `scripts/`・`references/`・`assets/` も同期）。
生成物:

- `docs/skill-catalog.md`: スキル名・概要・出典を**出典リポジトリ順**でまとめた一覧
- `docs/skill-purpose-catalog.md`: **目的（カテゴリ）別**に整理した一覧
- `docs/skill-porting-guide.md`: 別プロジェクトへ持ち運ぶときの**移植チェックリスト**
- `docs/skill-duplication.md`: スキルが**複数リポジトリに重複**している状況（プラグイン集約候補）
- `docs/skills/<name>.html`: 各スキルの**詳細ページ**（できること・使いどころ・入出力）。Pages のスキル一覧からリンク

目的分類は `catalog/categories.json` でスキル**名**単位に定義し、同期時にカタログとマニフェストへ
付与します。未分類のスキルは `未分類` にまとめ、同期時に警告します。

### 移植性（portability）の分析

各スキルの持ち運びやすさを、`SKILL.md` から検出したパスの性質で3段階に自動判定します。
検出パスは **同梱物 / パラメータ化済み / 同梱前提 / 外部依存** に分類し、tier は
**そのまま（portable）/ 同梱前提（companions）/ 要調整（rework）** で表します。詳細と読み替え
対象は `docs/skill-porting-guide.md`、内訳は `manifest.json` の `portability` に入ります。

### 同期・再生成

Python 3.11 以降と、対象リポジトリを参照できる GitHub CLI 認証が必要です。

```bash
gh auth status
python3 scripts/sync_skills.py                          # 全リポジトリを同期して再生成
python3 scripts/sync_skills.py --repo owner/repo --dry-run   # 特定リポジトリだけ確認
python3 scripts/sync_skills.py --from-manifest          # GitHub を叩かず既存マニフェストから再生成
python3 -m unittest discover -s tests -v
```

同期は全件取得に成功してから生成物を置き換えます（途中失敗時の不完全なカタログは保存しません）。

### GitHub Pages（HTML）

`docs/index.html` は `web/index.template.html`（Apple 調・Tailwind CSS）にカタログデータを差し込んで
生成します。各スキルの詳細ページ `docs/skills/<name>.html` は `web/skill-detail.template.html` に
`catalog/skill-details.json` の要約を流し込んで生成し、一覧のスキル名からリンクします。スタイルは
`docs/tailwind.css` にビルド済みで同梱し、テンプレートのクラスを変更したときだけ再ビルドします
（npm レジストリへのアクセスが必要）。

```bash
./web/build-css.sh   # docs/tailwind.css を再生成
```

### 定期更新

`.github/workflows/sync-skills.yml` が毎週月曜と手動実行時に同期 PR を作成します。private リポジトリも
対象にする場合は、読み取り権限を持つ fine-grained PAT を Actions secret `SKILL_SOURCE_TOKEN` に登録して
ください。`main` 更新時は `.github/workflows/deploy-pages.yml` が `docs/` を GitHub Pages にデプロイします。
新しいスキルは各プロジェクトの `.claude/skills/<skill-name>/SKILL.md` に追加すれば、次回同期で反映されます。
