import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from textdiffedit.cli import EditError, GitHubBody, main, render_diff, replace_lines


class ReplaceTests(unittest.TestCase):
    def test_replaces_only_selected_lines(self):
        self.assertEqual(replace_lines("a\nb\nc\n", "2:2", "b\n", "B\n"), "a\nB\nc\n")

    def test_rejects_stale_or_wrong_lines(self):
        with self.assertRaises(EditError):
            replace_lines("a\nb\n", "2:2", "c\n", "B\n")

    def test_rejects_broken_boundary(self):
        with self.assertRaises(EditError):
            replace_lines("a\nb\n", "1:1", "a\n", "A")

    def test_accepts_last_line_without_newline(self):
        self.assertEqual(replace_lines("a\nb", "2:2", "b", "B"), "a\nB")

    def test_diff_marks_missing_final_newline(self):
        diff = render_diff("a\nold", "a\nnew")
        self.assertIn("-old\n\\ No newline at end of file\n+new", diff)

    def test_provider_kind_must_match_url(self):
        with self.assertRaises(EditError):
            GitHubBody("gh-issue-body", "https://github.com/a/b/pull/1")

    @patch("subprocess.run")
    def test_provider_sends_json_body(self, run):
        run.return_value.stdout = '{"body":"a"}'
        provider = GitHubBody("gh-pr-body", "https://github.com/a/b/pull/1")
        self.assertEqual(provider.fetch(), "a")
        provider.update("new\nbody")
        self.assertIn("github.com", run.call_args.args[0])
        self.assertEqual(run.call_args.kwargs["encoding"], "utf-8")
        self.assertEqual(run.call_args.kwargs["input"], '{"body": "new\\nbody"}')


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.old = root / "old.md"
        self.new = root / "new.md"
        self.old.write_bytes("旧文\r\n".encode("utf-8"))
        self.new.write_bytes("新文\r\n".encode("utf-8"))
        self.args = ["gh-issue-body", "https://github.com/a/b/issues/1",
                     "--replace", "1:1", "--expect", str(self.old), "--with", str(self.new)]

    @patch("textdiffedit.cli.GitHubBody")
    def test_preserves_crlf_and_unicode(self, factory):
        provider = factory.return_value
        provider.fetch.return_value = "旧文\r\nそのまま\r\n"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(self.args + ["--yes"]), 0)
        provider.update.assert_called_once_with("新文\r\nそのまま\r\n")

    @patch("textdiffedit.cli.GitHubBody")
    @patch("builtins.input", return_value="n")
    def test_declining_does_not_update(self, prompt, factory):
        provider = factory.return_value
        provider.fetch.return_value = "旧文\r\n"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(self.args), 1)
        provider.update.assert_not_called()

    @patch("textdiffedit.cli.GitHubBody")
    @patch("sys.stderr", new_callable=io.StringIO)
    def test_concurrent_change_does_not_update(self, stderr, factory):
        provider = factory.return_value
        provider.fetch.side_effect = ["旧文\r\n", "他者の編集\r\n"]
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(self.args + ["--yes"]), 1)
        self.assertIn("Remote text changed", stderr.getvalue())
        provider.update.assert_not_called()


if __name__ == "__main__":
    unittest.main()
