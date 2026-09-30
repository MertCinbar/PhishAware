import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
import app.models as models

def verileri_doldur():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    sirket = db.query(models.Sirket).first()
    if not sirket:
        sirket = models.Sirket(
            ad="TrendLojistik A.S.",
            sektor="E-Ticaret ve Lojistik"
        )
        db.add(sirket)
        db.commit()
        db.refresh(sirket)
        print(f"[OK] Sirket eklendi: {sirket.ad} (ID: {sirket.id})")

    calisan_var_mi = db.query(models.Calisan).first()
    if not calisan_var_mi:
        calisanlar = [
            models.Calisan(sirket_id=sirket.id, ad_soyad="Mert Cinbar", email="mert@trendlojistik.com", departman="Bilgi Islem (IT)", risk_puani=0),
            models.Calisan(sirket_id=sirket.id, ad_soyad="Ayse Yilmaz", email="ayse@trendlojistik.com", departman="Muhasebe", risk_puani=15),
            models.Calisan(sirket_id=sirket.id, ad_soyad="Mehmet Demir", email="mehmet@trendlojistik.com", departman="Insan Kaynaklari", risk_puani=5),
        ]
        db.add_all(calisanlar)
        db.commit()
        print(f"[OK] {len(calisanlar)} adet ornek calisan eklendi.")

    sablon_var_mi = db.query(models.Sablon).first()
    if not sablon_var_mi:
        sablon = models.Sablon(
            baslik="Acil Kargo Teslimat Uyarisi",
            konu="[ONEMLI] Gonderiniz teslim edilemedi!",
            gonderen_adi="Hizli Kargo Musteri Hizmetleri",
            icerik_html="""<p>Kargonuz adres yetersizligi nedeniyle teslim edilemedi. Adresinizi guncelleyin: <a href="{{LINK}}">Tiklayin</a></p>""",
            yapay_zeka_ile_mi=False
        )
        db.add(sablon)
        db.commit()
        print(f"[OK] Ornek sablon eklendi: {sablon.baslik}")

    db.close()
    print("[BASARILI] Tum ornek veriler hazir!")

if __name__ == "__main__":
    verileri_doldur()
