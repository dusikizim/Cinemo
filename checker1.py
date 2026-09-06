#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
import base64
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta

import requests
from playwright.async_api import async_playwright, Error as PlaywrightError


# ─── KULLANICI KANAL LİSTESİ (Buraya dilediğiniz kadar link ekleyebilirsiniz) ───
KANALLAR = [
    {
        "name": "Bein 1",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=beIN%20SPORTS%201&code=tr&user=cdnlivetv&plan=free",
        "image": "https://img-s-msn-com.akamaized.net/tenant/amp/entityid/AA1pt7gT.img", # İsteğe bağlı logo
        "group": "ULUSAL"  # İsteğe bağlı kategori
    },
    {
        "name": "bein 2",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=beIN%20SPORTS%202&code=tr&user=cdnlivetv&plan=free",
        "image": "",
        "group": "ULUSAL"
    },
    {
        "name": "TRT 1",
        "url": "https://cdnlivetv.tv/player.php?id=trt1",
        "image": "",
        "group": "TRT"
    }
]

# ─── GITHUB AYARLARI ──────────────────────────────────────────────────────────
# Yeni oluşturduğunuz Token'ı buraya yazın:
GITHUB_TOKEN = "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"

GITHUB_REPO = "kadirsener1/avva"
GITHUB_PATH = "playlist.m3u"
GITHUB_BRANCH = "main"

# ─── SİSTEM AYARLARI ──────────────────────────────────────────────────────────
OUTPUT_FILE = "playlist.m3u"
REMOTE_M3U_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/{GITHUB_BRANCH}/{GITHUB_PATH}"
DEBUG_FILE = "debug_failed.json"

TIMEOUT = 15000                 # Sayfa yükleme zaman aşımı (15s)
FIRST_WAIT = 3.0                # İlk yüklemede akış bekleme süresi (sn)
RELOAD_WAIT = 4.5               # Yenileme sonrası bekleme süresi (sn)
MAX_CONCURRENT = 4              # Eşzamanlı sekme sayısı

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
    "Referer": "https://cdnlivetv.tv/",
    "Origin": "https://cdnlivetv.tv",
}

BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--mute-audio",
    "--ignore-certificate-errors",
    "--ignore-ssl-errors",
    "--disable-extensions",
    "--disable-background-networking",
    "--hide-scrollbars",
    "--autoplay-policy=no-user-gesture-required",
    "--disable-blink-features=AutomationControlled",
]

BLOCKED_RESOURCE_TYPES = {"image", "media", "font"}


def is_valid_stream_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False

    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        return False

    invalid_chars = [
        " ", "{", "}", "<", ">", '"', "'", "`", ";", "(", ")",
        "\\", "\n", "\r", "\t", "&&", "||", "import", "function"
    ]
    if any(c in url for c in invalid_chars):
        return False

    junk_keywords = ["parser", "bundle", "webpack", "chunk", "worker", "player.min"]
    url_lower = url.lower()
    if any(k in url_lower for k in junk_keywords):
        return False

    base_path = url.split("?")[0].lower()
    if not (".m3u8" in base_path or ".mpd" in base_path):
        return False

    return True


def extract_from_html(html_text: str, base_url: str = "") -> str:
    if not html_text:
        return ""

    html_text = html_text.replace("\\/", "/").replace("\\u0026", "&")
    pattern = r'https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&*+,;=%]+\.(?:m3u8|mpd)(?:\?[a-zA-Z0-9\-._~:/?#\[\]@!$&*+,;=%]*)?'

    matches = re.findall(pattern, html_text, re.IGNORECASE)
    for m in matches:
        if is_valid_stream_url(m):
            return m

    return ""

                extinf += f' tvg-logo="{logo}"'
            if group:
                extinf += f' group-title="{group}"'
            extinf += f',{sc["name"]}'

            final_channels.append({
                "extinf": extinf,
                "stream_url": sc["stream_url"]
            })
            processed_keys.add(sc_key)

    # 4. M3U İçeriğini Oluştur
    output_lines = [
        "#EXTM3U",
        f"# Son guncelleme : {now} (TR)",
        f"# Kanal sayisi   : {len(final_channels)}\n"
    ]
    for ch in final_channels:
        output_lines.append(ch["extinf"])
        output_lines.append(ch["stream_url"] + "\n")
        
    full_m3u_content = "\n".join(output_lines)

    # Yerel dosyaya yaz
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_m3u_content)
    except Exception as e:
        print(f"⚠️ Yerel dosya yazılırken hata: {e}")

    # 5. DOĞRUDAN GITHUB REPOSUNA GÖNDER
    upload_to_github(full_m3u_content)


def print_report(channels: list, success: list, failed: list):
    turkey_tz = timezone(timedelta(hours=3))
    now = datetime.now(turkey_tz).strftime("%d.%m.%Y %H:%M:%S")

    print(f"\n{'═'*65}")
    print(f"📊 SONUÇ RAPORU")
    print(f"{'═'*65}")
    print(f"  📺 Taranan kanal sayısı  : {len(channels)}")
    print(f"  ✅ Başarıyla çözülen     : {len(success)}")
    print(f"  ❌ Başarısız olan        : {len(failed)}")
    print(f"  📁 Çıktı Dosyası         : {OUTPUT_FILE}")
    print(f"  🕐 Güncelleme zamanı     : {now}")
    print(f"{'═'*65}\n")


async def main():
    print("═" * 65)
    print("   📺 ÖZEL LİSTE — GITHUB ENTEGRASYONLU STREAM AYIKLAYICI")
    print("═" * 65 + "\n")

    if not KANALLAR:
        print("⚠️ Lütfen kodun başındaki 'KANALLAR' listesine en az bir link ekleyin.")
        return

    print(f"📋 İşlenecek kanal sayısı: {len(KANALLAR)}")
    print(f"⚡ Eşzamanlı Sekme       : {MAX_CONCURRENT}")
    print(f"🛡️  URL Doğrulayıcı       : Aktif\n")

    success, failed = await process_all(KANALLAR)

    write_m3u(success, OUTPUT_FILE)

    with open(DEBUG_FILE, "w", encoding="utf-8") as f:
        json.dump(failed, f, ensure_ascii=False, indent=2)

    print_report(KANALLAR, success, failed)


if __name__ == "__main__":
    asyncio.run(main())
