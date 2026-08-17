# 🚀 AI Digital Product Generator — Lynk.id Automation

Sistem **Agentic AI** yang membantu kreator menghasilkan produk digital (template, worksheet, planner) secara semi-otomatis untuk dijual di **Lynk.id**.

## ✨ Fitur

| Fitur | Deskripsi |
|---|---|
| 🤖 **Telegram Bot** | Ketik `/create [ide]` → langsung dapat copywriting lengkap |
| 📝 **AI Copywriting** | Judul, deskripsi, harga, tag SEO, dan CTA otomatis via Gemini |
| 🖼️ **Image Generator** | Download gambar cover & preview produk dari Pollinations.ai |
| 💰 **Zero Cost** | Semua layanan gratis — Vercel, Gemini, Pollinations.ai |

## 📐 Arsitektur

```
User → Telegram → Vercel (Webhook) → Gemini API → Response ke User
User → Local PC (generate.py) → Pollinations.ai → Download Gambar
User → HP → Lynk.id (Manual Upload)
```

## 📁 Struktur Folder

```
├── vercel/                    # Cloud — Deploy ke Vercel
│   ├── api/webhook.py         # Endpoint Telegram webhook
│   ├── agents/copywriter.py   # Integrasi Gemini AI
│   ├── utils/formatter.py     # Format pesan Telegram
│   ├── requirements.txt
│   └── vercel.json
│
├── local/                     # PC Lokal
│   ├── generate.py            # Download gambar Pollinations.ai
│   └── requirements.txt
│
├── .env.example               # Template environment variables
└── README.md
```

## 🛠️ Setup — Langkah demi Langkah

### Prasyarat
- **Python 3.9+** terinstall di PC
- **Akun GitHub** (untuk deploy ke Vercel)
- **Akun Vercel** gratis — [vercel.com](https://vercel.com)
- **Telegram Bot Token** dari [@BotFather](https://t.me/BotFather)
- **Google Gemini API Key** dari [Google AI Studio](https://aistudio.google.com/)

### 1. Clone Repository

```bash
git clone https://github.com/USERNAME/ai-digital-product-generator.git
cd ai-digital-product-generator
```

### 2. Setup Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env dan isi dengan API key Anda
# GEMINI_API_KEY=your_key_here
# TELEGRAM_BOT_TOKEN=your_token_here
```

### 3. Setup Script Lokal (PC)

```bash
cd local
pip install -r requirements.txt
```

### 4. Deploy ke Vercel

1. Push kode ke GitHub repository Anda.
2. Buka [vercel.com](https://vercel.com) → Import project dari GitHub.
3. Set **Root Directory** ke `vercel`.
4. Tambahkan **Environment Variables** di Vercel Dashboard:
   - `GEMINI_API_KEY` = API key Gemini Anda
   - `TELEGRAM_BOT_TOKEN` = Token Bot Telegram Anda
5. Deploy!

### 5. Set Webhook Telegram

Setelah deploy berhasil, jalankan perintah ini (ganti URL dan TOKEN):

```bash
curl -F "url=https://YOUR-VERCEL-URL.vercel.app/api/webhook" \
     https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook
```

Anda akan menerima response:
```json
{"ok": true, "result": true, "description": "Webhook was set"}
```

## 📱 Cara Pakai

### Bot Telegram

1. Buka chat dengan bot Anda di Telegram
2. Ketik `/start` untuk melihat instruksi
3. Ketik `/create template canva untuk toko baju`
4. Bot akan mengirim:
   - Judul, kategori, harga
   - Deskripsi panjang dengan bullet point
   - Tag SEO (minimal 5)
   - Prompt untuk cover image
   - Prompt untuk content/preview image
   - Call to action untuk promosi

### Generate Gambar (PC Lokal)

1. Copy prompt dari balasan bot
2. Buka terminal di PC:

```bash
cd local
python generate.py
```

3. Paste prompt cover → Enter
4. Paste prompt content → Enter
5. Gambar otomatis tersimpan di folder `local/output/`

### Upload ke Lynk.id

1. Kirim gambar dari PC ke HP (via WhatsApp/Telegram)
2. Buka Lynk.id di HP
3. Buat produk baru
4. Copy-paste judul, deskripsi, harga, dan tag dari balasan bot
5. Upload gambar dan publish!

## 🔧 Troubleshooting

| Masalah | Solusi |
|---|---|
| Bot tidak merespon | Cek webhook sudah di-set dengan URL yang benar |
| Error "GEMINI_API_KEY not set" | Tambahkan env var di Vercel Dashboard |
| Timeout di Vercel | Gemini API kadang lambat; coba lagi |
| Gambar tidak terdownload | Periksa koneksi internet dan coba prompt berbeda |
| JSON parse error | Coba `/create` lagi — kadang Gemini mengembalikan format berbeda |

## 📊 Batas & Limitasi

- **Gemini API**: 60 request/menit (gratis) — cukup untuk penggunaan personal
- **Vercel Hobby**: Timeout 10 detik per function — biasanya cukup
- **Pollinations.ai**: Unlimited, tanpa API key — bisa lambat saat traffic tinggi
- Upload ke Lynk.id masih **manual** (otomatisasi di fase selanjutnya)

## 📜 Lisensi

MIT License — Bebas digunakan dan dimodifikasi.
