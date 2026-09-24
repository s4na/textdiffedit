# textdiffedit

取得したテキストの指定行を置換し、差分を確認してから更新する CLI。最初の provider は GitHub の PR 本文と Issue 本文です。Python 3.10 以降と、認証済みの `gh` が必要です。

## Homebrew でインストール

このリポジトリを非公式 tap として使います。初回は次の一行で tap の登録とインストールを行います（初回マージ後の Formula 更新完了が必要です）。

```bash
brew tap s4na/textdiffedit https://github.com/s4na/textdiffedit.git && brew install s4na/textdiffedit/textdiffedit
gh auth login
textdiffedit --help
```

Homebrew が Python と `gh` を依存としてインストールします。

tap 登録後は `brew install s4na/textdiffedit/textdiffedit` でインストールできます。更新は `brew update && brew upgrade s4na/textdiffedit/textdiffedit` です。

リポジトリ名が `homebrew-` で始まらないため、初回の `brew tap` にはURL指定が必要です。

## 使い方

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

## Formula の自動更新

main へのpush時に、そのコミットがmainにマージ済みのPRのマージコミットと一致するかを確認します。一致したときだけGHAがアーカイブを取得し、そのURL・バージョン・SHA-256を `Formula/textdiffedit.rb` に書き込んで main にコミットします。単なるPRのcloseや通常の直接pushでは更新しません。アーカイブはFormula更新コミットではなくマージコミットを参照するため、ハッシュの自己参照を避けられます。

標準の `GITHUB_TOKEN` の `contents: write` と `pull-requests: read` を使用します。別リポジトリ・追加secret・GitHub Releaseは不要です。mainへのbotのpushを禁止するブランチ保護がある場合は、この更新も拒否されます。

新しいマージでmainが進んでいる場合や、更新済みのマージを再実行した場合はスキップします。バージョンはこのワークフローの実行番号を使った `0.1.<run_number>` です。
