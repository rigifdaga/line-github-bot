from flask import Flask, request
from pyngrok import ngrok
import requests
import json
import os

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

app = Flask(__name__)

def send_line_message(message):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    body = {
        'to': LINE_USER_ID,
        'messages': [{
            'type': 'text',
            'text': message
        }]
    }
    r = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, data=json.dumps(body))
    print(f"LINE response: {r.status_code} {r.text}")

@app.route("/github-webhook", methods=["POST"])
def github_webhook():
    event = request.headers.get('X-GitHub-Event')
    payload = request.json

    if event == 'pull_request':
        action = payload['action']
        title = payload['pull_request']['title']
        user = payload['sender']['login']
        url = payload['pull_request']['html_url']
        send_line_message(f"[PR {action}] {title} oleh {user}\n{url}")

    elif event == 'issue_comment':
        comment = payload['comment']['body']
        user = payload['sender']['login']
        url = payload['comment']['html_url']
        send_line_message(f"[Komentar] oleh {user}: {comment}\n{url}")

    return '', 200

@app.route("/callback", methods=["POST"])
def line_webhook():
    body = request.get_json()
    print("📥 Event dari LINE:")
    print(json.dumps(body, indent=2)) 

    return 'OK', 200

if __name__ == "__main__":
    public_url = ngrok.connect(5000)
    print(f"🌐 Ngrok tunnel running at: {public_url}/github-webhook")
    app.run(port=5000)
