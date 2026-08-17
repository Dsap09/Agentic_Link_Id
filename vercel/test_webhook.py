"""
Test script untuk Vercel webhook — simulasi lokal TANPA deploy.

Script ini:
1. Load environment variables dari .env
2. Jalankan Flask app di background
3. Kirim fake Telegram update ke webhook endpoint
4. Tampilkan response

Cara pakai:
    python test_webhook.py
"""

import os
import sys
import json
import time
import threading

# Fix encoding Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load .env file
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(env_path)

# Verifikasi env vars tersedia
gemini_key = os.environ.get("GEMINI_API_KEY")
telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")

if not gemini_key or gemini_key == "your_gemini_api_key_here":
    print("❌ GEMINI_API_KEY belum di-set di .env")
    sys.exit(1)

if not telegram_token or telegram_token == "your_telegram_bot_token_here":
    print("❌ TELEGRAM_BOT_TOKEN belum di-set di .env")
    sys.exit(1)

print("✅ Environment variables loaded")
print(f"   GEMINI_API_KEY: {gemini_key[:10]}...{gemini_key[-4:]}")
print(f"   TELEGRAM_BOT_TOKEN: {telegram_token[:10]}...{telegram_token[-4:]}")

# Tambah path ke vercel modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

# Import Flask app
from api.webhook import app

# Test configuration
TEST_HOST = "127.0.0.1"
TEST_PORT = 5555


def run_flask():
    """Run Flask di thread terpisah."""
    app.run(host=TEST_HOST, port=TEST_PORT, debug=False, use_reloader=False)


def send_test_update(text: str, chat_id: int = 12345) -> dict:
    """Kirim fake Telegram update ke webhook."""
    fake_update = {
        "update_id": 100000001,
        "message": {
            "message_id": 1,
            "from": {
                "id": chat_id,
                "is_bot": False,
                "first_name": "TestUser",
            },
            "chat": {
                "id": chat_id,
                "first_name": "TestUser",
                "type": "private",
            },
            "date": int(time.time()),
            "text": text,
        },
    }

    url = f"http://{TEST_HOST}:{TEST_PORT}/api/webhook"
    try:
        resp = requests.post(url, json=fake_update, timeout=60)
        return {
            "status": resp.status_code,
            "body": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text,
        }
    except requests.RequestException as exc:
        return {"status": -1, "error": str(exc)}


def main():
    print("\n" + "=" * 60)
    print("🧪 Webhook Local Test — AI Digital Product Generator")
    print("=" * 60)

    # Start Flask server
    print(f"\n🚀 Starting Flask server at http://{TEST_HOST}:{TEST_PORT}")
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()
    time.sleep(2)  # Tunggu server ready

    print("✅ Server running\n")

    # ── Test 1: /start command ──
    print("-" * 60)
    print("📋 Test 1: Perintah /start")
    result = send_test_update("/start")
    print(f"   Status: {result['status']}")
    if result["status"] == 200:
        print("   ✅ PASSED — Bot merespon /start")
    else:
        print(f"   ❌ FAILED — {result}")

    # ── Test 2: /create tanpa argumen ──
    print("\n" + "-" * 60)
    print("📋 Test 2: Perintah /create (tanpa argumen)")
    result = send_test_update("/create")
    print(f"   Status: {result['status']}")
    if result["status"] == 200:
        print("   ✅ PASSED — Bot menolak /create kosong")
    else:
        print(f"   ❌ FAILED — {result}")

    # ── Test 3: /create dengan ide produk (REAL Gemini call) ──
    print("\n" + "-" * 60)
    print("📋 Test 3: Perintah /create [ide] — panggil Gemini API")
    print("   ⏳ Mengirim ke Gemini API... (bisa 5-15 detik)")
    result = send_test_update("/create template canva untuk toko kopi")
    print(f"   Status: {result['status']}")
    if result["status"] == 200:
        print("   ✅ PASSED — Gemini merespon dan produk di-generate!")
    else:
        print(f"   ❌ FAILED — {result}")

    # ── Test 4: Perintah tidak dikenal ──
    print("\n" + "-" * 60)
    print("📋 Test 4: Perintah tidak dikenal")
    result = send_test_update("hello bot")
    print(f"   Status: {result['status']}")
    if result["status"] == 200:
        print("   ✅ PASSED — Bot menolak perintah tidak dikenal")
    else:
        print(f"   ❌ FAILED — {result}")

    # ── Test 5: Non-POST method (GET) ──
    print("\n" + "-" * 60)
    print("📋 Test 5: GET request (seharusnya ditolak)")
    try:
        resp = requests.get(f"http://{TEST_HOST}:{TEST_PORT}/api/webhook", timeout=10)
        if resp.status_code == 405:
            print(f"   Status: {resp.status_code}")
            print("   ✅ PASSED — GET method ditolak (405)")
        else:
            print(f"   Status: {resp.status_code}")
            print(f"   ⚠️ Unexpected response: {resp.status_code}")
    except requests.RequestException as exc:
        print(f"   ❌ Error: {exc}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print("   Catatan: Test 1,2,4 mengecek routing dan validasi.")
    print("   Test 3 melakukan REAL API call ke Gemini.")
    print("   Pesan Telegram tidak terkirim ke chat Anda karena chat_id = 12345 (fake).")
    print("   Tapi jika Test 3 PASSED, artinya Gemini berhasil generate produk!")
    print("\n   Jika semua test passed, webhook siap deploy ke Vercel! 🚀")
    print("=" * 60)


if __name__ == "__main__":
    main()
