# Human Intervention Rule

自動処理せず人間へ引き渡す事項。

- CAPTCHA
- ログイン、多要素認証
- 利用規約への同意
- 有料購入
- 機微情報の外部送信判断
- 法的判断
- 情報源間の重大な未解決対立

## 扱い

該当した時点で `run.json` の `status` を `needs_human` にし、
`human_actions_required` に「何が必要か」「どのファイルで止まっているか」を記録して停止する。

回避を試みない。認証情報の推測、CAPTCHA の自動解答、規約同意の代行を行わない。
