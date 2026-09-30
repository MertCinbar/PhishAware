import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("--- ASAMA 5 TESTLERI BASLIYOR ---\n")

r_csv = client.get("/rapor/csv/1")
assert r_csv.status_code == 200, f"CSV Indirme Hatasi: {r_csv.text}"
assert "text/csv" in r_csv.headers.get("content-type", "")
assert "attachment; filename=" in r_csv.headers.get("content-disposition", "")

csv_text = r_csv.content.decode("utf-8-sig")
assert "Calisan ID" in csv_text or "Çalışan ID" in csv_text
assert "Departman" in csv_text
assert "Risk Puani" in csv_text or "Risk Puanı" in csv_text
assert "Mert Cinbar" in csv_text or "Mert Çinbar" in csv_text

print("[OK] Resmi Kurumsal CSV Denetim Raporu basariyla uretildi ve indirildi!")
print(f"      Rapor Boyutu: {len(r_csv.content)} bayt")
print(f"      Baslik Satiri: {csv_text.splitlines()[0]}")

r_dash = client.get("/dashboard")
assert r_dash.status_code == 200
dash_html = r_dash.text

assert "CSV Denetim Raporu" in dash_html, "CSV Butonu Dashboard'da bulunamadi"
assert "Raporu Yazdir" in dash_html or "Raporu Yazdır" in dash_html, "Print Butonu Dashboard'da bulunamadi"
assert "Yeni Simulasyon Tatbikati Baslat" in dash_html or "Yeni Simülasyon Tatbikatı Başlat" in dash_html, "Hizli Baslatici Dashboard'da bulunamadi"
assert "yeniKampanyaBaslat" in dash_html, "Kampanya Baslatma JS fonksiyonu bulunamadi"
assert "Aktif Kampanya Hedef Calisanlari" in dash_html or "Aktif Kampanya Hedef Çalışanları" in dash_html or "Aktif Kampanya Hedef Takip Masası" in dash_html, "Hedef calisanlar tablosu bulunamadi"

print("[OK] Dashboard Asama 5 Operasyon Merkezi (Kampanya Baslatici + CSV Export + Print CSS) basariyla yerlesti!")

yeni_kampanya_payload = {
    "ad": "Asama 5 Guvenlik Testi Tatbikati",
    "sirket_id": 1,
    "sablon_id": 1
}
r_kamp = client.post("/kampanyalar/baslat", json=yeni_kampanya_payload)
assert r_kamp.status_code == 200, f"Kampanya baslatma hatasi: {r_kamp.text}"
kamp_data = r_kamp.json()

print(f"[OK] Yeni Kampanya Olusturuldu: '{kamp_data['kampanya_adi']}'")
print(f"      Hedeflenen Calisan Sayisi: {kamp_data['toplam_hedef_calisan']}")
assert len(kamp_data["hedefler"]) > 0
print(f"      Ornek Simule Link: {kamp_data['hedefler'][0]['simule_link']}")

print("\n[TEBRIKLER] ASAMA 5 TUM TESTLERI BASARIYLA GECTI!")
