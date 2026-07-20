# common — 共通部分（正本）

複数の研究リポジトリに**乱立していた**同名スキルを、**共通部分**として1つに集約した
正本です。新しい研究リポジトリを作るときは、ここから必要なスキルを引き込みます。

## 共通 と 固有 の分け方

| | 置き場所 | 例 |
| --- | --- | --- |
| **共通部分** | この `common/`（正本） | 役割ベースに汎化したスキル本体・規約・サブエージェント |
| **リポジトリ固有** | 各リポジトリの `.claude/` | `documentation-conventions.md` §1「役割→パス」表に埋める実際のパス、そのリポジトリだけのスキル |

スキル本体は特定プロジェクトのパスを直接持たず、規約 §1 の**役割名**で参照します。
移植先では役割→パス表の値だけを差し替えれば、スキル本体を編集せずに動きます。

## 構成

- `skills/<skill>/SKILL.md` — 汎化済みスキルの正本
- `docs/documentation-conventions.md` — 共通規約（役割→既定パス表を含む）
- `agents/*.md` — 共通サブエージェント（planner / implementer / reviewer）

## 引き込み方（新しい研究リポジトリで）

```bash
# 新しいリポジトリのルートで実行
python3 <skill-repository>/scripts/install_skills.py --bundle research --into .
```

`.claude/skills/` に共通スキルが、`.claude/docs/`・`.claude/agents/` に同梱物が配置されます。
配置後、`.claude/docs/documentation-conventions.md` の役割→パス表を自リポジトリに合わせて
編集してください。

## 正本の更新

`common/` はいまのところ手動でキュレーションします（初期値は汎化済みの `dpsynth-demo`
版から作成）。出典リポジトリ側でスキルを改善したら、その汎化版をここへ反映します。
`docs/skill-duplication.md` に、どのスキルが何リポジトリに重複しているか（乱立の度合い）を
自動集計しているので、共通化の対象を把握できます。
