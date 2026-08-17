### File 2: `brief.md`

```markdown
# Technical Brief: AI Digital Product Generator

**Target AI/Developer:** Antigravity / Gemini / Claude  
**Tujuan:** Memberikan instruksi teknis eksak untuk membangun proyek ini.

## 1. Arsitektur Sistem

```text
[User] -> [Telegram] -> [Vercel (Webhook)] -> [Gemini API] -> [Response ke User]
                                                      |
                                                      v
                                              [Format Teks Produk]
                                                      |
[User] -> [Local PC: generate.py] -> [Pollinations.ai] -> [Download Gambar]
                                                      |
[User] -> [HP] -> [Lynk.id] (Manual Copy-Paste + Upload)
```

## 2. Teknologi yang Digunakan (Zero Cost)

| Komponen | Teknologi | Alasan |
| :--- | :--- | :--- |
| **Runtime Cloud** | Vercel (Hobby Plan) | Gratis, mendukung Python, auto-deploy dari GitHub. |
| **Bahasa Cloud** | Python 3.9+ | Mudah untuk integrasi API dan parsing. |
| **Bahasa Lokal** | Python 3.9+ | Sama, untuk konsistensi. |
| **AI Teks** | Google Gemini API (`gemini-1.5-flash`) | Gratis kuota 60 RPM. |
| **AI Gambar** | Pollinations.ai | Gratis tak terbatas, tanpa API Key. |
| **Interface** | Telegram Bot API | Webhook gratis. |
| **Library Python** | `requests`, `python-telegram-bot` (atau Flask), `Pillow` (opsional). | Standard dan ringan. |

## 3. Struktur Folder Proyek

```text
/root-project/
├── vercel/                    # Kode untuk Vercel
│   ├── api/
│   │   └── webhook.py         # Endpoint utama Telegram
│   ├── agents/
│   │   ├── research.py        # Logika riset niche (opsional)
│   │   └── copywriter.py      # Logika prompt ke Gemini
│   ├── utils/
│   │   └── formatter.py       # Format balasan jadi Markdown/Plain
│   ├── requirements.txt       # Dependensi Vercel
│   └── vercel.json            # Konfigurasi routes
│
├── local/                     # Kode untuk PC Lokal
│   ├── generate.py            # Script utama download gambar
│   ├── config.py              # (Opsional) Default prompt
│   └── requirements.txt       # Dependensi lokal (requests)
│
└── README.md                  # Panduan instalasi
```

## 4. Implementasi Detail Vercel (`webhook.py`)

### 4.1. Setup Webhook
- Gunakan Flask atau `python-telegram-bot` v20+ (asynchronous).
- Endpoint: `POST /api/webhook`.
- Parse `update.message.text`.

### 4.2. Prompt Engineering untuk Gemini (KRITIS)
Kirimkan system instruction berikut ke Gemini API:

```text
Anda adalah copywriter produk digital profesional.
User akan memberikan ide produk (contoh: "Template Canva untuk Kafe").
Buatkan response dalam format JSON yang VALID dengan key berikut:
- title: string (maks 60 karakter)
- category: string (misal: Template Sosial Media, Planner, dll)
- price: string (berikan 2 opsi: harga promo dan harga normal, format "Rp X")
- description: string (minimal 120 kata, fokus pada benefit dan fitur, gunakan bullet point)
- tags: array of string (minimal 5 tag)
- cover_prompt: string (deskripsi untuk gambar cover produk, aesthetic, resolusi tinggi)
- content_prompt: string (deskripsi untuk gambar isi/detail produk)
- cta: string (Call to action untuk promosi di sosial media)
```

### 4.3. Kode Core (Copywriter Agent)
```python
import os
import json
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_product_pack(user_idea: str):
    prompt = f"""
    Buatkan data produk digital untuk ide: "{user_idea}".
    Hanya balas dengan JSON valid.
    """
    response = model.generate_content(prompt)
    # Bersihkan markdown JSON jika ada
    cleaned = response.text.replace('```json', '').replace('```', '')
    return json.loads(cleaned)
```

### 4.4. Formatter untuk Telegram
Balasan harus dalam format **Markdown** atau **Plain** yang mudah di-copy.
Gunakan format blok kode atau bullet. Contoh output:

```text
📦 *PRODUK: [TITLE]*
💰 Harga: [PRICE]
📝 Deskripsi:
[DESCRIPTION]

🏷️ Tag: [TAGS]

🖼️ Prompt Cover: [COVER_PROMPT]
🖼️ Prompt Isi: [CONTENT_PROMPT]

📣 CTA: [CTA]
```

## 5. Implementasi Detail Lokal (`generate.py`)

### 5.1. Fungsi Download
```python
import requests
import os
from datetime import datetime

def download_image(prompt, filename):
    # Pollinations.ai endpoint
    url = f"https://pollinations.ai/p/{prompt}?width=1080&height=1080&nologo=true"
    response = requests.get(url)
    if response.status_code == 200:
        with open(f"output/{filename}.png", "wb") as f:
            f.write(response.content)
        print(f"✅ Gambar tersimpan: {filename}")
    else:
        print(f"❌ Gagal download: {response.status_code}")
```

### 5.2. Alur Script
1. Minta user memasukkan prompt cover.
2. Minta user memasukkan prompt isi.
3. Buat folder `output/` jika belum ada.
4. Download kedua gambar dengan timestamp agar unik.

## 6. Environment Variables (Vercel)
- `GEMINI_API_KEY`: Dapatkan dari Google AI Studio (gratis).
- `TELEGRAM_BOT_TOKEN`: Dapatkan dari @BotFather.
- `VERCEL_URL`: Otomatis diisi oleh Vercel.

## 7. Panduan Deploy ke Vercel
1. Push kode ke GitHub.
2. Import repository ke Vercel.
3. Set Environment Variables di Dashboard Vercel.
4. Set Webhook Telegram:
   `curl -F "url=https://[your-vercel-url]/api/webhook" https://api.telegram.org/bot[TOKEN]/setWebhook`

## 8. Instruksi untuk AI Agent (AntiGravity) - Tindakan Spesifik
Mohon buatkan file-file berikut secara lengkap berdasarkan brief di atas:
1. `vercel/api/webhook.py` (Flask + Async handling).
2. `vercel/agents/copywriter.py` (Integrasi Gemini JSON).
3. `vercel/utils/formatter.py` (Format pesan).
4. `vercel/requirements.txt`.
5. `local/generate.py` (Script download mandiri).
6. `README.md` (Panduan setup dari nol).

**Catatan Penting untuk AI:** 
- Pastikan semua file memiliki error handling (try-except).
- Pada `webhook.py`, gunakan `telegram.Bot` untuk reply agar mudah, atau gunakan `requests` manual untuk mengirim balasan.
- Jangan lupa tambahkan logging sederhana untuk debugging.
```
