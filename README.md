# textdiffedit

取得したテキストの指定行を置換し、差分を確認してから更新する CLI。最初の provider は GitHub の PR 本文と Issue 本文です。Python 3.10 以降と、認証済みの `gh` が必要です。

## Homebrew でインストール

PR マージ後に最初のリリースが公開されたら、次の一行でインストールできます。

```bash
brew install s4na/try-s4na-tap/textdiffedit
gh auth login
textdiffedit --help
```

Homebrew が Python と `gh` を依存としてインストールします。

公開ワークフローには、`s4na/homebrew-try-s4na-tap` の Contents 書き込み権限を持つ fine-grained token を、このリポジトリの Actions secret `HOMEBREW_TAP_TOKEN` に登録してください。main へのマージ後にテスト、GitHub Release 作成、tap Formula 更新を順に実行します。

```bash
textdiffedit gh-pr-body https://github.com/OWNER/REPO/pull/123 \
  --replace 12:15 --expect old.md --with new.md

textdiffedit gh-issue-body https://github.com/OWNER/REPO/issues/456 \
  --replace 4:4 --expect old.md --with new.md
```

行番号は 1 始まりで両端を含みます。`old.md` には置換前の行を正確に、`new.md` には置換後の行を書きます。途中の行を置換するときは両ファイルの末尾改行も含めてください。差分を表示し、`y` を入力すると更新します。`--yes` で対話を省略できます。

指定行が `old.md` と一致しない場合や、確認中にリモート本文が変わった場合は中止します。GitHub API の更新は全文送信であり、更新直前の再取得と送信の間に他者が編集した場合の競合は完全には防げません。

```bash
python -m unittest discover -s tests
```

## 開発時の検証

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -W error -m unittest discover -s tests
```

GitHub Actions で PR と main への push ごとに同じ lint・テストを実行します。
