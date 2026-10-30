import io
import logging
from unittest.mock import Mock, PropertyMock, patch

from django.test import SimpleTestCase
from github3.exceptions import UnprocessableEntity
from requests import Response

from fb_emails.models import IncomingMessage
from fb_github.models import IssueDeliveryRejected, Repository, validation_details


class ValidationLoggingTests(SimpleTestCase):
    def error(self, errors):
        response = Response()
        response.status_code = 422
        response.json = lambda: {'message': 'Validation Failed', 'errors': errors}
        return UnprocessableEntity(response)

    def test_worker_console_keeps_safe_details_without_extra_formatter(self):
        error = self.error([{
            'resource': 'Issue', 'field': 'body', 'code': 'unprocessable',
            'message': 'body is too long (maximum is 65536 characters)',
        }, {
            'resource': 'PRIVATE_RESOURCE', 'field': 'PRIVATE_FIELD', 'code': 'PRIVATE_CODE',
            'message': 'PRIVATE_MESSAGE\nforged log line', 'value': 'PRIVATE_VALUE',
        }])
        repo = Repository(id=14)
        msg = IncomingMessage(id=1, subject='PRIVATE_SUBJECT')
        github_repo = Mock(archived=False)
        github_repo.create_issue.side_effect = error
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
        logger = logging.getLogger('fb_github.models')
        logger.addHandler(handler)
        try:
            with patch.object(Repository, 'gh_repo', new_callable=PropertyMock, return_value=github_repo), \
                    patch('fb_github.models.msg_to_markdown', return_value='PRIVATE_BODY'):
                self.assertIsNone(repo.create_issue_from_incoming_msg(msg))
        finally:
            logger.removeHandler(handler)
        output = stream.getvalue()
        self.assertIn("'github_status': 422", output)
        self.assertIn("'code': 'unprocessable'", output)
        self.assertIn("'reason': 'body-too-long'", output)
        self.assertIn("'issue_title_length': 15", output)
        self.assertIn("'issue_body_length': 12", output)
        self.assertIn('UnprocessableEntity: 422 Validation Failed', output)
        self.assertNotIn('PRIVATE', output)
        self.assertNotIn('forged log line', output)
        github_repo.create_issue.assert_called_once_with(title=msg.subject, body='PRIVATE_BODY')

    def test_malformed_provider_details_do_not_break_diagnostics(self):
        for errors in (None, 'PRIVATE', {'message': 'PRIVATE'}, [None, [], 'PRIVATE'],
                       [{'resource': [], 'field': {}, 'code': [], 'message': {}}]):
            with self.subTest(errors=errors):
                result = validation_details(self.error(errors))
                self.assertNotIn('PRIVATE', repr(result))
        self.assertEqual(validation_details(self.error([])), {'shape': 'list', 'count': 0, 'details': []})

    def test_details_are_bounded_and_do_not_copy_arbitrary_messages(self):
        error = self.error([{'resource': 'Issue', 'field': 'body', 'code': 'custom',
                            'message': 'body is too long PRIVATE'}] * 100)
        details = validation_details(error)
        self.assertEqual(details['count'], 100)
        self.assertEqual(len(details['details']), 10)
        self.assertTrue(all(d['reason'] == 'other' for d in details['details']))
        self.assertNotIn('PRIVATE', repr(details))

    def test_known_rejection_still_uses_named_status_without_error_log(self):
        error = self.error([{'resource': 'Issue', 'field': 'title', 'code': 'custom',
                            'message': 'title is too long'}])
        github_repo = Mock(archived=False)
        github_repo.create_issue.side_effect = error
        with patch.object(Repository, 'gh_repo', new_callable=PropertyMock, return_value=github_repo), \
                patch('fb_github.models.msg_to_markdown', return_value='body'), \
                self.assertNoLogs('fb_github.models', level='ERROR'):
            with self.assertRaises(IssueDeliveryRejected) as caught:
                Repository().create_issue_from_incoming_msg(IncomingMessage(subject='title'))
        self.assertEqual(caught.exception.status, IncomingMessage.Status.IssueTitleTooLong)
