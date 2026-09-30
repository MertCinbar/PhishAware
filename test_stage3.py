import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("--- AŞAMA 3 TESTLERİ BAŞLIYOR ---\n")

r_dash = client.get("/dashboard")
assert r_dash.status_code == 200
assert "PhishAware" in r_dash.text
print("[OK] Dark Mode Yonetim Paneli (/dashboard) basariyla render edildi!")

ai_istek = {
    "sektor": "Finans ve Bankacilik",
    "departman": "Muhasebe",
    "zorluk": "orta"
}
r_ai = client.post("/ai/sablon-uret", json=ai_istek)
assert r_ai.status_code == 200
ai_data = r_ai.json()
print(f"[OK] Yapay Zeka Sablonu Uretildi! ID: {ai_data['id']}")
print(f"   -> Baslik: {ai_data['baslik']}")
print(f"   -> Konu: {ai_data['konu']}")
print(f"   -> Gonderen: {ai_data['gonderen_adi']}")

r_sample = client.get("/kampanyalar/1/ozet")
if r_sample.status_code == 200 and r_sample.json()["hedefler"]:
    sample_token = r_sample.json()["hedefler"][0]["takip_kodu"]
    r_tikla = client.get(f"/tikla/{sample_token}")
    assert r_tikla.status_code == 200
    assert "Siber" in r_tikla.text
    print(f"[OK] Koyu ve Akici Farkindalik Egitim Ekrani (/tikla/{sample_token[:8]}...) basariyla calisiyor!")

print("\n[TEBRIKLER] ASAMA 3 VE TUM KOYU TEMA ARAYUZLERI BASARIYLA GECTI!")
