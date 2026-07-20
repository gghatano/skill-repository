# Portable Agentic Development Skills

AI コーディングエージェントを用いた開発で有効な **開発ループ構造** を、特定の
LLM・製品に依存しない **再利用可能な Skill 群** として定義するライブラリ。

個別プロジェクトごとに「調査 → 設計 → 実装 → テスト → レビュー → 修正 → 完了判定」の
やり方を毎回プロンプトへ書き下すのではなく、**汎用的な開発パターンを Skill として分離**し、
複数プロジェクト・複数エージェント環境へ持ち運べる状態を目指す。

想定利用環境: Claude Code / Codex / その他 Coding Agent / サブエージェントを持つ Agent Runtime。

## 中心思想

再利用する対象は **プロンプトそのものではない**。

- ❌ Prompt を再利用する
- ✅ **Development Pattern** を再利用する
- ❌ Agent を資産化する
- ✅ **Agentic Workflow** を資産化する

したがって本ライブラリの中心成果物は次の 3 つで、これらを分離することで
特定の Coding Agent 製品が変わっても **開発プロセス自体を再利用**できる。

```
Skill Library  +  Workflow Library  +  Execution Adapter
```

## 3 層モデル

エージェントの動作を 3 層に分離する。上の層は下の層を組み合わせて構成する。

```
Project Spec   何を作るか（要件・制約・入出力・完了条件）… プロジェクト固有
     ↓
Workflow       どの順序・構造で作業するか（Skill の組み合わせとループ）… 半再利用
     ↓
Skill          特定の作業パターンをどう実行するか … 完全再利用（プロジェクト知識を持たない）
```

- **Project Spec** … 各プロジェクト側に置く。`templates/project-spec.md` を雛形に作る。
- **Workflow** … `workflows/*.yaml`。Skill を並べ、ループ・停止条件・Context 共有範囲を定義する。
- **Skill** … `skills/**/SKILL.md`。単一の作業パターン。**ドメイン知識を持たない**。

### Skill / Workflow / Adapter の 3 分離

| 層 | 役割 | 例 |
| --- | --- | --- |
| **Skill** | WHAT TO DO（作業パターン） | `independent-review` |
| **Workflow** | 組み合わせ・ループ・Context 共有範囲 | `default-development.yaml` |
| **Adapter** | HOW TO EXECUTE（実行方法） | Claude Code の Task tool で 3 サブエージェント起動 |

Workflow を Skill の中に埋め込まないこと。例えば `test → fix → test` は `test` Skill ではなく
`test-and-fix` Composite Skill として定義する。こうすると `test` 単体でも使える。

## 設計原則

1. **Skill は「役割」ではなく「作業パターン」**。`frontend-agent` ではなく `implement` / `cross-review`。
2. **Skill と Domain Knowledge を分離**。「何を調べるか」は Spec、「どう調べるか」が Skill。
3. **生成と評価を分離**。実装・レビュー・テスト評価・完了判定は別 Skill（可能なら別 Agent）へ。
4. **独立探索フェーズを確保**。複数 Agent の初期探索は相互の出力を共有しない。
5. **LLM 評価より機械的検証を優先**。Static → Unit → Integration → Property → LLM → Human の順。
6. **成果物駆動**。Agent 間通信は自然言語チャットではなく成果物ファイル（`spec.md` / `plan.md` /
   `test-results.json` / `review.md` / `verification.md`）を介する。

## ディレクトリ構成

```
agentic-development-skills/
├── README.md
├── SCHEMA.md                    # 全 SKILL.md 共通のインターフェース定義
├── skills/
│   ├── core/                    # 単一の作業パターン
│   │   ├── explore/  plan/  implement/  test/
│   │   └── review/   fix/   verify/     integrate/
│   └── composite/               # Core を組み合わせたループ構造
│       ├── test-and-fix/  review-and-fix/  independent-review/
├── workflows/                   # Skill を並べた実行順序
│   └── default-development.yaml
├── adapters/                    # 各エージェント製品での実行方法
│   ├── claude-code/  codex/  generic/
├── templates/                   # 成果物の雛形
│   ├── project-spec.md  implementation-plan.md
│   ├── review-report.md verification-report.md
└── examples/
```

## 標準 Workflow（default-development）

```
Explore → Plan → Independent Plan Review → Implement → Test → Fix Loop
        → Independent Code Review → Fix Loop → Verify
```

並列 Agent を使える環境では Plan / Implementation を独立レビュアー複数で評価し Integrate する
（`workflows/default-development.yaml` と `adapters/` を参照）。

## 使い方

1. 対象プロジェクトで `templates/project-spec.md` を埋めて `spec.md` を作る。
2. `workflows/default-development.yaml`（または派生）を選ぶ。
3. 実行環境に合わせて `adapters/<agent>/` の手順で Workflow を回す。
4. 各 Skill は成果物ファイルを入出力し、次の Skill へ引き渡す。

## スコープ（この MVP に含むもの）

- Core Skills: `explore` `plan` `implement` `test` `review` `fix` `verify` `integrate`
- Composite Skills: `test-and-fix` `review-and-fix` `independent-review`
- Workflow: `default-development`
- Templates: `project-spec` `implementation-plan` `review-report` `verification-report`
- Adapters: `claude-code` `codex` `generic`

将来拡張（未実装）: `root-cause-analysis` `architecture-decision` `migration` `refactoring`
`performance-optimization` `security-review` `privacy-review` `documentation` `release`、
および Workflow 自体を評価・改善する仕組み。
