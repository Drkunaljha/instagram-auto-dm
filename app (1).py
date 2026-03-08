"""
╔══════════════════════════════════════════════════════════════════╗
║     INSTAGRAM AUTO DM BOT - Comment se Auto DM Bhejne wala     ║
║     Made with Python + Flask + Instagram Graph API              ║
╚══════════════════════════════════════════════════════════════════╝

📌 YE CODE KYA KARTA HAI:
   1. Instagram ke comments ko sunता hai (Webhook)
   2. Jab bhi koi comment kare → automatically DM bhejta hai
   3. Same user ko baar-baar DM nahi jaata (duplicate protection)
   4. Keyword filter — sirf kuch specific words pe DM bhejo
"""

from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

# ═══════════════════════════════════════════════════
#  ⚙️  CONFIGURATION — YAHAN APNI VALUES DAALO
# ═══════════════════════════════════════════════════
CONFIG = {
    # Facebook Developer Console se milega
    "ACCESS_TOKEN": "YOUR_INSTAGRAM_ACCESS_TOKEN",
    
    # Webhook verify karne ke liye — koi bhi secret word rakh sakte ho
    "VERIFY_TOKEN": "my_secret_token_123",
    
    # Tumhara Instagram Business Account ID
    "INSTAGRAM_ACCOUNT_ID": "YOUR_INSTAGRAM_ACCOUNT_ID",
    
    # ─────────────────────────────────────────
    # 🎯 DM SETTINGS
    # ─────────────────────────────────────────
    
    # Kya sirf specific keywords pe DM bhejein?
    # True = sirf keywords wale comments pe DM
    # False = SABHI comments pe DM bhejo
    "KEYWORD_FILTER_ON": False,
    
    # Agar KEYWORD_FILTER_ON = True hai, to ye keywords likho
    # Jab koi in words se comment kare, tabhi DM jaayega
    "TRIGGER_KEYWORDS": ["info", "link", "send", "chahiye", "details", "price", "dm"],
    
    # Woh DM message jo automatically jaayega
    "AUTO_DM_MESSAGE": """Heyyy! 👋

Shukriya comment karne ke liye! 😊

Ye lo jo tum dhundh rahe the 👇
🔗 https://your-link-here.com

Koi bhi sawaal ho to reply karo!
Hum zaroor help karenge 🙏

— Team ❤️""",
    
    # Post comment ke baad public reply bhi karna hai? (Optional)
    "SEND_PUBLIC_REPLY": True,
    "PUBLIC_REPLY_TEXT": "Shukriya! 🙏 Check your DMs for more info 📩",
}

# ═══════════════════════════════════════════════════
#  FLASK APP SETUP
# ═══════════════════════════════════════════════════
app = Flask(__name__)

# Already DM bheje gaye users ka track (Duplicate avoid karne ke liye)
already_dm_sent = set()

# Log file
LOG_FILE = "dm_log.txt"


