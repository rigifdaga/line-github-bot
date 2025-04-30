import unittest
from unittest.mock import patch, Mock

import requests
from app import app, send_line_message
import json

class TestBot(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    @patch('app.requests.post')
    def test_send_line_message_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "OK"

        send_line_message("Tes kirim pesan")
        mock_post.assert_called_once()

        args, kwargs = mock_post.call_args
        self.assertIn('Authorization', kwargs['headers'])
        self.assertIn('messages', kwargs['data'])

    @patch('app.requests.post', side_effect=requests.exceptions.Timeout)
    def test_send_line_message_timeout(self, mock_post):
        # Hanya memastikan tidak ada exception saat timeout
        try:
            send_line_message("Timeout test")
        except Exception:
            self.fail("send_line_message should handle Timeout exception gracefully.")

    @patch('app.requests.post', side_effect=requests.exceptions.RequestException("Network Error"))
    def test_send_line_message_request_exception(self, mock_post):
        try:
            send_line_message("Error test")
        except Exception:
            self.fail("send_line_message should handle RequestException gracefully.")

    @patch('app.send_line_message')
    def test_github_webhook_pull_request(self, mock_send):
        payload = {
            "action": "opened",
            "pull_request": {
                "title": "Add feature X",
                "html_url": "http://github.com/example/pr/1"
            },
            "sender": {
                "login": "username"
            }
        }

        response = self.client.post(
            "/github-webhook",
            json=payload,
            headers={"X-GitHub-Event": "pull_request"}
        )

        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once()

    @patch('app.send_line_message')
    def test_github_webhook_comment(self, mock_send):
        payload = {
            "comment": {
                "body": "Looks good!",
                "html_url": "http://github.com/example/comment/1"
            },
            "sender": {
                "login": "username"
            }
        }

        response = self.client.post(
            "/github-webhook",
            json=payload,
            headers={"X-GitHub-Event": "issue_comment"}
        )

        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once()

    def test_line_webhook_receives_post(self):
        payload = {
            "events": [{
                "type": "message",
                "message": {"type": "text", "text": "Hello"}
            }]
        }

        response = self.client.post(
            "/callback",
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "OK")

if __name__ == '__main__':
    unittest.main()
