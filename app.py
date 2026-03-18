from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

ACCOUNTS = [
    {
        "ACCESS_TOKEN": "IGAANmfnNUxjVBZAFlfUURBZAFJmWUsxTDRJZAk1hYlhWRlFSd3loWkc0ajRGU2ZA0SzZAVbjhyRXdkenc1ZATNITmhhRHZAhRm5IdzJkeWJGdkdpMEF6Q0JZAOV9OOU1mZAVNxdjg3TVZAnemdPUDFSQlZAxcWw5bHoxdk5yVk83Y2VHNXNGQQZDZD",
        "INSTAGRAM_ACCOUNT_ID": "17841442329015303",
        "AUTO_DM_MESSAGE": "Heyyy! Shukriya comment karne ke liye! Ye lo jo tum dhundh rahe the: https://your-link-here.com Koi bhi sawaal ho to reply karo!",
        "PUBLIC_REPLY_TEXT": "Shukriya! Check your DMs for more info!",
    },
    {
        "ACCESS_TOKEN": "EAALkomMWsxEBQxBrpXaa0jZC67Nm3iN5wNdZCXfZBqZBmD6zkHcGsA4QYSaUKilMkRfi93GiAi4UG2iekC7AxfQZAd3cdZB5jgrz4sIgkt7bjxYlHxAYjpVMFZAwteqoh9ZAGfTpjPYsYH43DjMu6DL13rIRCIelgZAQ7XqmxanESDtlIUndTMT71a2JX7ZBM125OtPfYZCdByeDAzdyyLCig5Mb5Gt9DjdBlBnaWMwsnUoiNZCYQ9imjKPsG0rJZCHztaaQnlZArNwn7MjihTCEgasKs7",
        "INSTAGRAM_ACCOUNT_ID": "25673523418993611",
        "AUTO_DM_MESSAGE": "Heyyy! Shukriya comment karne ke liye! Ye lo jo tum dhundh rahe the: https://your-link-here.com Koi bhi sawaal ho to reply karo!",
        "PUBLIC_REPLY_TEXT": "Shukriya! Check your DMs for more info!",
    }
]

CONFIG = {
    "VERIFY_TOKEN": "my_secret_token_123",
    "KEYWORD_FILTER_ON": False,
    "TRIGGER_KEYWORDS": ["info", "link", "send", "chahiye", "details", "price", "dm"],
    "SEND_PUBLIC_REPLY": True,
}

app = Flask(__name__)
already_dm_sent = set()

def log_message(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def contains_keyword(comment_text):
    if not CONFIG["KEYWORD_FILTER_ON"]:
        return True
    comment_lower = comment_text.lower()
    for keyword in CONFIG["TRIGGER_KEYWORDS"]:
        if keyword.lower() in comment_lower:
            return True
    return False

def get_account(account_id):
    for acc in ACCOUNTS:
        if acc["INSTAGRAM_ACCOUNT_ID"] == account_id:
            return acc
    return ACCOUNTS[0]

def send_auto_dm(user_id, username="", account=None):
    if account is None:
        account = ACCOUNTS[0]
    key = f"{account['INSTAGRAM_ACCOUNT_ID']}_{user_id}"
    if key in already_dm_sent:
        log_message(f"Already sent DM to {username} - Skipping")
        return False
    url = f"https://graph.instagram.com/v18.0/{account['INSTAGRAM_ACCOUNT_ID']}/messages"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": account["AUTO_DM_MESSAGE"]},
        "access_token": account["ACCESS_TOKEN"]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            already_dm_sent.add(key)
            log_message(f"DM sent to @{username}")
            return True
        else:
            log_message(f"DM error: {response.json()}")
            return False
    except Exception as e:
        log_message(f"DM exception: {str(e)}")
        return False

def send_public_reply(comment_id, account=None):
    if not CONFIG["SEND_PUBLIC_REPLY"]:
        return
    if account is None:
        account = ACCOUNTS[0]
    url = f"https://graph.instagram.com/v18.0/{comment_id}/replies"
    payload = {
        "message": account["PUBLIC_REPLY_TEXT"],
        "access_token": account["ACCESS_TOKEN"]
    }
    try:
        requests.post(url, params=payload)
    except Exception as e:
        log_message(f"Public reply exception: {str(e)}")

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == CONFIG["VERIFY_TOKEN"]:
        log_message("Webhook Verified!")
        return challenge, 200
    return "Forbidden", 403

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.get_json()
    try:
        if data.get('object') == 'instagram':
            for entry in data.get('entry', []):
                entry_id = entry.get('id', '')
                account = get_account(entry_id)
                for change in entry.get('changes', []):
                    if change.get('field') == 'comments':
                        comment_data = change.get('value', {})
                        comment_text = comment_data.get('text', '')
                        commenter_id = comment_data.get('from', {}).get('id', '')
                        commenter_name = comment_data.get('from', {}).get('username', 'Unknown')
                        comment_id = comment_data.get('id', '')
                        log_message(f"New Comment from @{commenter_name}: {comment_text[:50]}")
                        if contains_keyword(comment_text):
                            dm_sent = send_auto_dm(commenter_id, commenter_name, account)
                            if dm_sent and comment_id:
                                send_public_reply(comment_id, account)
    except Exception as e:
        log_message(f"Webhook error: {str(e)}")
    return jsonify({"status": "ok"}), 200

@app.route('/')
def home():
    return jsonify({
        "status": "Bot is RUNNING!",
        "accounts_connected": len(ACCOUNTS),
        "total_dms_sent": len(already_dm_sent),
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
