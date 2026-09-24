import unittest
from unittest.mock import patch

from textdiffedit.cli import EditError, GitHubBody, replace_lines


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

    def test_provider_kind_must_match_url(self):
        with self.assertRaises(EditError):
            GitHubBody("gh-issue-body", "https://github.com/a/b/pull/1")

    @patch("subprocess.run")
    def test_provider_sends_json_body(self, run):
        run.return_value.stdout = '{"body":"a"}'
        provider = GitHubBody("gh-pr-body", "https://github.com/a/b/pull/1")
        self.assertEqual(provider.fetch(), "a")
        provider.update("new\nbody")
        self.assertEqual(run.call_args.kwargs["input"], '{"body": "new\\nbody"}')


if __name__ == "__main__":
    unittest.main()
