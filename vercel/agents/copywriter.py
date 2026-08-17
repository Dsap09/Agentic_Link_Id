"""
Copywriter Agent — Menghasilkan data produk digital terstruktur dengan Multi-Provider Fallback.

Provider Chain (Automatic Failover):
1. Gemini 3.6 Flash (Google AI Studio) — Primary
2. Groq (Llama 3.3 70B / Llama 3.1 8B) — Fallback 1
3. OpenRouter (Llama 3.1 8B Free) — Fallback 2
4. HuggingFace Inference API (Llama 3.2 3B) — Fallback 3

Jika provider utama (Gemini) terkena rate limit (429) atau error,
sistem otomatis mencoba provider cadangan berikutnya yang aktif.
"""

import os
import json
import logging
import requests

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Model configuration
GEMINI_MODEL = "gemini-3.6-flash"
GROQ_MODEL = "llama-3.3-70b-versatile"
OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct:free"
HF_MODEL = "meta-llama/Llama-3.2-3B-Instruct"

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
    "PENTING: Hanya balas dengan JSON valid tanpa markdown codeblock."
)

MAX_IDEA_LENGTH = 500


def _clean_json_text(text: str) -> str:
    """Bersihkan markdown wrapper dari response text."""
    raw = text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        cleaned = [line for line in lines if not line.strip().startswith("```")]
        return "\n".join(cleaned).strip()
    return raw


def _call_gemini(prompt: str) -> str:
    """Provider 1: Google Gemini API."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY tidak di-set.")

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.7,
        response_mime_type="application/json",
    )
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=config,
    )
    if not response or not response.text:
        raise RuntimeError("Gemini mengembalikan response kosong.")
    return response.text


def _call_groq(prompt: str) -> str:
    """Provider 2: Groq API (Llama 3.3 70B)."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY tidak di-set.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _call_openrouter(prompt: str) -> str:
    """Provider 3: OpenRouter API (Llama 3.1 8B Free)."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY tidak di-set.")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _call_huggingface(prompt: str) -> str:
    """Provider 4: Hugging Face Inference API."""
    api_key = os.environ.get("HF_API_KEY")
    if not api_key:
        raise ValueError("HF_API_KEY tidak di-set.")

    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    full_prompt = f"{SYSTEM_INSTRUCTION}\n\nUser: {prompt}\nJSON Response:"
    payload = {
        "inputs": full_prompt,
        "parameters": {"max_new_tokens": 1000, "return_full_text": False},
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=40)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list) and len(data) > 0:
        return data[0].get("generated_text", "")
    raise RuntimeError("Invalid response from Hugging Face API.")


def generate_product_pack(user_idea: str) -> dict:
    """Menghasilkan data produk digital dengan automatic multi-provider fallback.

    Args:
        user_idea: Ide produk dari user, misalnya "Template Canva untuk Kafe".

    Returns:
        dict berisi data produk terstruktur.

    Raises:
        ValueError: Jika input kosong/terlalu panjang.
        RuntimeError: Jika semua provider gagal.
    """
    if not user_idea or not user_idea.strip():
        raise ValueError("Ide produk tidak boleh kosong.")

    user_idea = user_idea.strip()
    if len(user_idea) > MAX_IDEA_LENGTH:
        raise ValueError(f"Ide produk terlalu panjang (maks {MAX_IDEA_LENGTH} karakter).")

    prompt = f'Buatkan data produk digital lengkap untuk ide: "{user_idea}".'

    # Fallback chain order
    providers = [
        ("Gemini (Primary)", _call_gemini),
        ("Groq (Fallback 1)", _call_groq),
        ("OpenRouter (Fallback 2)", _call_openrouter),
        ("Hugging Face (Fallback 3)", _call_huggingface),
    ]

    last_error = None

    for name, provider_fn in providers:
        try:
            logger.info("Mencoba provider: %s", name)
            raw_response = provider_fn(prompt)
            cleaned_json = _clean_json_text(raw_response)
            product_data = json.loads(cleaned_json)

            # Validasi minimal key
            required_keys = {"title", "category", "description", "tags", "cover_prompt"}
            if required_keys.issubset(product_data.keys()):
                logger.info("✅ Berhasil generate produk via provider: %s", name)
                return product_data
            else:
                logger.warning("Provider %s mengembalikan JSON tanpa key lengkap.", name)
                # Jika JSON valid tapi key kurang, tetap kembalikan
                return product_data

        except ValueError as val_err:
            # Key tidak di-set -> skip ke provider berikutnya secara hening
            logger.debug("Provider %s skipped: %s", name, val_err)
            continue
        except Exception as exc:
            logger.warning("Provider %s gagal: %s. Mencoba fallback berikutnya...", name, exc)
            last_error = exc
            continue

    logger.error("Semua text generation provider gagal.")
    raise RuntimeError(
        "Gagal menghubungi AI. Silakan coba lagi nanti."
    ) from last_error
