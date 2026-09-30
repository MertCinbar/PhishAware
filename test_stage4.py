import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("--- AŞAMA 4 TESTLERİ BAŞLIYOR ---\n")

r_analitik = client.get("/analitik/sirket/1")
assert r_analitik.status_code == 200, f"Hata: {r_analitik.text}"
data = r_analitik.json()

print(f"[OK] Şirket Analitiği Çekildi: {data['sirket_adi']} ({data['sektor']})")
print("\n--- DEPARTMAN BAZLI ZAAFİYET TABLOSU ---")
for dep in data["departmanlar"]:
    print(f"  * {dep['departman']}: Toplam {dep['toplam']} kişi | Tuzağa Düşen: {dep['tiklayan']} | Risk: %{dep['oran']}")

ai_rapor = data["ai_danismani"]
print(f"\n--- [AI] GUVENLIK DANISMANI (CISO ADVISOR) RAPORU ---")
print(f"En Riskli Departman: {ai_rapor.get('en_riskli_departman')}")
print(f"Genel Değerlendirme: {ai_rapor.get('genel_degerlendirme')}")
print("Yönetim Eylem Planı:")
for oneri in ai_rapor.get("aksiyon_onerileri", []):
    print(f"  -> {oneri}")

r_dash = client.get("/dashboard")
assert r_dash.status_code == 200
assert "Departman Zaafiyet Dağılımı" in r_dash.text
assert "CISO Güvenlik" in r_dash.text or "AI Güvenlik" in r_dash.text
print("\n[OK] Dashboard'da Departman İlerleme Çubukları ve AI Danışmanı başarıyla yerleşti!")

print("\n[TEBRİKLER] AŞAMA 4 TÜM TESTLERİ BAŞARIYLA GEÇTİ!")
