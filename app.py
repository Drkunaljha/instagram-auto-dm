from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

CONFIG = {
    "ACCESS_TOKEN": "EAALkomMWsxEBQ7vqtu3wh8ZBDSTZCWoznNUlZAOikAzv0dNSlcTFk41M74jIA6ohXzJGqdDUUoPpfX9DkcOUUe8dr6VySoRbK4YpGtT5Nyl3R3oP35CYvBgEe21Pa7kERHJAXJBDm6S3tCioTod1etPL7qHwU3fBnuMgKL0k2taaZBphrucK8hVjNp0JLgCm52gqL39c5qdte9UXyMFofXIlkKDhb2ZCjMWHLiLos5DDOzuwMvxRnMcrCZAaIShUuwax5WZCmIaokxbKiGG0rKP",
    "VERIFY_TOKEN": "my_secret_token_123",
    "INSTAGRAM_ACCOUNT_ID": "17841442329015303",
    "KEYWORD_FILTER_ON": False,
    "TRIGGER_KEYWORDS": ["info", "link", "send", "chahiye", "details", "price", "dm"],
    "AUTO_DM_MESSAGE": "Heyyy! Shukriya comment karne ke liye! Ye lo jo tum dhundh rahe the: https://your-link-here.com Koi bhi sawaal ho to reply karo!",
    "SEND_PUBLIC_REPLY": True,
    "PUBLIC_REPLY_TEXT": "Shukriya! Check your DMs for more info!",
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

def send_auto_dm(user_id, username=""):
    if user_id in already_dm_sent:
        log_message(f"Already sent DM to {username} - Skipping")
        return False
    url = f"https://graph.instagram.com/v18.0/{CONFIG['INSTAGRAM_ACCOUNT_ID']}/messages"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": CONFIG["AUTO_DM_MESSAGE"]},
        "access_token": CONFIG["ACCESS_TOKEN"]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            already_dm_sent.add(user_id)
            log_message(f"DM sent to @{username}")
            return True
        else:
            log_message(f"DM error: {response.json()}")
            return False
    except Exception as e:
        log_message(f"DM exception: {str(e)}")
        return False

def send_public_reply(comment_id):
    if not CONFIG["SEND_PUBLIC_REPLY"]:
        return
    url = f"https://graph.instagram.com/v18.0/{comment_id}/replies"
    payload = {
        "message": CONFIG["PUBLIC_REPLY_TEXT"],
        "access_token": CONFIG["ACCESS_TOKEN"]
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
    log_message(f"Webhook verification - Token: {token}")
    if mode == 'subscribe' and token == CONFIG["VERIFY_TOKEN"]:
        log_message("Webhook Verified!")
        return challenge, 200
    log_message("Webhook Verification FAILED!")
    return "Forbidden", 403

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.get_json()
    try:
        if data.get('object') == 'instagram':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('field') == 'comments':
                        comment_data = change.get('value', {})
                        comment_text = comment_data.get('text', '')
                        commenter_id = comment_data.get('from', {}).get('id', '')
                        commenter_name = comment_data.get('from', {}).get('username', 'Unknown')
                        comment_id = comment_data.get('id', '')
                        log_message(f"New Comment from @{commenter_name}: {comment_text[:50]}")
                        if contains_keyword(comment_text):
                            dm_sent = send_auto_dm(commenter_id, commenter_name)
                            if dm_sent and comment_id:
                                send_public_reply(comment_id)
    except Exception as e:
        log_message(f"Webhook error: {str(e)}")
    return jsonify({"status": "ok"}), 200

@app.route('/')
def home():
    return jsonify({
        "status": "Bot is RUNNING!",
        "total_dms_sent": len(already_dm_sent),
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
