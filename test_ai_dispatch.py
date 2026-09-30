import requests
import json

BASE = "http://127.0.0.1:8000"

print("--- TEST 1: Tüm Şirket (Hepsi) + Otomatik AI Senaryo Eşleme ---")
payload_all = {
    "ad": "2026 Otomatik AI Tüm Şirket Tatbikatı",
    "sirket_id": 1,
    "hedef_departman": "hepsi",
    "kanal": "email",
    "otomatik_ai": True
}
r1 = requests.post(f"{BASE}/kampanyalar/baslat", json=payload_all)
print("Durum Kodu:", r1.status_code)
d1 = r1.json()
print("Toplam Hedef Çalışan:", d1.get("toplam_hedef_calisan"))
loglar1 = d1.get("dagitim_raporu", {}).get("loglar", [])
print(f"Dağıtılan toplam log sayısı: {len(loglar1)}")
for l in loglar1[:7]:
    print(f" - [{l['sira']}] {l['calisan_adi']} ({l['departman']}) -> {l['sablon_adi']}")

print("\n--- TEST 2: Tek Departman Hedefleme: Sadece 'Bilgi İşlem (IT)' ---")
payload_it = {
    "ad": "2026 IT WhatsApp Siber Güvenlik Tatbikatı",
    "sirket_id": 1,
    "hedef_departman": "Bilgi İşlem (IT)",
    "kanal": "whatsapp",
    "otomatik_ai": True
}
r2 = requests.post(f"{BASE}/kampanyalar/baslat", json=payload_it)
print("Durum Kodu:", r2.status_code)
d2 = r2.json()
print("Toplam Hedef IT Çalışanı:", d2.get("toplam_hedef_calisan"))
loglar2 = d2.get("dagitim_raporu", {}).get("loglar", [])
for l in loglar2:
    print(f" - [{l['sira']}] {l['calisan_adi']} ({l['departman']}) -> {l['sablon_adi']} (Kanal: {l['kanal']})")

print("\n--- TEST 3: Tek Departman Hedefleme: Sadece 'İnsan Kaynakları (İK)' ---")
payload_ik = {
    "ad": "2026 İK Özel SMS Tatbikatı",
    "sirket_id": 1,
    "hedef_departman": "İnsan Kaynakları (İK)",
    "kanal": "sms",
    "otomatik_ai": True
}
r3 = requests.post(f"{BASE}/kampanyalar/baslat", json=payload_ik)
print("Durum Kodu:", r3.status_code)
d3 = r3.json()
print("Toplam Hedef İK Çalışanı:", d3.get("toplam_hedef_calisan"))
loglar3 = d3.get("dagitim_raporu", {}).get("loglar", [])
for l in loglar3:
    print(f" - [{l['sira']}] {l['calisan_adi']} ({l['departman']}) -> {l['sablon_adi']} (Kanal: {l['kanal']})")

print("\n--- TEST 4: /dashboard HTML Kontrolleri ---")
r4 = requests.get(f"{BASE}/dashboard")
print("Dashboard HTTP:", r4.status_code)
assert "phishaware_theme') || 'classic'" in r4.text, "Varsayılan tema classic olmalı!"
assert "🛡️" in r4.text, "Logo kalkan emojisi olmalı!"
assert "hedefDepartman" in r4.text, "Hedef departman seçicisi mevcut olmalı!"
assert "Atanan Oltalama Senaryosu" in r4.text, "Tabloda Atanan Senaryo sütunu mevcut olmalı!"
print("Tüm doğrulamalar başarıyla geçti!")
