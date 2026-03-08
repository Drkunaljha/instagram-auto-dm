"""
╔══════════════════════════════════════════════════════════╗
║  TEST SCRIPT — Bina Instagram ke locally test karo      ║
║  Ye script fake webhook bhejta hai aur DM test karta hai ║
╚══════════════════════════════════════════════════════════╝
"""

import requests
import json

# ─── Apna local server URL ───
BASE_URL = "http://localhost:5000"

def test_bot_status():
    """Bot chal raha hai ya nahi check karo"""
    print("\n" + "="*50)
    print("🔍 BOT STATUS CHECK")
    print("="*50)
    r = requests.get(f"{BASE_URL}/")
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))

def test_fake_comment(comment_text="Yaar ye kya hai! INFO chahiye"):
    """
    Fake Instagram comment webhook bhejo — test ke liye
    """
    print("\n" + "="*50)
    print(f"💬 FAKE COMMENT BHEJ RAHA HOON: '{comment_text}'")
    print("="*50)
    
    # Instagram jaisa data format
    fake_webhook_data = {
        "object": "instagram",
        "entry": [
            {
                "id": "YOUR_ACCOUNT_ID",
                "time": 1234567890,
                "changes": [
                    {
                        "field": "comments",
                        "value": {
                            "id": "comment_123456",
                            "text": comment_text,
                            "from": {
                                "id": "user_987654",
                                "username": "test_user_hindi"
                            },
                            "media": {
                                "id": "post_111222333",
                                "media_product_type": "POST"
                            },
                            "timestamp": "2025-01-01T12:00:00+0000"
                        }
                    }
                ]
            }
        ]
    }
    
    r = requests.post(
        f"{BASE_URL}/webhook",
        json=fake_webhook_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Response Status: {r.status_code}")
    print(f"Response: {r.json()}")

def test_webhook_verification():
    """Webhook verification test karo"""
    print("\n" + "="*50)
    print("🔗 WEBHOOK VERIFICATION TEST")
    print("="*50)
    
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "my_secret_token_123",
        "hub.challenge": "test_challenge_12345"
    }
    
    r = requests.get(f"{BASE_URL}/webhook", params=params)
    print(f"Status: {r.status_code}")
    print(f"Challenge returned: {r.text}")

def test_stats():
    """Stats dekho"""
    print("\n" + "="*50)
    print("📊 STATS")
    print("="*50)
    r = requests.get(f"{BASE_URL}/stats")
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))


# ─── TESTS RUN KARO ───
if __name__ == "__main__":
    print("\n🚀 INSTAGRAM AUTO DM BOT — TEST SUITE")
    print("⚠️  Pehle app.py chala lo: python app.py")
    print("Tab yeh test script chalao: python test_bot.py\n")
    
    try:
        # 1. Bot status check
        test_bot_status()
        
        # 2. Webhook verification test
        test_webhook_verification()
        
        # 3. Normal comment test (no keyword)
        test_fake_comment("Bahut achha post hai!")
        
        # 4. Keyword wala comment test
        test_fake_comment("Yaar INFO chahiye mujhe!")
        
        # 5. Stats dekho
        test_stats()
        
        print("\n✅ SAARE TESTS COMPLETE! Check karo app.py ka output")
        
    except Exception as e:
        print(f"\n❌ Test fail hua: {e}")
        print("💡 Make sure app.py chal raha ho pehle!")
