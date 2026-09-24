# textdiffedit

取得したテキストの指定行を置換し、差分を確認してから更新する CLI。最初の provider は GitHub の PR 本文と Issue 本文です。Python 3.10 以降と、認証済みの `gh` が必要です。

```bash
python -m textdiffedit gh-pr-body https://github.com/OWNER/REPO/pull/123 \
  --replace 12:15 --expect old.md --with new.md

python -m textdiffedit gh-issue-body https://github.com/OWNER/REPO/issues/456 \
  --replace 4:4 --expect old.md --with new.md
```

行番号は 1 始まりで両端を含みます。`old.md` には置換前の行を正確に、`new.md` には置換後の行を書きます。途中の行を置換するときは両ファイルの末尾改行も含めてください。差分を表示し、`y` を入力すると更新します。`--yes` で対話を省略できます。

指定行が `old.md` と一致しない場合や、確認中にリモート本文が変わった場合は中止します。GitHub API の更新は全文送信であり、更新直前の再取得と送信の間に他者が編集した場合の競合は完全には防げません。

```bash
python -m unittest discover -s tests
```
