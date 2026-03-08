╔══════════════════════════════════════════════════════════════════╗
║       INSTAGRAM AUTO DM BOT — SETUP GUIDE (Hindi)              ║
╚══════════════════════════════════════════════════════════════════╝

📁 FILES:
   app.py          → Main bot code (Flask server + webhook handler)
   test_bot.py     → Local test script
   requirements.txt → Python packages
   .env.example    → Credentials template
   README.txt      → Yeh file (setup guide)

═══════════════════════════════════════════════════════════════════
PART 1: INSTAGRAM API SETUP (Facebook Developer Console)
═══════════════════════════════════════════════════════════════════

STEP 1 — Facebook Developer Account
  1. https://developers.facebook.com jaao
  2. "My Apps" → "Create App" click karo
  3. "Business" type select karo
  4. App name likho (jaise "MyInstagramBot")

STEP 2 — Instagram Basic Display Add Karo
  1. App Dashboard mein "Add Product" click karo
  2. "Instagram Graph API" → "Set Up" click karo

STEP 3 — Instagram Account Connect
  1. Instagram Account → Connect karo (Business/Creator account chahiye)
  2. Permissions allow karo:
     ✅ instagram_manage_comments
     ✅ instagram_manage_messages  
     ✅ pages_manage_metadata

STEP 4 — Access Token Generate Karo
  1. Graph API Explorer → Tool mein jaao
  2. Apna App select karo
  3. "Generate Access Token" click karo
  4. Saari permissions select karo
  5. Token copy karo → app.py mein daalo

STEP 5 — Instagram Account ID Nikalo
  Run karo:
  curl "https://graph.instagram.com/me?access_token=YOUR_TOKEN"
  ID wala value copy karo → app.py mein daalo

═══════════════════════════════════════════════════════════════════
PART 2: LOCAL MACHINE PE CHALANA
═══════════════════════════════════════════════════════════════════

Terminal mein yeh commands chalao:

  # 1. Project folder mein jaao
  cd instagram_auto_dm

  # 2. Python packages install karo
  pip install -r requirements.txt

  # 3. app.py mein apni values daalo
  #    (ACCESS_TOKEN, VERIFY_TOKEN, INSTAGRAM_ACCOUNT_ID)
  
  # 4. Bot start karo
  python app.py

  # 5. Doosri terminal mein ngrok chalao (public URL ke liye)
  ngrok http 5000

═══════════════════════════════════════════════════════════════════
PART 3: NGROK SETUP (Public URL ke liye zaroori!)
═══════════════════════════════════════════════════════════════════

Instagram ko ek public URL chahiye webhook ke liye.
Ngrok free mein local server ko public banata hai.

  1. https://ngrok.com pe free account banao
  2. Download karo ngrok
  3. Terminal mein: ngrok http 5000
  4. Ye URL milega: https://abc123.ngrok.io
  5. Webhook URL hogi: https://abc123.ngrok.io/webhook

═══════════════════════════════════════════════════════════════════
PART 4: WEBHOOK INSTAGRAM PE REGISTER KARO
═══════════════════════════════════════════════════════════════════

  1. Facebook Developer Console → App → Webhooks
  2. "Subscribe to this object" → Instagram select karo
  3. Callback URL: https://abc123.ngrok.io/webhook
  4. Verify Token: my_secret_token_123 (jo app.py mein daala)
  5. "Verify and Save" click karo
  6. "comments" field pe subscribe karo

═══════════════════════════════════════════════════════════════════
PART 5: TEST KARO
═══════════════════════════════════════════════════════════════════

  # Locally test karne ke liye (app.py chalne ke baad):
  python test_bot.py

  # Ya apni Instagram post pe jaake comment karo
  # Aur check karo ki DM aaya ya nahi!

═══════════════════════════════════════════════════════════════════
app.py MEIN CUSTOMIZE KARO:
═══════════════════════════════════════════════════════════════════

  "KEYWORD_FILTER_ON": False    → Sabhi comments pe DM
  "KEYWORD_FILTER_ON": True     → Sirf keyword wale comments pe DM
  
  "TRIGGER_KEYWORDS": ["info", "link", "chahiye"]  → Apne keywords
  
  "AUTO_DM_MESSAGE": "..."      → Apna DM message
  
  "SEND_PUBLIC_REPLY": True     → Post pe bhi reply karo

═══════════════════════════════════════════════════════════════════
FREE HOSTING OPTIONS (24/7 chalane ke liye):
═══════════════════════════════════════════════════════════════════

  Option 1: Railway.app (Free tier available)
    - https://railway.app
    - GitHub se deploy karo

  Option 2: Render.com (Free tier available)  
    - https://render.com
    - Simple deployment

  Option 3: Vercel (Free)
    - https://vercel.com

═══════════════════════════════════════════════════════════════════
⚠️  IMPORTANT NOTES:
═══════════════════════════════════════════════════════════════════

  ❶ Instagram Business/Creator Account zaroori hai
  ❷ Access Token ko KABHI publicly share mat karo
  ❸ Instagram ki 24-hour messaging window rule hai
     (Comment ke 24 ghante baad DM nahi bheja ja sakta)
  ❹ Ye code META ki official API use karta hai — 100% safe hai
  ❺ Bahut zyada DM bhejne se account flag ho sakta hai
     (Bot code mein already duplicate protection hai)
