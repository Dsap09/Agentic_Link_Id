"""
Telegram Webhook Handler — Endpoint utama untuk Vercel.

Menerima update dari Telegram Bot API via webhook,
memproses perintah /create, dan mengirim balasan.
"""

import os
import sys
import json
import logging

from flask import Flask, request, jsonify

# Tambahkan parent directory ke path agar bisa import agents & utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests as http_requests

from agents.copywriter import generate_product_pack
from utils.formatter import format_product_markdown, format_product_plain

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# --- App Setup ---
app = Flask(__name__)

# Telegram Bot Token — HARUS dari environment variable
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN environment variable is not set. "
        "Dapatkan token dari https://t.me/BotFather"
    )

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Batas panjang pesan Telegram
TELEGRAM_MAX_MESSAGE_LENGTH = 4096


def send_telegram_message(chat_id: int, text: str, parse_mode: str = None) -> bool:
    """Kirim pesan ke Telegram chat.

    Args:
        chat_id: ID chat Telegram tujuan.
        text: Teks pesan yang akan dikirim.
        parse_mode: "MarkdownV2", "HTML", atau None untuk plain text.

    Returns:
        True jika berhasil, False jika gagal.
    """
    url = f"{TELEGRAM_API_BASE}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        resp = http_requests.post(url, json=payload, timeout=10)
        if resp.status_code != 200:
            logger.error(
                "Telegram sendMessage gagal (status %d)", resp.status_code
            )
            return False
        return True
    except http_requests.RequestException:
        logger.error("Network error saat mengirim pesan Telegram.")
        return False


def send_long_message(chat_id: int, text: str, parse_mode: str = None) -> bool:
    """Kirim pesan panjang dengan memecah ke beberapa pesan jika melebihi limit.

    Args:
        chat_id: ID chat Telegram tujuan.
        text: Teks pesan lengkap.
        parse_mode: Mode parsing Telegram.

    Returns:
        True jika semua bagian berhasil dikirim.
    """
    if len(text) <= TELEGRAM_MAX_MESSAGE_LENGTH:
        return send_telegram_message(chat_id, text, parse_mode)

    # Pecah berdasarkan baris, jaga agar tidak melebihi limit
    lines = text.split("\n")
    current_chunk = []
    current_length = 0
    all_success = True

    for line in lines:
        line_length = len(line) + 1  # +1 untuk newline
        if current_length + line_length > TELEGRAM_MAX_MESSAGE_LENGTH:
            chunk_text = "\n".join(current_chunk)
            if not send_telegram_message(chat_id, chunk_text, parse_mode):
                all_success = False
            current_chunk = [line]
            current_length = line_length
        else:
            current_chunk.append(line)
            current_length += line_length

    # Kirim sisa
    if current_chunk:
        chunk_text = "\n".join(current_chunk)
        if not send_telegram_message(chat_id, chunk_text, parse_mode):
            all_success = False

    return all_success


@app.route("/api/webhook", methods=["POST"])
def webhook():
    """Handler utama untuk webhook Telegram."""
    try:
        update = request.get_json(force=True, silent=True)
    except Exception:
        logger.warning("Gagal parse request body.")
        return jsonify({"ok": False, "error": "Invalid request body"}), 400

    if not update:
        return jsonify({"ok": False, "error": "Empty request"}), 400

    # Ambil data pesan
    message = update.get("message")
    if not message:
        # Mungkin edited_message, callback, dll — abaikan
        return jsonify({"ok": True})

    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not chat_id:
        return jsonify({"ok": True})

    # Validasi: hanya proses teks
    if not text:
        return jsonify({"ok": True})

    # Trim dan limit panjang input
    text = text.strip()
    if len(text) > 1000:
        send_telegram_message(
            chat_id,
            "⚠️ Pesan terlalu panjang. Maksimal 1000 karakter.",
        )
        return jsonify({"ok": True})

    # Handle perintah /start
    if text.startswith("/start"):
        welcome_msg = (
            "👋 Selamat datang di *AI Digital Product Generator*\\!\n\n"
            "Saya membantu Anda membuat produk digital untuk Lynk\\.id\\.\n\n"
            "🚀 *Cara Pakai:*\n"
            "Ketik `/create` diikuti ide produk Anda\\.\n\n"
            "📝 *Contoh:*\n"
            "`/create template canva untuk toko baju`\n"
            "`/create planner mingguan untuk mahasiswa`\n"
            "`/create worksheet bahasa Inggris anak SD`\n\n"
            "Bot akan menghasilkan judul, deskripsi, harga, tag SEO, "
            "dan prompt untuk generate gambar cover\\! 🎨"
        )
        send_telegram_message(chat_id, welcome_msg, parse_mode="MarkdownV2")
        return jsonify({"ok": True})

    # Handle perintah /create
    if text.startswith("/create"):
        # Ambil ide setelah /create
        idea = text[len("/create"):].strip()

        if not idea:
            send_telegram_message(
                chat_id,
                "⚠️ Silakan tambahkan ide produk setelah /create.\n"
                "Contoh: /create template canva untuk toko baju",
            )
            return jsonify({"ok": True})

        # Kirim "typing" indicator
        try:
            http_requests.post(
                f"{TELEGRAM_API_BASE}/sendChatAction",
                json={"chat_id": chat_id, "action": "typing"},
                timeout=5,
            )
        except http_requests.RequestException:
            pass  # Non-critical, lanjutkan

        send_telegram_message(
            chat_id,
            "⏳ Sedang memproses ide produk Anda... Mohon tunggu.",
        )

        try:
            product_data = generate_product_pack(idea)
        except ValueError as exc:
            send_telegram_message(chat_id, f"⚠️ {exc}")
            return jsonify({"ok": True})
        except RuntimeError as exc:
            send_telegram_message(chat_id, f"❌ {exc}")
            return jsonify({"ok": True})
        except Exception:
            logger.exception("Unexpected error saat generate product.")
            send_telegram_message(
                chat_id,
                "❌ Terjadi kesalahan yang tidak terduga. Silakan coba lagi.",
            )
            return jsonify({"ok": True})

        # Kirim versi Markdown dulu
        markdown_text = format_product_markdown(product_data)
        md_success = send_long_message(
            chat_id, markdown_text, parse_mode="MarkdownV2"
        )

        if not md_success:
            # Fallback ke plain text jika Markdown gagal
            plain_text = format_product_plain(product_data)
            send_long_message(chat_id, plain_text)

        # Kirim instruksi follow-up
        followup = (
            "✅ *Langkah Selanjutnya:*\n\n"
            "1\\. Copy prompt cover di atas\n"
            "2\\. Buka terminal di PC, jalankan `python generate\\.py`\n"
            "3\\. Paste prompt → gambar akan di\\-download otomatis\n"
            "4\\. Upload ke Lynk\\.id bersama data produk di atas\\!"
        )
        send_telegram_message(chat_id, followup, parse_mode="MarkdownV2")

        return jsonify({"ok": True})

    # Perintah tidak dikenal
    send_telegram_message(
        chat_id,
        "🤔 Perintah tidak dikenali.\n"
        "Ketik /create [ide produk] untuk mulai.\n"
        "Contoh: /create template canva untuk toko baju",
    )
    return jsonify({"ok": True})


# Vercel membutuhkan handler sebagai variabel module-level
# Flask app sudah terdefinisi di atas, Vercel akan menggunakannya.
