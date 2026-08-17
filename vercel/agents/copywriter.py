"""
Copywriter Agent — Menghasilkan data produk digital terstruktur menggunakan Google Gemini API.

Menerima ide produk dari user, mengirimkan prompt ke Gemini,
dan mengembalikan JSON terstruktur berisi semua elemen produk
yang dibutuhkan untuk listing di Lynk.id.

Menggunakan SDK baru 'google-genai' (menggantikan 'google-generativeai' yang deprecated).
"""

import os
import json
import logging

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Konfigurasi Gemini — API key HARUS dari environment variable.
_api_key = os.environ.get("GEMINI_API_KEY")
if not _api_key:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not set. "
        "Dapatkan API key dari https://aistudio.google.com/"
    )

# Inisialisasi client dengan API key
_client = genai.Client(api_key=_api_key)

# Model yang digunakan — gemini-3.6-flash (gratis, cepat, versi terbaru)
MODEL_NAME = "gemini-3.6-flash"

# System instruction untuk output JSON terstruktur
SYSTEM_INSTRUCTION = (
    "Anda adalah copywriter produk digital profesional untuk marketplace Indonesia. "
    "User akan memberikan ide produk (contoh: 'Template Canva untuk Kafe'). "
    "Buatkan response dalam format JSON yang VALID dengan key berikut:\n"
    "- title: string (maks 60 karakter, menarik dan SEO-friendly)\n"
    "- category: string (misal: Template Sosial Media, Planner, Worksheet, dll)\n"
    "- price: object dengan key 'promo' dan 'normal' (format 'Rp X.XXX')\n"
    "- description: string (minimal 120 kata, fokus pada benefit dan fitur, "
    "gunakan bullet point dengan emoji)\n"
    "- tags: array of string (minimal 5 tag, relevan untuk SEO)\n"
    "- cover_prompt: string (deskripsi detail untuk AI image generator, "
    "aesthetic, modern, professional, resolusi tinggi)\n"
    "- content_prompt: string (deskripsi detail untuk gambar isi/preview produk)\n"
    "- cta: string (Call to action menarik untuk promosi di sosial media)\n\n"
    "PENTING: Hanya balas dengan JSON valid."
)

# Batas maksimum panjang input ide produk (karakter).
MAX_IDEA_LENGTH = 500


def generate_product_pack(user_idea: str) -> dict:
    """Menghasilkan data produk digital dari ide user.

    Args:
        user_idea: Ide produk dari user, misalnya "Template Canva untuk Kafe".

    Returns:
        dict berisi data produk terstruktur.

    Raises:
        ValueError: Jika input kosong atau terlalu panjang.
        RuntimeError: Jika Gemini gagal menghasilkan JSON valid.
    """
    # Validasi input
    if not user_idea or not user_idea.strip():
        raise ValueError("Ide produk tidak boleh kosong.")

    user_idea = user_idea.strip()

    if len(user_idea) > MAX_IDEA_LENGTH:
        raise ValueError(
            f"Ide produk terlalu panjang (maks {MAX_IDEA_LENGTH} karakter)."
        )

    prompt = f'Buatkan data produk digital lengkap untuk ide: "{user_idea}".'

    logger.info("Mengirim request ke Gemini untuk ide produk.")

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.7,
        response_mime_type="application/json",
    )

    response = None
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        try:
            response = _client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=config,
            )
            break
        except Exception as exc:
            logger.warning("Gemini API attempt %d/%d failed: %s", attempt, max_retries, exc)
            if attempt < max_retries:
                import time
                time.sleep(2 * attempt)
            else:
                logger.error("Gemini API request gagal setelah %d retries.", max_retries)
                raise RuntimeError(
                    "Gagal menghubungi AI. Silakan coba lagi nanti."
                ) from exc

    if not response.text:
        raise RuntimeError("AI tidak menghasilkan response. Silakan coba lagi.")

    # Bersihkan markdown JSON wrapper jika ada
    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        # Hapus ```json ... ``` atau ``` ... ```
        lines = raw_text.split("\n")
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                continue
            cleaned_lines.append(line)
        raw_text = "\n".join(cleaned_lines)

    try:
        product_data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logger.error("Gagal parse JSON dari Gemini response.")
        raise RuntimeError(
            "AI menghasilkan format yang tidak valid. Silakan coba lagi."
        ) from exc

    # Validasi key minimum
    required_keys = {"title", "category", "description", "tags", "cover_prompt"}
    missing = required_keys - set(product_data.keys())
    if missing:
        logger.warning("Response JSON missing keys: %s", missing)
        # Tetap kembalikan data yang ada, formatter akan handle missing fields

    logger.info("Berhasil generate data produk: %s", product_data.get("title", "N/A"))
    return product_data
