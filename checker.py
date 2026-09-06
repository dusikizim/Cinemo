#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta

import requests
from playwright.async_api import async_playwright, Error as PlaywrightError


# ─── KULLANICI KANAL LİSTESİ ──────────────────────────────────────────────────
KANALLAR = [
    
    {
        "name": "uktntsports1",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=TNT%20Sports%201&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "uktntsports2",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=TNT%20Sports%202&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "uktntsports3",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=TNT%20Sports%203&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "uktntsports4",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=TNT%20Sports%204&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "uktntsportsultimate",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=TNT%20Sports%20Ultimate&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukskysportsmainevent",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Sky%20Sports%20Main%20Event&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukskysportspremierleague",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Sky%20Sports%20Premier%20League&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukskysportsfootball",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Sky%20Sports%20Football&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukskysportsf1",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Sky%20Sports%20F1&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukskysportscricket",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Sky%20Sports%20Cricket&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukskysportsgolf",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Sky%20Sports%20Golf&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukskysportsaction",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Sky%20Sports%20Action&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukskysportsarena",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Sky%20Sports%20Arena&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukskysportstennis",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Sky%20Sports%20Tennis&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukskysportsmix",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Sky%20Sports%20Mix&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukskysportsnews",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Sky%20Sports%20News&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukskysportsracing",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Sky%20Sports%20Racing&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukpremiersports1",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Premier%20Sports%201&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukpremiersports2",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Premier%20Sports%202&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukeurosport1",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Eurosport%201&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukeurosport2",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=Eurosport%202&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    {
        "name": "ukbbcone",
        "url": "https://cdnlivetv.tv/api/v1/channels/player/?name=BBC%20One&code=gb&user=cdnlivetv&plan=free",
        "group": "uk"
    },
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📂 Yazma İşlemi Başlatıldı (Klasör: {target_dir})")

    if not items:
        print("   ⚠️ Yazılacak başarılı kanal bulunamadı.")
        return

    for ch in items:
        name = ch["name"]
        stream = ch["stream_url"]

        # Dosya adı için geçersiz karakterleri temizle
        safe_name = sanitize_filename(name)
        file_path = target_dir / f"{safe_name}.m3u8"

        # İstenen formatta M3U8 dosyasını yaz:
        # #EXTM3U
        # #EXT-X-VERSION:3
        # #EXT-X-STREAM-INF:BANDWIDTH=8000000
        # Yayın linki
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                f.write("#EXT-X-VERSION:3\n")
                f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth}\n")
                f.write(f"{stream}\n")
            print(f"   💾 Yazıldı: {file_path.name}")
        except Exception as e:
            print(f"   ❌ Dosya yazma hatası ({name}): {e}")


def print_report(channels: list, success: list, failed: list):
    turkey_tz = timezone(timedelta(hours=3))
    now = datetime.now(turkey_tz).strftime("%d.%m.%Y %H:%M:%S")

    print(f"\n{'═'*65}")
    print(f"📊 SONUÇ RAPORU")
    print(f"{'═'*65}")
    print(f"  📺 Girilen kanal sayısı  : {len(channels)}")
    print(f"  ✅ Başarıyla çözülen     : {len(success)}")
    print(f"  ❌ Başarısız olan        : {len(failed)}")
    print(f"  📁 Çıktı Klasör Yolu     : ./{OUTPUT_DIR_NAME}/")
    print(f"  🕐 Güncelleme zamanı     : {now}")
    print(f"{'═'*65}\n")


async def main():
    print("═" * 65)
    print("   📺 ÖZEL LİSTE — ÇOKLU KANAL AYRI DOSYA KAYDEDİCİ")
    print("═" * 65 + "\n")

    if not KANALLAR:
        print("⚠️  Lütfen 'KANALLAR' listesine en az bir kanal ekleyin.")
        return

    print(f"📋 İşlenecek kanal sayısı: {len(KANALLAR)}")
    print(f"⚡ Eşzamanlı Sekme       : {MAX_CONCURRENT}")
    print(f"📁 Klasör Hedefi         : ./{OUTPUT_DIR_NAME}/\n")

    success, failed = await process_all(KANALLAR)

    # Kanalları ayrı dosyalar halinde yazdır
    write_individual_m3u8(success, OUTPUT_DIR_NAME)

    with open(DEBUG_FILE, "w", encoding="utf-8") as f:
        json.dump(failed, f, ensure_ascii=False, indent=2)

    print_report(KANALLAR, success, failed)
    print(f"✅ Başarıyla tamamlandı! Çalışan kanallar './{OUTPUT_DIR_NAME}/' klasörüne kaydedildi.\n")


if __name__ == "__main__":
    asyncio.run(main())