# ═══════════════════════════════════════════════════
#  📝 LOGGING FUNCTION
# ═══════════════════════════════════════════════════
def log_message(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")


# ═══════════════════════════════════════════════════
#  🔍 KEYWORD CHECK FUNCTION
# ═══════════════════════════════════════════════════
def contains_keyword(comment_text):
    """Comment mein trigger keyword hai ya nahi check karo"""
    if not CONFIG["KEYWORD_FILTER_ON"]:
        return True  # Filter OFF hai — sab comments pe DM bhejo
    
    comment_lower = comment_text.lower()
    for keyword in CONFIG["TRIGGER_KEYWORDS"]:
        if keyword.lower() in comment_lower:
            log_message(f"✅ Keyword found: '{keyword}' in comment: '{comment_text[:50]}'")
            return True
    
    log_message(f"⚠️ No keyword found in: '{comment_text[:50]}' — DM nahi bheja")
    return False


# ═══════════════════════════════════════════════════
#  📩 AUTO DM BHEJNE KA FUNCTION
# ═══════════════════════════════════════════════════
def send_auto_dm(user_id, username=""):
    """
    User ko automatic DM bhejo Instagram Graph API se
    """
    # Duplicate check — same user ko baar baar DM mat bhejo
    if user_id in already_dm_sent:
        log_message(f"⏭️ Already sent DM to {username} ({user_id}) — Skip kar rahe hain")
        return False
    
    url = f"https://graph.instagram.com/v18.0/{CONFIG['INSTAGRAM_ACCOUNT_ID']}/messages"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    payload = {
        "recipient": {
            "id": user_id
        },
        "message": {
            "text": CONFIG["AUTO_DM_MESSAGE"]
        },
        "access_token": CONFIG["ACCESS_TOKEN"]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 200:
            already_dm_sent.add(user_id)
            log_message(f"✅ DM Successfully sent to: @{username} (ID: {user_id})")
            return True
        else:
            log_message(f"❌ DM bhejne mein error: {response_data}")
            return False
            
    except Exception as e:
        log_message(f"❌ Exception aaya DM bhejte waqt: {str(e)}")
        return False


# ═══════════════════════════════════════════════════
#  💬 PUBLIC COMMENT REPLY FUNCTION
# ═══════════════════════════════════════════════════
def send_public_reply(comment_id):
    """
    Post ke comment ka public reply karo
    """
    if not CONFIG["SEND_PUBLIC_REPLY"]:
        return
    
    url = f"https://graph.instagram.com/v18.0/{comment_id}/replies"
    
    payload = {
        "message": CONFIG["PUBLIC_REPLY_TEXT"],
        "access_token": CONFIG["ACCESS_TOKEN"]
    }
    
    try:
        response = requests.post(url, params=payload)
        if response.status_code == 200:
            log_message(f"✅ Public reply sent on comment: {comment_id}")
        else:
            log_message(f"⚠️ Public reply error: {response.json()}")
    except Exception as e:
        log_message(f"❌ Public reply exception: {str(e)}")


# ═══════════════════════════════════════════════════
#  🔗 WEBHOOK VERIFICATION (Instagram ke liye zaroori)
# ═══════════════════════════════════════════════════
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Instagram pehli baar webhook verify karne ke liye GET request bhejta hai
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    log_message(f"🔗 Webhook verification request received — Mode: {mode}, Token: {token}")
    
    if mode == 'subscribe' and token == CONFIG["VERIFY_TOKEN"]:
        log_message("✅ Webhook Verified Successfully!")
        return challenge, 200
    else:
        log_message("❌ Webhook Verification FAILED — Wrong token!")
        return "Forbidden", 403


# ═══════════════════════════════════════════════════
#  📨 MAIN WEBHOOK — COMMENTS RECEIVE KARO
# ═══════════════════════════════════════════════════
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Jab bhi koi comment karta hai — Instagram yahan notification bhejta hai
    """
    data = request.get_json()
    
    # Raw data log karo (debugging ke liye)
    log_message(f"📥 Webhook received: {json.dumps(data, indent=2)[:200]}...")
    
    try:
        # Instagram se aane wala data process karo
        if data.get('object') == 'instagram':
            
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    
                    # ─── COMMENT EVENT CHECK ───
                    if change.get('field') == 'comments':
                        comment_data = change.get('value', {})
                        
                        comment_text = comment_data.get('text', '')
                        commenter_id = comment_data.get('from', {}).get('id', '')
                        commenter_name = comment_data.get('from', {}).get('username', 'Unknown')
                        comment_id = comment_data.get('id', '')
                        post_id = comment_data.get('media', {}).get('id', '')
                        
                        log_message(f"💬 New Comment! User: @{commenter_name} | Text: '{comment_text[:50]}'")
                        
                        # ─── KEYWORD CHECK ───
                        if contains_keyword(comment_text):
                            
                            # ─── AUTO DM BHEJO ───
                            dm_sent = send_auto_dm(commenter_id, commenter_name)
                            
                            # ─── PUBLIC REPLY KARO (Optional) ───
                            if dm_sent and comment_id:
                                send_public_reply(comment_id)
                        
                    # ─── MESSAGE EVENT CHECK (Story replies etc.) ───
                    elif change.get('field') == 'messages':
                        log_message(f"📨 Message event received")
    
    except Exception as e:
        log_message(f"❌ Webhook processing error: {str(e)}")
    
    # Instagram ko 200 OK bhejna zaroori hai
    return jsonify({"status": "ok"}), 200


# ═══════════════════════════════════════════════════
#  🏠 HOME PAGE — STATUS CHECK
# ═══════════════════════════════════════════════════
@app.route('/')
def home():
    return jsonify({
        "status": "🟢 Instagram Auto DM Bot is RUNNING!",
        "total_dms_sent": len(already_dm_sent),
        "keyword_filter": CONFIG["KEYWORD_FILTER_ON"],
        "keywords": CONFIG["TRIGGER_KEYWORDS"] if CONFIG["KEYWORD_FILTER_ON"] else "ALL COMMENTS",
        "message": "Bot chal raha hai! Comments ka wait kar raha hoon..."
    })


# ═══════════════════════════════════════════════════
#  📊 STATS PAGE
# ═══════════════════════════════════════════════════
@app.route('/stats')
def stats():
    """
    Kitne DMs bheje — ye dekho
    """
    return jsonify({
        "total_unique_users_dm_sent": len(already_dm_sent),
        "users_dm_sent_to": list(already_dm_sent)[-10:],  # Last 10
        "bot_status": "active",
        "config": {
            "keyword_filter": CONFIG["KEYWORD_FILTER_ON"],
            "keywords": CONFIG["TRIGGER_KEYWORDS"],
            "public_reply": CONFIG["SEND_PUBLIC_REPLY"]
        }
    })


# ═══════════════════════════════════════════════════
#  🚀 SERVER START
# ═══════════════════════════════════════════════════
if __name__ == '__main__':
    log_message("=" * 60)
    log_message("🚀 Instagram Auto DM Bot START ho raha hai...")
    log_message(f"🔑 Keyword Filter: {'ON' if CONFIG['KEYWORD_FILTER_ON'] else 'OFF (All comments)'}")
    log_message(f"💬 DM Message set hai: {len(CONFIG['AUTO_DM_MESSAGE'])} characters")
    log_message("🌐 Server: http://localhost:5000")
    log_message("🔗 Webhook URL: http://localhost:5000/webhook")
    log_message("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
