import os, sys, re, json, subprocess
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SESSION = os.environ["TG_SESSION"].strip()
LINK = os.environ.get("TG_LINK", "https://t.me/c/4429882693/597").strip()

m = re.search(r"t\.me/c/(\d+)/(\d+)", LINK)
if not m:
    print("❌ Invalid private Telegram link:", LINK)
    sys.exit(1)

chat_id = int("-100" + m.group(1))
msg_id = int(m.group(2))

os.makedirs("downloads", exist_ok=True)
print(f"🚀 Connecting to Telegram & fetching chat={chat_id}, msg={msg_id}...")

with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
    # Populate entity cache from dialogs so private channel resolves reliably
    client.get_dialogs()
    msg = client.get_messages(chat_id, ids=msg_id)
    if not msg or not msg.media:
        print("❌ Message or media not found!")
        sys.exit(1)
    print("📥 Downloading file on GitHub High-Speed Server...")
    path = client.download_media(msg, file="downloads/")
    print(f"✅ Downloaded to: {path}")

print("\n☁️ 1. Uploading to Gofile.io...")
srv_raw = subprocess.check_output(["curl", "-s", "https://api.gofile.io/servers"]).decode()
srv = json.loads(srv_raw)["data"]["servers"][0]["name"]
up_raw = subprocess.check_output(["curl", "-s", "-F", f"file=@{path}", f"https://{srv}.gofile.io/contents/uploadfile"]).decode()
gofile_url = json.loads(up_raw).get("data", {}).get("downloadPage", "Failed")
print(f"==========================================")
print(f"🔗 GOFILE LINK: {gofile_url}")
print(f"==========================================")

print("\n☁️ 2. Uploading to Google Drive via rclone...")
remotes = subprocess.check_output(["rclone", "listremotes"]).decode().strip().splitlines()
if remotes:
    remote = remotes[0]
    subprocess.run(["rclone", "copy", path, f"{remote}Telegram_Backups/", "-v"], check=False)
    print(f"✅ Uploaded to Google Drive: {remote}Telegram_Backups/")
else:
    print("⚠️ RCLONE_CONFIG secret empty or no remotes found.")
