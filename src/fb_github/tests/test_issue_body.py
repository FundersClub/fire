from unittest.mock import Mock, PropertyMock, patch

from django.test import SimpleTestCase, override_settings

from fb_emails.models import IncomingMessage
from fb_github.models import Repository


class IssueBodyTests(SimpleTestCase):
    def create_issue(self, body, conversion_error=False):
        msg = IncomingMessage(subject="Synthetic email", body_text=body)
        github_repo = Mock(archived=False)
        github_repo.create_issue.return_value.as_dict.return_value = {"number": 1}
        github_repo.create_issue.return_value.number = 1
        with (
            patch.object(
                Repository,
                "gh_repo",
                new_callable=PropertyMock,
                return_value=github_repo,
            ),
            patch(
                "fb_github.models.msg_to_markdown",
                return_value=body,
                side_effect=ValueError("conversion failed")
                if conversion_error
                else None,
            ),
            patch("fb_github.models.Issue.objects.create") as save_issue,
        ):
            Repository().create_issue_from_incoming_msg(msg)
        github_repo.create_issue.assert_called_once()
        sent_body = github_repo.create_issue.call_args.kwargs["body"]
        self.assertEqual(save_issue.call_args.kwargs["body"], sent_body)
        self.assertEqual(msg.body_text, body)
        return sent_body

    def test_bodies_within_limit_are_unchanged(self):
        for length in (0, 65_535, 65_536):
            with self.subTest(length=length):
                body = "a" * length
                self.assertEqual(self.create_issue(body), body)

    def test_long_rendered_bodies_keep_prefix_and_note_within_limit(self):
        for body in ("a" * 65_537, "a" * 200_000, "😀é" * 40_000):
            with self.subTest(length=len(body)):
                sent_body = self.create_issue(body)
                self.assertEqual(len(sent_body), 65_536)
                prefix, note = sent_body.split("\n\n---\n")
                self.assertTrue(body.startswith(prefix))
                self.assertEqual(
                    note,
                    "Email truncated to fit GitHub's issue body limit. "
                    "See the original email for the full message.",
                )

    @override_settings(DEBUG=False)
    def test_text_fallback_also_gets_truncated(self):
        with self.assertLogs("fb_github.models", level="ERROR"):
            sent_body = self.create_issue(
                "fallback text " * 10_000, conversion_error=True
            )
        self.assertEqual(len(sent_body), 65_536)
        self.assertTrue(sent_body.startswith("fallback text "))
        self.assertIn("Email truncated", sent_body)
