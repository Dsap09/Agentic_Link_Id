"""
Local Image Generator — Download gambar produk dari Pollinations.ai.

Script CLI interaktif yang menerima prompt dari user (didapat dari Bot Telegram),
lalu mengunduh gambar cover dan gambar isi/preview produk.
Gambar disimpan di folder 'output/' dengan nama file unik (timestamp).

Cara pakai:
    python generate.py
"""

import os
import re
import sys
import time
import urllib.parse
from datetime import datetime

# Fix encoding untuk Windows console (cp1252 tidak mendukung emoji)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")

import requests


# Konfigurasi
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1080
REQUEST_TIMEOUT = 120  # Pollinations.ai bisa lambat saat generate


def sanitize_filename(name: str) -> str:
    """Bersihkan string menjadi filename yang aman.

    Hanya mengizinkan karakter alfanumerik, underscore, dan hyphen.
    Mencegah path traversal.

    Args:
        name: String input yang akan dijadikan bagian filename.

    Returns:
        String yang aman digunakan sebagai filename.
    """
    # Ambil hanya basename untuk mencegah path traversal
    name = os.path.basename(name)
    # Hanya izinkan karakter aman
    safe_name = re.sub(r"[^\w\-]", "_", name)
    # Limit panjang
    return safe_name[:50] if safe_name else "image"


def download_image(prompt: str, label: str) -> str:
    """Download gambar dari Pollinations.ai berdasarkan prompt.

    Args:
        prompt: Deskripsi gambar yang ingin di-generate.
        label: Label untuk gambar (misal: 'cover', 'content').

    Returns:
        Path file yang berhasil disimpan.

    Raises:
        RuntimeError: Jika download gagal.
    """
    # Buat output directory jika belum ada
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Encode prompt untuk URL
    encoded_prompt = urllib.parse.quote(prompt, safe="")

    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&nologo=true"
    )

    # Buat filename unik dengan timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_label = sanitize_filename(label)
    filename = f"{safe_label}_{timestamp}.jpg"
    filepath = os.path.join(OUTPUT_DIR, filename)

    print(f"\n🎨 Generating: {label}")
    print(f"   Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    print(f"   Resolusi: {IMAGE_WIDTH}x{IMAGE_HEIGHT}")
    print(f"   Mendownload dari Pollinations.ai...")

    max_retries = 3
    response = None

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT, stream=True)

            # Handle rate limiting dengan retry
            if response.status_code == 429:
                wait_time = min(10 * attempt, 30)
                print(f"   ⏳ Rate limited, menunggu {wait_time}s... (percobaan {attempt}/{max_retries})")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            break  # Berhasil, keluar dari loop

        except requests.Timeout:
            if attempt < max_retries:
                print(f"   ⏳ Timeout, mencoba lagi... (percobaan {attempt}/{max_retries})")
                time.sleep(5)
                continue
            raise RuntimeError(
                f"Timeout ({REQUEST_TIMEOUT}s) saat download setelah {max_retries}x percobaan. "
                "Coba lagi atau periksa koneksi internet."
            )
        except requests.ConnectionError:
            raise RuntimeError(
                "Gagal terhubung ke Pollinations.ai. Periksa koneksi internet."
            )
        except requests.HTTPError as exc:
            if attempt < max_retries and exc.response.status_code >= 500:
                print(f"   ⏳ Server error, mencoba lagi... (percobaan {attempt}/{max_retries})")
                time.sleep(5)
                continue
            raise RuntimeError(
                f"Server error (HTTP {exc.response.status_code}). Coba lagi nanti."
            )
    else:
        raise RuntimeError(
            "Gagal download setelah beberapa percobaan. Coba lagi nanti."
        )

    # Verifikasi response berisi data gambar (bukan HTML redirect)
    content_type = response.headers.get("content-type", "")
    # Baca awal content untuk cek magic bytes
    first_chunk = next(response.iter_content(chunk_size=16), b"")

    is_jpeg = first_chunk[:2] == b"\xff\xd8"
    is_png = first_chunk[:4] == b"\x89PNG"
    is_html = first_chunk.lstrip()[:1] == b"<"

    if is_html or (not is_jpeg and not is_png):
        raise RuntimeError(
            "Response bukan gambar valid (mungkin HTML redirect). Coba ubah prompt Anda."
        )

    with open(filepath, "wb") as f:
        f.write(first_chunk)  # Tulis chunk pertama yang sudah dibaca
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    file_size_kb = os.path.getsize(filepath) / 1024
    print(f"   ✅ Tersimpan: {filepath} ({file_size_kb:.1f} KB)")

    return filepath


def main():
    """Main entry point — interaktif CLI."""
    print("=" * 60)
    print("🖼️  AI Digital Product — Image Generator")
    print("   Powered by Pollinations.ai (Gratis & Tanpa API Key)")
    print("=" * 60)
    print()
    print("💡 Paste prompt dari Bot Telegram Anda di bawah ini.")
    print("   Ketik 'quit' atau 'q' untuk keluar.")
    print()

    while True:
        print("-" * 60)

        # Input prompt cover
        print("\n📷 [1/2] Prompt COVER produk:")
        cover_prompt = input(">>> ").strip()

        if cover_prompt.lower() in ("quit", "q", "exit"):
            print("\n👋 Sampai jumpa!")
            break

        if not cover_prompt:
            print("⚠️ Prompt tidak boleh kosong. Coba lagi.")
            continue

        # Input prompt content/preview
        print("\n📷 [2/2] Prompt ISI/PREVIEW produk:")
        content_prompt = input(">>> ").strip()

        if content_prompt.lower() in ("quit", "q", "exit"):
            print("\n👋 Sampai jumpa!")
            break

        if not content_prompt:
            print("⚠️ Prompt tidak boleh kosong. Coba lagi.")
            continue

        # Download kedua gambar
        print("\n⏳ Memulai proses download gambar...")
        results = []

        try:
            cover_path = download_image(cover_prompt, "cover")
            results.append(("Cover", cover_path))
        except RuntimeError as exc:
            print(f"   ❌ Gagal download cover: {exc}")

        # Delay sedikit antara request
        time.sleep(2)

        try:
            content_path = download_image(content_prompt, "content")
            results.append(("Content", content_path))
        except RuntimeError as exc:
            print(f"   ❌ Gagal download content: {exc}")

        # Summary
        print("\n" + "=" * 60)
        print("📊 HASIL:")
        if results:
            for label, path in results:
                print(f"   ✅ {label}: {path}")
            print(f"\n📁 Folder output: {OUTPUT_DIR}")
            print("   Kirim file ini ke HP Anda untuk upload ke Lynk.id!")
        else:
            print("   ❌ Tidak ada gambar yang berhasil didownload.")
        print("=" * 60)

        # Tanya lagi
        print("\n🔄 Generate gambar lagi? (Enter untuk lanjut, 'q' untuk keluar)")
        again = input(">>> ").strip()
        if again.lower() in ("quit", "q", "exit"):
            print("\n👋 Sampai jumpa!")
            break


if __name__ == "__main__":
    main()
