"""
Formatter — Mengubah data produk JSON menjadi teks yang siap kirim di Telegram.

Mendukung format Markdown (untuk Telegram) dan Plain Text (untuk copy-paste).
"""

import logging

logger = logging.getLogger(__name__)


def _escape_markdown(text: str) -> str:
    """Escape karakter khusus Telegram MarkdownV2.

    Telegram MarkdownV2 memerlukan escape untuk karakter:
    _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    special_chars = r"_*[]()~`>#+-=|{}.!"
    escaped = []
    for char in text:
        if char in special_chars:
            escaped.append("\\")
        escaped.append(char)
    return "".join(escaped)


def format_product_markdown(product: dict) -> str:
    """Format data produk menjadi pesan Telegram (Markdown).

    Args:
        product: dict berisi data produk dari copywriter agent.

    Returns:
        String pesan terformat untuk Telegram.
    """
    title = product.get("title", "Produk Tanpa Judul")
    category = product.get("category", "-")
    description = product.get("description", "Tidak ada deskripsi.")
    tags = product.get("tags", [])
    cover_prompt = product.get("cover_prompt", "-")
    content_prompt = product.get("content_prompt", "-")
    cta = product.get("cta", "")

    # Handle harga — bisa berupa string atau dict
    price_data = product.get("price", "-")
    if isinstance(price_data, dict):
        price_promo = price_data.get("promo", "-")
        price_normal = price_data.get("normal", "-")
        price_text = f"{price_promo} (Normal: {price_normal})"
    else:
        price_text = str(price_data)

    # Format tags sebagai string
    if isinstance(tags, list):
        tags_text = ", ".join(str(tag) for tag in tags)
    else:
        tags_text = str(tags)

    message_lines = [
        f"📦 *PRODUK: {_escape_markdown(title)}*",
        f"📂 Kategori: {_escape_markdown(category)}",
        f"💰 Harga: {_escape_markdown(price_text)}",
        "",
        f"📝 *Deskripsi:*",
        _escape_markdown(description),
        "",
        f"🏷️ *Tag:* {_escape_markdown(tags_text)}",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"🖼️ *Prompt Cover \\(copy untuk generate gambar\\):*",
        f"`{cover_prompt}`",
        "",
        f"🖼️ *Prompt Isi/Preview:*",
        f"`{content_prompt}`",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    if cta:
        message_lines.extend([
            "",
            f"📣 *CTA:* {_escape_markdown(cta)}",
        ])

    return "\n".join(message_lines)


def format_product_plain(product: dict) -> str:
    """Format data produk menjadi plain text (mudah di-copy-paste).

    Args:
        product: dict berisi data produk dari copywriter agent.

    Returns:
        String pesan plain text.
    """
    title = product.get("title", "Produk Tanpa Judul")
    category = product.get("category", "-")
    description = product.get("description", "Tidak ada deskripsi.")
    tags = product.get("tags", [])
    cover_prompt = product.get("cover_prompt", "-")
    content_prompt = product.get("content_prompt", "-")
    cta = product.get("cta", "")

    # Handle harga
    price_data = product.get("price", "-")
    if isinstance(price_data, dict):
        price_promo = price_data.get("promo", "-")
        price_normal = price_data.get("normal", "-")
        price_text = f"{price_promo} (Normal: {price_normal})"
    else:
        price_text = str(price_data)

    # Format tags
    if isinstance(tags, list):
        tags_text = ", ".join(str(tag) for tag in tags)
    else:
        tags_text = str(tags)

    lines = [
        f"📦 PRODUK: {title}",
        f"📂 Kategori: {category}",
        f"💰 Harga: {price_text}",
        "",
        "📝 Deskripsi:",
        description,
        "",
        f"🏷️ Tag: {tags_text}",
        "",
        "========================",
        "",
        "🖼️ Prompt Cover (copy untuk generate gambar):",
        cover_prompt,
        "",
        "🖼️ Prompt Isi/Preview:",
        content_prompt,
        "",
        "========================",
    ]

    if cta:
        lines.extend([
            "",
            f"📣 CTA: {cta}",
        ])

    return "\n".join(lines)
