### File 1: `prd.md`

```markdown
# PRD: AI Digital Product Generator (Lynk.id Automation)

**Versi:** 1.0.0  
**Status:** Draft  
**Target Biaya Operasional:** Rp 0,- (Zero Cost)  

## 1. Pendahuluan
Proyek ini bertujuan untuk membangun sebuah sistem Agentic AI yang membantu pengguna (kreator) menghasilkan produk digital (template, worksheet, planner) secara semi-otomatis untuk dijual di platform Lynk.id. Sistem ini didesain untuk meminimalisir biaya operasional dengan memanfaatkan layanan freemium dan membagi proses komputasi antara Cloud (Vercel) dan Local Machine.

## 2. Tujuan (Goals)
1.  **Otomatisasi Konten:** Menghasilkan judul, deskripsi, harga, dan tag SEO secara instan.
2.  **Generasi Visual:** Menyediakan prompt untuk menghasilkan desain cover produk melalui AI Gambar.
3.  **Zero Operational Cost:** Tidak ada biaya berlangganan API berbayar.
4.  **User-Friendly:** Menggunakan antarmuka Telegram sebagai remote control.

## 3. Target Audiens (User Persona)
- **Nama:** Alex (24 tahun)
- **Pekerjaan:** Freelancer / Digital Creator pemula.
- **Kebutuhan:** Ingin mengisi toko Lynk.id dengan banyak produk, tetapi kesulitan menulis copywriting dan mencari ide niche.
- **Keterbatasan:** Tidak mau mengeluarkan uang untuk alat berbayar dan tidak paham koding rumit.

## 4. Scope (Lingkup Pekerjaan)

### In-Scope (Akan Dibangun):
- Bot Telegram yang menerima perintah `/create [topik]`.
- Sistem di Vercel yang memproses ide menjadi teks produk (menggunakan Gemini API).
- Script Python Lokal untuk mengunduh gambar dari Pollinations.ai berdasarkan prompt.
- Panduan Manual Upload via HP Lynk.id.

### Out-of-Scope (Tidak Dibangun di Fase Ini):
- Otomatisasi upload otomatis ke Lynk.id (karena risiko block dan membutuhkan browser berat).
- Sistem pembayaran atau manajemen inventory.
- Generate gambar langsung di Vercel (hanya prompt).

## 5. Functional Requirements (Fitur)
| ID | Fitur | Deskripsi | Prioritas |
| :--- | :--- | :--- | :--- |
| **FR-01** | Perintah Bot | Bot merespon perintah `/create [nama produk]` di Telegram. | P0 |
| **FR-02** | Research Agent | Bot melakukan pencarian kata kunci/trend (menggunakan Gemini) untuk menentukan harga dan positioning. | P1 |
| **FR-03** | Copywriting Agent | Bot menghasilkan output terstruktur: Judul, Kategori, Harga, Deskripsi Panjang, Tag, dan Call to Action. | P0 |
| **FR-04** | Image Prompt | Bot menyertakan 2 prompt visual spesifik (Cover & Isi) untuk AI Generator. | P0 |
| **FR-05** | Local Generator | Script (`generate.py`) di PC yang membaca prompt dan menyimpan gambar ke folder lokal. | P0 |
| **FR-06** | Export Data | Bot menyediakan teks siap copy-paste yang diformat rapi untuk input manual di HP. | P0 |

## 6. Non-Functional Requirements (NFR)
- **Keamanan:** Environment variables (API Key) tidak boleh terekspos di kode.
- **Kinerja:** Bot harus merespon dalam waktu < 30 detik (batas timeout Vercel).
- **Biaya:** Penggunaan Google Gemini harus berada di kuota gratis (60 request/menit). Pollinations.ai unlimited.
- **Skalabilitas:** Struktur kode harus modular (pisah file untuk research, copywriting, dan formatting).

## 7. Alur Kerja User (User Flow)
1.  User membuka Telegram dan mengetik `/create template canva untuk toko baju`.
2.  Bot Vercel menerima request -> memanggil Gemini API -> mengembalikan teks lengkap (deskripsi, prompt, dll).
3.  User menyalin bagian "Image Prompt" dari balasan bot.
4.  User membuka terminal di PC lokal dan menjalankan `python generate.py`.
5.  Script meminta input prompt, lalu mengunduh gambar dan menyimpannya di folder `output/`.
6.  User mengirim file gambar dari PC ke HP (via WhatsApp/Telegram).
7.  User membuka aplikasi Lynk.id di HP, membuat produk baru.
8.  User **Copy-Paste** judul, deskripsi, harga, dan tag dari balasan Bot Telegram.
9.  User upload file gambar dari HP dan publish.

## 8. Metrik Kesuksesan
- Waktu pembuatan produk dari ide menjadi siap upload < 10 menit.
- Bot dapat berjalan 24/7 tanpa biaya tambahan.
- Deskripsi produk yang dihasilkan memiliki tingkat keterbacaan (Flesch score) yang baik untuk konversi.
```