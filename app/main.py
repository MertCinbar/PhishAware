from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import uuid
import csv
import io
import socket
import qrcode
import os

from app.database import engine, get_db, Base
import app.models as models
import app.schemas as schemas
from app.ai_generator import senaryo_uret, risk_analizi_yorumu
from app.dispatcher import (
    toplu_otomatik_dagitim, 
    gercek_smtp_mail_gonder, 
    maskelenmis_gonderici_belirle,
    env_yukle,
    env_guncelle
)

def get_lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PhishAware - Oltalama Simülasyon & Farkındalık API",
    description="Şirketler için siber güvenlik oltalama tatbikatı, YZ senaryo üretimi, departman analitiği ve risk platformu.",
    version="2.1.0"
)

@app.get("/", tags=["Genel"])
def ana_sayfa():
    return {
        "sistem": "PhishAware API",
        "durum": "Aktif",
        "mesaj": "Veritabanı bağlantısı başarılı! Yönetim paneli için /dashboard, API testleri için /docs adresine gidin."
    }

@app.post("/sirketler/", response_model=schemas.SirketCevap, tags=["Şirketler"])
def sirket_olustur(sirket: schemas.SirketOlustur, db: Session = Depends(get_db)):
    yeni_sirket = models.Sirket(
        ad=sirket.ad,
        sektor=sirket.sektor
    )
    db.add(yeni_sirket)
    db.commit()
    db.refresh(yeni_sirket)
    return yeni_sirket

@app.get("/sirketler/", response_model=List[schemas.SirketCevap], tags=["Şirketler"])
def sirketleri_listele(db: Session = Depends(get_db)):
    return db.query(models.Sirket).all()

@app.post("/calisanlar/", response_model=schemas.CalisanCevap, tags=["Çalışanlar"])
def calisan_ekle(calisan: schemas.CalisanOlustur, db: Session = Depends(get_db)):
    sirket = db.query(models.Sirket).filter(models.Sirket.id == calisan.sirket_id).first()
    if not sirket:
        raise HTTPException(status_code=404, detail="Belirtilen ID'ye sahip bir şirket bulunamadı!")

    yeni_calisan = models.Calisan(
        sirket_id=calisan.sirket_id,
        ad_soyad=calisan.ad_soyad,
        email=calisan.email,
        departman=calisan.departman
    )
    db.add(yeni_calisan)
    db.commit()
    db.refresh(yeni_calisan)
    return yeni_calisan

@app.get("/calisanlar/", response_model=List[schemas.CalisanCevap], tags=["Çalışanlar"])
def calisanlari_listele(sirket_id: int = None, db: Session = Depends(get_db)):
    sorgu = db.query(models.Calisan)
    if sirket_id:
        sorgu = sorgu.filter(models.Calisan.sirket_id == sirket_id)
    return sorgu.all()

@app.post("/sablonlar/", response_model=schemas.SablonCevap, tags=["Şablonlar"])
def sablon_olustur(sablon: schemas.SablonOlustur, db: Session = Depends(get_db)):
    yeni_sablon = models.Sablon(
        baslik=sablon.baslik,
        konu=sablon.konu,
        gonderen_adi=sablon.gonderen_adi,
        icerik_html=sablon.icerik_html,
        yapay_zeka_ile_mi=sablon.yapay_zeka_ile_mi
    )
    db.add(yeni_sablon)
    db.commit()
    db.refresh(yeni_sablon)
    return yeni_sablon

@app.get("/sablonlar/", response_model=List[schemas.SablonCevap], tags=["Şablonlar"])
def sablonlari_listele(db: Session = Depends(get_db)):
    return db.query(models.Sablon).all()


@app.post("/ai/sablon-uret", response_model=schemas.SablonCevap, tags=["Yapay Zeka (AI) Modülü"])
def yapay_zeka_ile_sablon_uret(istek: schemas.AISablonIstek, db: Session = Depends(get_db)):
    uretilen = senaryo_uret(
        sektor=istek.sektor,
        departman=istek.departman,
        zorluk=istek.zorluk,
        kanal=istek.kanal
    )

    yeni_sablon = models.Sablon(
        baslik=uretilen.get("baslik", f"{istek.sektor} - {istek.departman} ({istek.kanal.upper()}) Senaryosu"),
        konu=uretilen.get("konu", "Hesabınızla ilgili önemli bildirim"),
        gonderen_adi=uretilen.get("gonderen_adi", "Kurumsal Sistem Yönetimi"),
        icerik_html=uretilen.get("icerik_html", "<p>Bildirim detayları için <a href='{{LINK}}'>tıklayınız</a>.</p>"),
        yapay_zeka_ile_mi=True,
        kanal=istek.kanal
    )
    db.add(yeni_sablon)
    db.commit()
    db.refresh(yeni_sablon)
    return yeni_sablon


@app.get("/analitik/sirket/{sirket_id}", tags=["Analitik & Risk Raporu"])
def sirket_risk_analitigi(sirket_id: int, db: Session = Depends(get_db)):
    sirket = db.query(models.Sirket).filter(models.Sirket.id == sirket_id).first()
    if not sirket:
        raise HTTPException(status_code=404, detail="Şirket bulunamadı!")

    dep_dict = {}
    for calisan in sirket.calisanlar:
        dep = calisan.departman
        if dep not in dep_dict:
            dep_dict[dep] = {"departman": dep, "toplam": 0, "tiklayan": 0, "toplam_risk": 0}

        dep_dict[dep]["toplam"] += 1
        dep_dict[dep]["toplam_risk"] += calisan.risk_puani

        if any(log.tiklandi_mi for log in calisan.simulasyon_loglari):
            dep_dict[dep]["tiklayan"] += 1

    departman_istatistikleri = []
    for dep, v in dep_dict.items():
        oran = round((v["tiklayan"] / v["toplam"]) * 100, 1) if v["toplam"] > 0 else 0.0
        departman_istatistikleri.append({
            "departman": dep,
            "toplam": v["toplam"],
            "tiklayan": v["tiklayan"],
            "oran": oran,
            "ortalama_risk": round(v["toplam_risk"] / v["toplam"], 1) if v["toplam"] > 0 else 0
        })

    ai_tavsiye = risk_analizi_yorumu(departman_istatistikleri)

    return {
        "sirket_id": sirket.id,
        "sirket_adi": sirket.ad,
        "sektor": sirket.sektor,
        "departmanlar": departman_istatistikleri,
        "ai_danismani": ai_tavsiye
    }


@app.get("/rapor/csv/{sirket_id}", tags=["Analitik & Risk Raporu"])
def sirket_raporu_csv(sirket_id: int, db: Session = Depends(get_db)):
    sirket = db.query(models.Sirket).filter(models.Sirket.id == sirket_id).first()
    if not sirket:
        raise HTTPException(status_code=404, detail="Şirket bulunamadı!")

    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';')

    writer.writerow([
        "Çalışan ID",
        "Ad Soyad",
        "E-Posta",
        "Departman",
        "Risk Puanı",
        "Kampanya Adı",
        "Tuzağa Düştü mü?",
        "Tıklanma Tarihi",
        "Eğitimi Tamamladı mı?"
    ])

    for calisan in sirket.calisanlar:
        if not calisan.simulasyon_loglari:
            writer.writerow([
                calisan.id,
                calisan.ad_soyad,
                calisan.email,
                calisan.departman,
                calisan.risk_puani,
                "Katılmadı",
                "Hayır (Güvenli)",
                "-",
                "Hayır"
            ])
        else:
            for log in calisan.simulasyon_loglari:
                kampanya_adi = log.kampanya.ad if log.kampanya else "Bilinmiyor"
                tarih_str = log.tiklanma_tarihi.strftime("%d.%m.%Y %H:%M") if log.tiklanma_tarihi else "-"
                writer.writerow([
                    calisan.id,
                    calisan.ad_soyad,
                    calisan.email,
                    calisan.departman,
                    calisan.risk_puani,
                    kampanya_adi,
                    "EVET (Zaafiyet)" if log.tiklandi_mi else "Hayır (Güvenli)",
                    tarih_str,
                    "EVET (Tamamlandı)" if log.egitim_tamamlandi_mi else "Hayır"
                ])

    csv_icerik = output.getvalue()
    dosya_adi = f"PhishAware_Denetim_Sirket_{sirket_id}.csv"
    return Response(
        content=csv_icerik,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={dosya_adi}"
        }
    )


@app.post("/kampanyalar/baslat", response_model=schemas.KampanyaOzet, tags=["Kampanyalar & Simülasyon"])
def kampanya_baslat(istek: schemas.KampanyaOlustur, db: Session = Depends(get_db)):
    sirket = db.query(models.Sirket).filter(models.Sirket.id == istek.sirket_id).first()
    if not sirket:
        raise HTTPException(status_code=404, detail="Şirket bulunamadı!")

    if not sirket.calisanlar:
        raise HTTPException(status_code=400, detail="Bu şirkete kayıtlı hiç çalışan yok! Önce çalışan ekleyin.")

    hedef_dep = (istek.hedef_departman or "hepsi").strip()
    if hedef_dep.lower() in ["hepsi", "all", "tüm şirket", "tum sirket", ""]:
        hedef_calisanlar = list(sirket.calisanlar)
    else:
        hedef_calisanlar = [c for c in sirket.calisanlar if c.departman.strip().lower() == hedef_dep.lower()]
        if not hedef_calisanlar:
            hedef_calisanlar = [c for c in sirket.calisanlar if (hedef_dep.lower() in c.departman.lower() or c.departman.lower() in hedef_dep.lower())]

    if not hedef_calisanlar:
        raise HTTPException(
            status_code=400, 
            detail=f"'{hedef_dep}' departmanında kayıtlı çalışan bulunamadı! Lütfen listeden geçerli bir departman seçin."
        )

    sablon = None
    if istek.sablon_id and istek.sablon_id > 0:
        sablon = db.query(models.Sablon).filter(models.Sablon.id == istek.sablon_id).first()

    secilen_kanal = istek.kanal or (getattr(sablon, "kanal", "email") if sablon else "email")

    if not sablon:
        sablon = db.query(models.Sablon).filter(models.Sablon.kanal == secilen_kanal).first()
        if not sablon:
            sablon = models.Sablon(
                baslik=f"Akıllı Oltalama ({secilen_kanal.upper()})",
                konu="[ÖNEMLİ] Güvenlik Bildirimi",
                gonderen_adi="Kurumsal Bilgi Güvenliği Masası",
                icerik_html="<p>Lütfen güvenlik bildirimini inceleyin: <a href='{{LINK}}'>Tıklayınız</a></p>",
                yapay_zeka_ile_mi=True,
                kanal=secilen_kanal
            )
            db.add(sablon)
            db.commit()
            db.refresh(sablon)

    kampanya = models.Kampanya(
        sirket_id=sirket.id,
        sablon_id=sablon.id,
        ad=istek.ad,
        durum="aktif"
    )
    db.add(kampanya)
    db.commit()
    db.refresh(kampanya)

    otomatik_ai = True if istek.otomatik_ai is None else istek.otomatik_ai
    dagitim_sonucu = toplu_otomatik_dagitim(
        kampanya, 
        hedef_calisanlar, 
        lan_ip=get_lan_ip(),
        hedef_departman=hedef_dep,
        kanal_override=secilen_kanal,
        otomatik_ai=otomatik_ai
    )

    hedefler_detay = []
    for log_kaydi, calisan in zip(dagitim_sonucu["loglar"], hedef_calisanlar):
        log = models.SimulasyonLog(
            kampanya_id=kampanya.id,
            calisan_id=calisan.id,
            takip_kodu=log_kaydi["takip_kodu"],
            mail_gonderildi_mi=True,
            senaryo_adi=log_kaydi.get("sablon_adi")
        )
        db.add(log)

        hedefler_detay.append(
            schemas.SimulasyonLogDetay(
                id=0,
                calisan_adi=calisan.ad_soyad,
                calisan_email=calisan.email,
                departman=calisan.departman,
                takip_kodu=log_kaydi["takip_kodu"],
                simule_link=log_kaydi["takip_linki"],
                tiklandi_mi=False,
                egitim_tamamlandi_mi=False,
                senaryo_adi=log_kaydi.get("sablon_adi")
            )
        )

    db.commit()

    return schemas.KampanyaOzet(
        kampanya_id=kampanya.id,
        kampanya_adi=kampanya.ad,
        durum=kampanya.durum,
        hedef_departman=hedef_dep,
        toplam_hedef_calisan=len(hedef_calisanlar),
        tiklayan_sayisi=0,
        egitim_tamamlayan_sayisi=0,
        tiklanma_orani_yuzde=0.0,
        hedefler=hedefler_detay,
        dagitim_raporu=dagitim_sonucu
    )


@app.get("/tikla/{takip_kodu}", response_class=HTMLResponse, tags=["Kampanyalar & Simülasyon"])
def linke_tiklandi(takip_kodu: str, db: Session = Depends(get_db)):
    log = db.query(models.SimulasyonLog).filter(models.SimulasyonLog.takip_kodu == takip_kodu).first()

    if not log:
        return HTMLResponse(
            content="""<div style='background:#0f172a; color:#f87171; padding:40px; font-family:sans-serif; text-align:center;'><h2>Geçersiz veya Süresi Dolmuş Simülasyon Bağlantısı!</h2></div>""",
            status_code=404
        )

    if not log.tiklandi_mi:
        log.tiklandi_mi = True
        log.tiklanma_tarihi = datetime.utcnow()
        log.calisan.risk_puani += 10
        db.commit()

    sirket_adi = log.calisan.sirket.ad if log.calisan and log.calisan.sirket else "Kurumsal Sistem Masası"
    calisan_adi = log.calisan.ad_soyad if log.calisan else "Değerli Çalışanımız"
    departman_adi = log.calisan.departman if log.calisan else "Şirket Personeli"
    calisan_email = log.calisan.email if log.calisan else "kullanici@sirket.com"

    html_icerik = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{sirket_adi} - Güvenli Kimlik & Evrak Portalı</title>
        <style>
            :root {{
                --bg: #090d16;
                --surface: rgba(18, 27, 45, 0.9);
                --border: rgba(255, 255, 255, 0.1);
                --danger: #ef4444;
                --danger-glow: rgba(239, 68, 68, 0.35);
                --emerald: #10b981;
                --cyan: #06b6d4;
                --text: #f8fafc;
                --muted: #94a3b8;
            }}
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: var(--bg);
                background-image: radial-gradient(circle at 50% 15%, rgba(6, 182, 212, 0.08), transparent 50%);
                color: var(--text);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 24px 16px;
            }}
            .card {{
                background: var(--surface);
                backdrop-filter: blur(20px);
                max-width: 640px;
                width: 100%;
                border-radius: 20px;
                border: 1px solid var(--border);
                box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6);
                padding: 36px;
                transition: all 0.4s ease;
            }}

            /* 1. Ekran: Sahte Kurumsal Portal */
            .portal-badge {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: rgba(6, 182, 212, 0.15);
                color: var(--cyan);
                border: 1px solid rgba(6, 182, 212, 0.3);
                padding: 6px 14px;
                border-radius: 9999px;
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 20px;
            }}
            .form-input {{
                width: 100%;
                background: #060911;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 10px;
                padding: 12px 14px;
                color: #fff;
                font-size: 14px;
                outline: none;
                margin-top: 6px;
                margin-bottom: 16px;
            }}
            .btn-verify {{
                width: 100%;
                background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%);
                color: #fff;
                border: none;
                padding: 14px;
                border-radius: 12px;
                font-weight: 700;
                font-size: 15px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(6, 182, 212, 0.35);
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .btn-verify:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(6, 182, 212, 0.5); }}

            .btn-phishalert {{
                width: 100%;
                background: rgba(239, 68, 68, 0.12);
                color: #fca5a5;
                border: 1px solid rgba(239, 68, 68, 0.3);
                padding: 12px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 13px;
                cursor: pointer;
                margin-top: 12px;
                transition: background 0.2s;
            }}
            .btn-phishalert:hover {{ background: rgba(239, 68, 68, 0.25); color: #fff; }}

            /* 2. Ekran: Dramatik Hacklenme İfşası */
            .glitch-header {{
                background: rgba(239, 68, 68, 0.15);
                border: 1px solid var(--danger);
                border-radius: 14px;
                padding: 18px;
                margin-bottom: 24px;
                animation: redPulse 1.8s infinite;
            }}
            @keyframes redPulse {{
                0%, 100% {{ box-shadow: 0 0 15px rgba(239, 68, 68, 0.3); }}
                50% {{ box-shadow: 0 0 35px rgba(239, 68, 68, 0.6); }}
            }}
            .exposed-box {{
                background: #060911;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 22px;
                font-size: 13px;
            }}
            .exposed-row {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }}
            .exposed-row:last-child {{ border-bottom: none; }}
            .exposed-val {{ font-weight: 600; color: #f87171; }}

            .relief-badge {{
                background: rgba(16, 185, 129, 0.15);
                border: 1px solid rgba(16, 185, 129, 0.3);
                color: #34d399;
                padding: 12px 16px;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                margin-bottom: 20px;
            }}

            .tip-item {{
                display: flex;
                align-items: flex-start;
                gap: 10px;
                background: rgba(255, 255, 255, 0.03);
                padding: 10px 12px;
                border-radius: 8px;
                font-size: 13px;
                color: #cbd5e1;
                margin-bottom: 8px;
            }}

            .btn-finish {{
                width: 100%;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: #fff;
                border: none;
                padding: 14px;
                border-radius: 12px;
                font-weight: 700;
                cursor: pointer;
                margin-top: 16px;
                transition: transform 0.2s;
            }}
            .btn-finish:hover {{ transform: translateY(-2px); }}
        </style>
    </head>
    <body>
        <div class="card" id="screenTrap">
            <div class="portal-badge">{sirket_adi} Güvenli Kimlik Masası</div>
            <h1 style="font-size:20px; font-weight:700; margin-bottom:10px;">Kurumsal Belge & İşlem Doğrulama</h1>
            <p style="font-size:13px; color:var(--muted); line-height:1.6; margin-bottom:22px;">
                Sayın <strong>{calisan_adi}</strong> ({departman_adi}),<br>
                Tarafınıza tanımlanmış kurumsal operasyonel bildirimi incelemek için lütfen kimliğinizi doğrulayınız.
            </p>
            <div>
                <label style="font-size:12px; color:var(--muted); margin-bottom:4px; display:block;">Kurumsal E-Posta Adresi</label>
                <input type="text" class="form-input" value="{calisan_email}" disabled style="opacity:0.8; margin-bottom:12px;" />
            </div>
            <div>
                <label style="font-size:12px; color:var(--muted); margin-bottom:4px; display:block;">Kurumsal Parola / Tek Kullanımlık Kod</label>
                <input type="password" id="inputPass" class="form-input" value="••••••••" placeholder="Şirket parolanız" style="margin-bottom:18px;" />
            </div>
            <button class="btn-verify" onclick="tuzagaDus()">Kimliği Doğrula ve İlerle</button>
            <button class="btn-phishalert" onclick="supheliBildir()">PhishAlert: Şüpheli Bildir (Güvenlik Masasına İlet)</button>
        </div>

        <div class="card" id="screenBreach" style="display:none;">
            <div style="border-left: 3px solid #ef4444; padding-left: 14px; margin-bottom: 18px;">
                <div style="font-size:11px; font-weight:700; color:#ef4444; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Bilgi Güvenliği Tatbikatı</div>
                <h2 style="font-size:18px; color:#ffffff; font-weight:700;">Simüle Edilmiş Oltalama Bildirimi</h2>
            </div>
            <p style="font-size:13px; color:#cbd5e1; line-height:1.6; margin-bottom:16px;">
                Şirket içi siber güvenlik farkındalık simülasyonu kapsamında hazırlanan bir bağlantıya tıkladınız. 
                Bu kontrollü bir tatbikattır; girdiğiniz parola sisteme kaydedilmemiştir ve bilgileriniz güvendedir.
            </p>
            <div class="exposed-box">
                <div class="exposed-row">
                    <span style="color:var(--muted);">Hedef Personel:</span>
                    <span class="exposed-val" style="color:#f1f5f9;">{calisan_adi}</span>
                </div>
                <div class="exposed-row">
                    <span style="color:var(--muted);">Departman / Kurum:</span>
                    <span class="exposed-val" style="color:#f1f5f9;">{departman_adi} ({sirket_adi})</span>
                </div>
                <div class="exposed-row">
                    <span style="color:var(--muted);">İstemci & Tarayıcı:</span>
                    <span class="exposed-val" id="userBrowser" style="color:#38bdf8;">Tarayıcı bilgisi alınıyor...</span>
                </div>
                <div class="exposed-row">
                    <span style="color:var(--muted);">Simülasyon Durumu:</span>
                    <span class="exposed-val" style="color:#f87171;">Oltalama Bağlantısına Tıklandı</span>
                </div>
            </div>

            <div style="font-size:13px; font-weight:600; color:#f1f5f9; margin-bottom:10px;">Bir Sonraki Seferde Dikkat Edilecek 3 Kriter:</div>
            <div class="tip-item"><div><strong>1. Alan Adı Kontrolü:</strong> Tarayıcı adres çubuğundaki alan adının şirketinizin resmi web sitesiyle birebir eşleştiğini doğrulayın.</div></div>
            <div class="tip-item"><div><strong>2. Yapay Aciliyet:</strong> "Hemen tıklamazsanız hesabınız askıya alınacak" baskısı saldırganların en yaygın taktiğidir.</div></div>
            <div class="tip-item"><div><strong>3. Parola Girişi:</strong> Bilgi İşlem veya İK ekipleri e-posta/SMS bağlantısı üzerinden asla parola doğrulamanızı talep etmez.</div></div>

            <button class="btn-finish" id="btnFinish" onclick="egitimBitir()">Bilgilendirmeyi Okudum ve Anladım</button>
            <div id="finishSuccess" style="display:none; margin-top:14px; color:#10b981; font-size:13px; font-weight:600; text-align:center;">
                Katılımınız başarıyla sisteme işlendi. Teşekkür ederiz.
            </div>
        </div>

        <div class="card" id="screenHero" style="display:none; text-align:center;">
            <div style="display:inline-flex; align-items:center; justify-content:center; width:52px; height:52px; border-radius:50%; background:rgba(16,185,129,0.15); color:#10b981; margin-bottom:16px;">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
            </div>
            <div class="portal-badge" style="background:rgba(16,185,129,0.12); color:#10b981; border-color:rgba(16,185,129,0.3); margin-bottom:12px;">
                GÜVENLİK İHBARI ALINDI
            </div>
            <h2 style="font-size:18px; color:#fff; margin-bottom:12px;">Şüpheli E-Posta Bildirimi Kaydedildi</h2>
            <p style="font-size:13px; color:var(--muted); line-height:1.6; margin-bottom:20px;">
                Sayın <strong>{calisan_adi}</strong>,<br>
                Şüpheli bağlantıyı açıp parola girmek yerine doğrudan güvenlik birimine ihbarda bulundunuz. Doğru güvenlik refleksi gösterdiniz.
            </p>
            <div style="background:#090d16; border:1px solid #1f2937; border-radius:8px; padding:14px; margin-bottom:18px; color:#10b981; font-size:12px; line-height:1.6; text-align:left;">
                &bull; Kurumsal güvenlik profilinize pozitif puan (+20) işlendi.<br>
                &bull; Bildiriminiz CISO Güvenlik Operasyon Masasına iletildi.
            </div>
            <div style="font-size:12px; color:var(--muted);">Bu sekmeyi güvenle kapatabilirsiniz.</div>
        </div>

        <script>
            document.getElementById('userBrowser').innerText = navigator.userAgent.split(')')[0] + ')';

            function tuzagaDus() {{
                document.getElementById('screenTrap').style.display = 'none';
                document.getElementById('screenBreach').style.display = 'block';
            }}

            function supheliBildir() {{
                fetch('/bildir/{takip_kodu}', {{ method: 'POST' }})
                    .then(r => r.json())
                    .then(data => {{
                        document.getElementById('screenTrap').style.display = 'none';
                        document.getElementById('screenHero').style.display = 'block';
                    }})
                    .catch(err => {{
                        document.getElementById('screenTrap').style.display = 'none';
                        document.getElementById('screenHero').style.display = 'block';
                    }});
            }}

            function egitimBitir() {{
                const btn = document.getElementById('btnFinish');
                btn.innerHTML = '⏳ Kaydediliyor...';
                fetch('/egitim-tamamla/{takip_kodu}', {{ method: 'POST' }})
                    .then(r => r.json())
                    .then(d => {{
                        btn.style.display = 'none';
                        document.getElementById('finishSuccess').style.display = 'block';
                    }})
                    .catch(err => {{
                        btn.style.display = 'none';
                        document.getElementById('finishSuccess').style.display = 'block';
                    }});
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_icerik)


@app.post("/bildir/{takip_kodu}", tags=["Kampanyalar & Simülasyon"])
def supheli_bildir(takip_kodu: str, db: Session = Depends(get_db)):
    log = db.query(models.SimulasyonLog).filter(models.SimulasyonLog.takip_kodu == takip_kodu).first()
    if not log:
        raise HTTPException(status_code=404, detail="Simülasyon kaydı bulunamadı!")

    log.supheli_bildirildi_mi = True
    log.calisan.risk_puani = max(0, log.calisan.risk_puani - 15)
    db.commit()
    return {
        "durum": "basarili",
        "mesaj": f"Tebrikler {log.calisan.ad_soyad}! Şüpheli oltalama saldırısını başarıyla tespit edip bildirdiniz.",
        "yeni_risk_puani": log.calisan.risk_puani
    }


@app.post("/egitim-tamamla/{takip_kodu}", tags=["Kampanyalar & Simülasyon"])
def egitim_tamamla(takip_kodu: str, db: Session = Depends(get_db)):
    log = db.query(models.SimulasyonLog).filter(models.SimulasyonLog.takip_kodu == takip_kodu).first()
    if not log:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı!")

    log.egitim_tamamlandi_mi = True
    db.commit()
    return {
        "durum": "basarili",
        "mesaj": "Tebrikler! Güvenlik farkındalık eğitimi tamamlandı.",
        "calisan": log.calisan.ad_soyad
    }


@app.get("/kampanyalar/{kampanya_id}/ozet", response_model=schemas.KampanyaOzet, tags=["Kampanyalar & Simülasyon"])
def kampanya_ozeti(kampanya_id: int, db: Session = Depends(get_db)):
    kampanya = db.query(models.Kampanya).filter(models.Kampanya.id == kampanya_id).first()
    if not kampanya:
        raise HTTPException(status_code=404, detail="Kampanya bulunamadı!")

    toplam_hedef = len(kampanya.simulasyon_loglari)
    tiklayanlar = sum(1 for log in kampanya.simulasyon_loglari if log.tiklandi_mi)
    egitim_bitirenler = sum(1 for log in kampanya.simulasyon_loglari if log.egitim_tamamlandi_mi)

    oran = round((tiklayanlar / toplam_hedef) * 100, 1) if toplam_hedef > 0 else 0.0

    hedefler_detay = [
        schemas.SimulasyonLogDetay(
            id=log.id,
            calisan_adi=log.calisan.ad_soyad,
            calisan_email=log.calisan.email,
            departman=log.calisan.departman,
            takip_kodu=log.takip_kodu,
            simule_link=f"http://127.0.0.1:8000/tikla/{log.takip_kodu}",
            tiklandi_mi=log.tiklandi_mi,
            egitim_tamamlandi_mi=log.egitim_tamamlandi_mi
        ) for log in kampanya.simulasyon_loglari
    ]

    return schemas.KampanyaOzet(
        kampanya_id=kampanya.id,
        kampanya_adi=kampanya.ad,
        durum=kampanya.durum,
        toplam_hedef_calisan=toplam_hedef,
        tiklayan_sayisi=tiklayanlar,
        egitim_tamamlayan_sayisi=egitim_bitirenler,
        tiklanma_orani_yuzde=oran,
        hedefler=hedefler_detay
    )


@app.get("/qr-kod/{takip_kodu}", tags=["Kampanyalar & Simülasyon"])
def qr_kod_uret(takip_kodu: str):
    lan_ip = get_lan_ip()
    hedef_url = f"http://{lan_ip}:8000/tikla/{takip_kodu}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(hedef_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#090d16", back_color="#ffffff")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")


@app.get("/afis/{takip_kodu}", response_class=HTMLResponse, tags=["Kampanyalar & Simülasyon"])
def ofis_afisi_goruntule(takip_kodu: str, db: Session = Depends(get_db)):
    log = db.query(models.SimulasyonLog).filter(models.SimulasyonLog.takip_kodu == takip_kodu).first()
    if not log:
        raise HTTPException(status_code=404, detail="Simülasyon kaydı bulunamadı!")

    sirket_adi = log.calisan.sirket.ad if log.calisan and log.calisan.sirket else "Kurumsal Yönetim"
    calisan_adi = log.calisan.ad_soyad if log.calisan else "Personel"
    departman = log.calisan.departman if log.calisan else "Genel"
    lan_ip = get_lan_ip()
    qr_img_src = f"/qr-kod/{takip_kodu}"
    hedef_url = f"http://{lan_ip}:8000/tikla/{takip_kodu}"

    html = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{sirket_adi} - Güvenlik & Duyuru Afişi</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #090d16;
                color: #f8fafc;
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
            }}
            .poster {{
                background: #ffffff;
                color: #0f172a;
                width: 100%;
                max-width: 650px;
                border-radius: 20px;
                box-shadow: 0 25px 60px rgba(0,0,0,0.6);
                overflow: hidden;
                border: 2px solid #e2e8f0;
            }}
            .poster-header {{
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #ffffff;
                padding: 32px 24px;
                text-align: center;
                border-bottom: 4px solid #0284c7;
            }}
            .poster-body {{
                padding: 36px 30px;
                text-align: center;
            }}
            .qr-frame {{
                display: inline-block;
                padding: 16px;
                background: #f8fafc;
                border: 3px dashed #0284c7;
                border-radius: 20px;
                margin: 24px 0;
            }}
            .qr-frame img {{
                width: 240px;
                height: 240px;
                display: block;
                border-radius: 8px;
            }}
            .poster-footer {{
                background: #f1f5f9;
                padding: 18px;
                font-size: 12px;
                color: #64748b;
                text-align: center;
                border-top: 1px solid #e2e8f0;
            }}
            .btn-action {{
                background: #0284c7;
                color: #fff;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }}
            @media print {{
                body {{ background: #fff; padding: 0; }}
                .no-print {{ display: none !important; }}
                .poster {{ box-shadow: none; border: none; max-width: 100%; }}
            }}
        </style>
    </head>
    <body>
        <div style="max-width:650px; width:100%; text-align:center;">
            <div class="no-print" style="margin-bottom:20px; display:flex; justify-content:space-between; align-items:center;">
                <button onclick="window.close()" class="btn-action" style="background:#334155;">✕ Kapat</button>
                <button onclick="window.print()" class="btn-action">🖨️ Afişi Yazdır / PDF Kaydet</button>
            </div>
            <div class="poster">
                <div class="poster-header">
                    <div style="font-size:13px; letter-spacing:2px; font-weight:700; opacity:0.8; margin-bottom:6px;">{sirket_adi.upper()}</div>
                    <h1 style="font-size:22px; margin:0; font-weight:800; color:#38bdf8;">KURUMSAL GÜVENLİK VE DUYURU PANOSU</h1>
                    <div style="font-size:13px; opacity:0.85; margin-top:8px;">2026 Güz Dönemi Yemek Kartı & Servis Doğrulaması</div>
                </div>
                <div class="poster-body">
                    <p style="font-size:15px; line-height:1.6; color:#1e293b; margin-bottom:12px;">
                        Sayın <strong>{calisan_adi}</strong> ({departman} Departmanı);
                    </p>
                    <p style="font-size:14px; line-height:1.6; color:#475569; max-width:480px; margin:0 auto;">
                        Şirketimizin yeni dönem yan haklar ve personel servis güzergahı güncellemesi kapsamında kimlik doğrulaması yapılması zorunludur.
                    </p>
                    <div class="qr-frame">
                        <img src="{qr_img_src}" alt="Simüle QR Kod" />
                        <div style="font-size:12px; color:#0284c7; font-weight:700; margin-top:10px;">
                            📱 AKILLI TELEFON KAMERANIZLA OKUTUNUZ
                        </div>
                    </div>
                    <div style="font-size:12px; color:#64748b; background:#f8fafc; padding:10px 14px; border-radius:8px; display:inline-block; border:1px solid #e2e8f0;">
                        Doğrulama Adresi: <code style="color:#0284c7; font-weight:600;">{hedef_url}</code>
                    </div>
                </div>
                <div class="poster-footer">
                    🔒 Bu belge {sirket_adi} Bilgi Güvenliği Birimi ve PhishAware Oltalama Tatbikatı kontrolündedir.
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.post("/simulasyon/canli-mail-testi", tags=["Kampanyalar & Simülasyon"])
def canli_mail_testi(
    alici_email: str,
    sablon_id: int,
    smtp_host: str = None,
    smtp_port: int = None,
    smtp_user: str = None,
    smtp_pass: str = None,
    kaydet: bool = False,
    db: Session = Depends(get_db)
):
    if kaydet and smtp_user and smtp_pass:
        ayarlar = {
            "SMTP_HOST": (smtp_host or "smtp.gmail.com").strip(),
            "SMTP_PORT": str(smtp_port or 587).strip(),
            "SMTP_USER": smtp_user.strip(),
            "SMTP_PASSWORD": smtp_pass.strip()
        }
        env_guncelle(ayarlar)

    sablon = db.query(models.Sablon).filter(models.Sablon.id == sablon_id).first()
    if not sablon:
        raise HTTPException(status_code=404, detail="Şablon bulunamadı!")

    ozel_token = str(uuid.uuid4())[:16]
    lan_ip = get_lan_ip()
    takip_linki = f"http://{lan_ip}:8000/tikla/{ozel_token}"

    sonuc = gercek_smtp_mail_gonder(
        alici_email=alici_email,
        alici_adi="Sayın Test Kullanıcısı",
        takip_linki=takip_linki,
        konu=sablon.konu,
        icerik_html=sablon.icerik_html,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_pass=smtp_pass
    )
    return sonuc


@app.get("/dashboard", response_class=HTMLResponse, tags=["Genel"])
def yonetim_paneli(db: Session = Depends(get_db)):
    toplam_calisan = db.query(models.Calisan).count()
    toplam_tiklama = db.query(models.SimulasyonLog).filter(models.SimulasyonLog.tiklandi_mi == True).count()
    toplam_egitim = db.query(models.SimulasyonLog).filter(models.SimulasyonLog.egitim_tamamlandi_mi == True).count()
    toplam_gonderi = db.query(models.SimulasyonLog).count()
    genel_oran = round((toplam_tiklama / toplam_gonderi) * 100, 1) if toplam_gonderi > 0 else 0.0

    calisanlar = db.query(models.Calisan).all()
    dep_dict = {}
    for c in calisanlar:
        d = c.departman
        if d not in dep_dict:
            dep_dict[d] = {"departman": d, "toplam": 0, "tiklayan": 0}
        dep_dict[d]["toplam"] += 1
        if any(log.tiklandi_mi for log in c.simulasyon_loglari):
            dep_dict[d]["tiklayan"] += 1

    dep_list = []
    for d, val in dep_dict.items():
        oran = round((val["tiklayan"] / val["toplam"]) * 100, 1) if val["toplam"] > 0 else 0.0
        dep_list.append({
            "departman": d,
            "toplam": val["toplam"],
            "tiklayan": val["tiklayan"],
            "oran": oran
        })
    dep_list.sort(key=lambda x: x["oran"], reverse=True)

    lan_ip = get_lan_ip()

    ai_danisman = risk_analizi_yorumu(dep_list)

    sirketler = db.query(models.Sirket).all()
    sablonlar = db.query(models.Sablon).all()
    varsayilan_sirket_id = sirketler[0].id if sirketler else 1
    varsayilan_sirket_adi = sirketler[0].ad if sirketler else "Kurum"

    sirket_options_html = "".join([f'<option value="{s.id}">{s.ad} ({s.sektor})</option>' for s in sirketler])
    channel_icons = {"email": "📧", "whatsapp": "💬", "sms": "📱", "qr": "🔳"}
    sablon_options_html = "".join([
        f'<option value="{sb.id}">{channel_icons.get(getattr(sb, "kanal", "email"), "📧")} {"[YZ] " if sb.yapay_zeka_ile_mi else ""}{sb.baslik}</option>' 
        for sb in sablonlar
    ])

    son_kampanya = db.query(models.Kampanya).order_by(models.Kampanya.id.desc()).first()
    son_kampanya_adi = son_kampanya.ad if son_kampanya else "Henüz Kampanya Yok"
    son_hedefler = son_kampanya.simulasyon_loglari if son_kampanya else []

    env_yukle()
    env_smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    env_smtp_port = os.getenv("SMTP_PORT", "587")
    env_smtp_user = os.getenv("SMTP_USER", "")

    ICON_SHIELD = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
    ICON_CHART = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'
    ICON_CPU = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>'
    ICON_SPARKLES = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3z"/></svg>'
    ICON_SEND = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>'
    ICON_USERS = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
    ICON_MAIL = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>'
    ICON_DOWNLOAD = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'
    ICON_PRINTER = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>'

    html = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PhishAware - Kurumsal Güvenlik Yönetim & Denetim Portalı</title>
        <style>
            :root {{
                --bg: #0b0f19;
                --surface: #111827;
                --surface-hover: #172236;
                --surface-card: #0f1624;
                --border: #1f2937;
                --border-subtle: #162032;
                --text: #f9fafb;
                --muted: #94a3b8;
                --primary: #2563eb;
                --primary-hover: #1d4ed8;
                --primary-text: #ffffff;
                --btn-sec-bg: #1f2937;
                --btn-sec-border: #374151;
                --btn-sec-text: #e5e7eb;
                --emerald: #10b981;
                --rose: #ef4444;
                --amber: #f59e0b;
                --cyan: #06b6d4;
                --radius: 8px;
                --radius-btn: 6px;
                --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            }}

            /* Varyant 2: Linear Minimal (Monokrom ve Geliştirici Odaklı) */
            body.theme-linear {{
                --bg: #09090b;
                --surface: #121215;
                --surface-hover: #18181c;
                --surface-card: #121215;
                --border: #27272a;
                --border-subtle: #1e1e24;
                --text: #ededed;
                --muted: #a1a1aa;
                --primary: #fafafa;
                --primary-hover: #e4e4e7;
                --primary-text: #09090b;
                --btn-sec-bg: #18181b;
                --btn-sec-border: #27272a;
                --btn-sec-text: #d4d4d8;
                --radius: 6px;
                --radius-btn: 4px;
            }}
            body.theme-linear .stat-value {{ font-family: var(--font-mono); letter-spacing: -0.04em; }}
            body.theme-linear .stat-card:hover, body.theme-linear .section-card:hover {{ transform: none !important; border-color: #3f3f46 !important; }}

            /* Varyant 3: SOC Operations Console (Datadog / Falcon Stili) */
            body.theme-soc {{
                --bg: #0d1117;
                --surface: #161b22;
                --surface-hover: #1c2128;
                --surface-card: #13171f;
                --border: #30363d;
                --border-subtle: #21262d;
                --text: #c9d1d9;
                --muted: #8b949e;
                --primary: #238636;
                --primary-hover: #2ea043;
                --primary-text: #ffffff;
                --btn-sec-bg: #21262d;
                --btn-sec-border: #30363d;
                --btn-sec-text: #c9d1d9;
                --radius: 4px;
                --radius-btn: 4px;
            }}
            body.theme-soc .section-title {{ font-family: var(--font-mono); font-size: 13px; text-transform: uppercase; letter-spacing: 0.06em; }}
            body.theme-soc table th {{ font-family: var(--font-mono); font-size: 11px; text-transform: uppercase; }}

            /* Varyant 4: Orijinal Neon Siber */
            body.theme-classic {{
                --bg: #090d16;
                --surface: #121b2d;
                --surface-hover: #17233a;
                --surface-card: #121b2d;
                --border: rgba(255, 255, 255, 0.08);
                --border-subtle: rgba(255, 255, 255, 0.04);
                --text: #f8fafc;
                --muted: #94a3b8;
                --primary: #06b6d4;
                --primary-hover: #0891b2;
                --primary-text: #000000;
                --btn-sec-bg: rgba(255, 255, 255, 0.08);
                --btn-sec-border: rgba(255, 255, 255, 0.15);
                --btn-sec-text: #f1f5f9;
                --radius: 12px;
                --radius-btn: 8px;
            }}
            body.theme-classic .logo-badge {{
                background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%) !important;
                box-shadow: 0 0 26px rgba(6, 182, 212, 0.55) !important;
                border: none !important;
                font-size: 26px !important;
                width: 50px !important;
                height: 50px !important;
            }}

            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background: var(--bg);
                color: var(--text);
                min-height: 100vh;
                padding: 26px 22px 44px;
                font-size: 14.5px;
                line-height: 1.55;
                transition: background 0.2s ease, color 0.2s ease;
            }}
            .container {{ max-width: 1340px; margin: 0 auto; }}

            /* Header */
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 18px;
                padding-bottom: 24px;
                border-bottom: 1px solid var(--border);
                margin-bottom: 30px;
            }}
            .header-brand {{
                display: flex;
                align-items: center;
                gap: 16px;
            }}
            .logo-badge {{
                width: 48px;
                height: 48px;
                border-radius: var(--radius);
                background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
                border: 1px solid var(--border);
                color: var(--text);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 25px;
                box-shadow: 0 0 22px rgba(6, 182, 212, 0.45);
                flex-shrink: 0;
            }}
            .header-title-wrap {{
                display: flex;
                flex-direction: column;
                gap: 3px;
            }}
            .header-title-row {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .header-title {{
                font-size: 22px;
                font-weight: 700;
                letter-spacing: -0.02em;
                color: var(--text);
            }}
            .header-tag {{
                font-size: 12px;
                font-weight: 600;
                background: var(--surface);
                border: 1px solid var(--border);
                color: var(--muted);
                padding: 3px 9px;
                border-radius: var(--radius-btn);
                letter-spacing: 0.02em;
            }}
            .header-subtitle {{
                font-size: 13.5px;
                color: var(--muted);
            }}

            .header-actions {{
                display: flex;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
                margin-left: auto;
                justify-content: flex-end;
            }}

            .btn-head {{
                display: inline-flex;
                align-items: center;
                gap: 7px;
                padding: 8px 15px;
                border-radius: var(--radius-btn);
                font-size: 13px;
                font-weight: 600;
                cursor: pointer;
                text-decoration: none;
                white-space: nowrap;
                transition: background 0.15s, border-color 0.15s;
            }}
            .btn-head-sec {{
                background: var(--btn-sec-bg);
                color: var(--btn-sec-text);
                border: 1px solid var(--btn-sec-border);
            }}
            .btn-head-sec:hover {{
                background: var(--surface-hover);
                color: var(--text);
            }}
            .btn-head-pri {{
                background: var(--primary);
                color: var(--primary-text);
                border: 1px solid transparent;
            }}
            .btn-head-pri:hover {{
                background: var(--primary-hover);
            }}

            .badge-live {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: rgba(16, 185, 129, 0.12);
                color: var(--emerald);
                border: 1px solid rgba(16, 185, 129, 0.35);
                padding: 7px 14px;
                border-radius: 9999px;
                font-size: 12.5px;
                font-weight: 600;
            }}
            .dot {{
                width: 9px;
                height: 9px;
                background: #10b981;
                border-radius: 50%;
                display: inline-block;
                box-shadow: 0 0 10px #10b981;
                animation: liveBlink 1.4s ease-in-out infinite;
            }}
            @keyframes liveBlink {{
                0%, 100% {{
                    opacity: 1;
                    transform: scale(1.15);
                    box-shadow: 0 0 12px #10b981, 0 0 4px #10b981;
                }}
                50% {{
                    opacity: 0.25;
                    transform: scale(0.8);
                    box-shadow: 0 0 2px rgba(16, 185, 129, 0.2);
                }}
            }}

            /* Stats Grid */
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 18px;
                margin-bottom: 26px;
            }}
            .stat-card {{
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: var(--radius);
                padding: 22px 24px;
                transition: border-color 0.2s;
            }}
            .stat-card:hover {{ border-color: rgba(255, 255, 255, 0.18); }}
            .stat-title {{ font-size: 13px; color: var(--muted); font-weight: 500; margin-bottom: 7px; text-transform: uppercase; letter-spacing: 0.04em; }}
            .stat-value {{ font-size: 32px; font-weight: 700; letter-spacing: -0.03em; color: var(--text); }}
            .stat-sub {{ font-size: 12px; color: var(--muted); margin-top: 7px; }}

            /* 2 Columns Layout */
            .grid-2 {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 22px;
                margin-bottom: 26px;
            }}
            @media (max-width: 900px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

            .section-card {{
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: var(--radius);
                padding: 24px 26px;
            }}
            .section-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 18px;
            }}
            .section-title {{
                font-size: 16px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 9px;
                color: var(--text);
            }}

            /* Progress Bars */
            .progress-item {{ margin-bottom: 15px; }}
            .progress-label {{
                display: flex;
                justify-content: space-between;
                font-size: 13px;
                margin-bottom: 6px;
                font-weight: 500;
            }}
            .bar-bg {{
                background: rgba(255, 255, 255, 0.06);
                height: 9px;
                border-radius: 9999px;
                overflow: hidden;
            }}
            .bar-fill {{
                height: 100%;
                border-radius: 9999px;
                transition: width 0.6s ease;
            }}

            /* AI CISO Box */
            .ai-advisor-box {{
                background: var(--surface-card);
                border: 1px solid var(--border);
                border-radius: var(--radius);
                padding: 20px 22px;
            }}
            .ai-summary {{ font-size: 14px; line-height: 1.65; color: var(--text); margin-bottom: 15px; }}
            .ai-steps {{ list-style: none; display: flex; flex-direction: column; gap: 9px; }}
            .ai-step-item {{
                display: flex;
                align-items: flex-start;
                gap: 11px;
                font-size: 13px;
                color: var(--text);
                background: var(--surface);
                border: 1px solid var(--border);
                padding: 11px 14px;
                border-radius: var(--radius-btn);
            }}

            /* Forms & Inputs */
            .form-group {{ margin-bottom: 16px; }}
            label {{ display: block; font-size: 13px; color: var(--muted); margin-bottom: 6px; font-weight: 500; }}
            select, input {{
                width: 100%; background: var(--surface-card); border: 1px solid var(--border);
                border-radius: var(--radius-btn); padding: 10px 13px; color: var(--text); font-size: 14px; outline: none;
                transition: border-color 0.15s;
            }}
            select:focus, input:focus {{ border-color: var(--primary); }}

            .btn-action-main {{
                width: 100%; background: var(--primary);
                color: var(--primary-text); border: none; padding: 12px 14px; border-radius: var(--radius-btn);
                font-size: 14px; font-weight: 600; cursor: pointer; transition: opacity 0.15s;
                display: flex; align-items: center; justify-content: center; gap: 8px;
            }}
            .btn-action-main:hover {{ opacity: 0.9; }}

            /* Tables */
            table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }}
            th {{ padding: 12px 14px; color: var(--muted); border-bottom: 1px solid var(--border); font-weight: 500; font-size: 13px; }}
            td {{ padding: 13px 14px; border-bottom: 1px solid var(--border-subtle); }}
            .badge-status {{ padding: 5px 9px; border-radius: var(--radius-btn); font-size: 12px; font-weight: 600; }}
            .status-caught {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }}
            .status-safe {{ background: var(--surface); color: var(--muted); border: 1px solid var(--border); }}
            .status-completed {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
            .btn-link {{
                background: var(--surface); color: var(--text); border: 1px solid var(--border);
                padding: 6px 12px; border-radius: var(--radius-btn); font-size: 12px; text-decoration: none; font-weight: 500;
                transition: background 0.15s;
            }}
            .btn-link:hover {{ background: var(--surface-hover); }}

            /* PRINT CSS */
            @media print {{
                body {{ background: #ffffff !important; color: #0f172a !important; padding: 10px !important; }}
                .header-actions, .theme-selector-wrap, .grid-actions, .btn-link, .badge-live, button, select, input, label, #aiSonuc, #kampanyaSonuc {{ display: none !important; }}
                .section-card, .stat-card, .ai-advisor-box {{ background: #ffffff !important; border: 1px solid #cbd5e1 !important; color: #0f172a !important; box-shadow: none !important; }}
                .stat-title, .progress-label, .ai-summary {{ color: #334155 !important; }}
                .ai-step-item {{ background: #f8fafc !important; color: #0f172a !important; border: 1px solid #cbd5e1 !important; }}
                table {{ border: 1px solid #cbd5e1 !important; }}
                th, td {{ border-bottom: 1px solid #cbd5e1 !important; color: #0f172a !important; }}
            }}
        </style>
    </head>
    <body>
        <script>
            (function() {{
                document.body.className = 'theme-classic';
                localStorage.setItem('phishaware_theme', 'classic');
            }})();
        </script>
        <div class="container">
            <div class="header">
                <div class="header-brand">
                    <div class="logo-badge">🛡️</div>
                    <div class="header-title-wrap">
                        <div class="header-title-row">
                            <h1 class="header-title">PhishAware</h1>
                            <span class="header-tag">Kurumsal Güvenlik Portalı</span>
                        </div>
                        <p class="header-subtitle">
                            Kurum: <strong>{varsayilan_sirket_adi}</strong> &bull; Çok Kanallı Oltalama Tatbikatı &bull; Departman Risk Analitiği
                        </p>
                    </div>
                </div>
                <div class="header-actions">
                    <a href="/rapor/csv/{varsayilan_sirket_id}" class="btn-head btn-head-pri" title="Excel uyumlu UTF-8 BOM CSV Denetim Raporu İndir">
                        {ICON_DOWNLOAD} <span>CSV Denetim Raporu</span>
                    </a>
                    <button onclick="window.print()" class="btn-head btn-head-sec" title="Yönetim Kurulu için A4 Formatında Yazdır / PDF Kaydet">
                        {ICON_PRINTER} <span>Raporu Yazdır (PDF)</span>
                    </button>
                    <span class="badge-live"><span class="dot"></span> Aktif</span>
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-title">Hedef Personel</div>
                    <div class="stat-value">{toplam_calisan}</div>
                    <div class="stat-sub">Kayıtlı Kurumsal Kadro</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Bağlantıyı Açanlar</div>
                    <div class="stat-value" style="color:var(--rose);">{toplam_tiklama}</div>
                    <div class="stat-sub" style="color:var(--rose);">Zaafiyet Gösteren</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Eğitimi Tamamlayanlar</div>
                    <div class="stat-value" style="color:var(--emerald);">{toplam_egitim}</div>
                    <div class="stat-sub" style="color:var(--emerald);">Farkındalık Bildirimini Okuyan</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Genel Risk Oranı</div>
                    <div class="stat-value" style="color:var(--cyan);">%{genel_oran}</div>
                    <div class="stat-sub">Kurumsal Zaafiyet Skoru</div>
                </div>
            </div>

            <div class="grid-2">
                <div class="section-card">
                    <div class="section-header">
                        <div class="section-title">{ICON_CHART} <span>Departman Zaafiyet Dağılımı</span></div>
                        <span style="font-size:12px; color:var(--muted);">Tıklama Oranları</span>
                    </div>
                    <p style="font-size:13px; color:var(--muted); margin-bottom:18px;">
                        Departman bazlı simülasyon tıklama ve zaafiyet oranları:
                    </p>
    """

    for dep in dep_list:
        bar_color = "var(--rose)" if dep["oran"] >= 50 else ("var(--amber)" if dep["oran"] > 0 else "var(--emerald)")
        html += f"""
                    <div class="progress-item">
                        <div class="progress-label">
                            <span>{dep["departman"]} ({dep["tiklayan"]}/{dep["toplam"]} Kişi)</span>
                            <span style="color:{bar_color}; font-weight:600;">%{dep["oran"]} Risk</span>
                        </div>
                        <div class="bar-bg">
                            <div class="bar-fill" style="width: {dep["oran"]}%; background: {bar_color};"></div>
                        </div>
                    </div>
        """

    html += f"""
                </div>

                <div class="section-card">
                    <div class="section-header">
                        <div class="section-title">{ICON_CPU} <span>CISO Güvenlik Analitiği & Eylem Planı</span></div>
                        <span style="font-size:11px; color:var(--muted); background:var(--surface); border:1px solid var(--border); padding:2px 8px; border-radius:4px;">Gemini Güvenlik Analizi</span>
                    </div>

                    <div class="ai-advisor-box">
                        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
                            <span style="font-size:12px; color:var(--muted);">Kritik Risk Grubu:</span>
                            <span style="background:rgba(239,68,68,0.15); color:#fca5a5; font-size:12px; padding:3px 10px; border-radius:6px; font-weight:600;">
                                {ai_danisman.get("en_riskli_departman", "Belirsiz")}
                            </span>
                        </div>
                        <div class="ai-summary">
                            {ai_danisman.get("genel_degerlendirme", "Veriler analiz edildi.")}
                        </div>
                        <div style="font-size:12px; font-weight:600; color:var(--text); margin-bottom:8px;">Önerilen Eylem Adımları:</div>
                        <ul class="ai-steps">
    """
    for oneri in ai_danisman.get("aksiyon_onerileri", []):
        html += f"""<li class="ai-step-item"><span style="color:var(--primary); font-weight:700;">&bull;</span><div>{oneri}</div></li>"""

    html += f"""
                        </ul>
                    </div>
                </div>
            </div>

            <div class="section-card" style="margin-bottom: 24px;">
                <div class="section-header" style="flex-wrap:wrap; gap:10px;">
                    <div class="section-title">
                        {ICON_SEND} <span>Yeni Simülasyon Tatbikatı Başlat (Otonom AI Destekli)</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="background:rgba(6,182,212,0.15); color:var(--cyan); border:1px solid rgba(6,182,212,0.3); padding:3px 10px; border-radius:9999px; font-size:11px; font-weight:600;">
                            ✨ Arka Plan AI Motoru Aktif
                        </span>
                        <span style="font-size:12px; color:var(--muted);">Hedefe Özel Otomatik Senaryo Eşleme</span>
                    </div>
                </div>

                <p style="font-size:13px; color:var(--muted); margin-bottom:18px;">
                    Yapay zeka oltalama motoru seçilen hedef kitleye göre arka planda otonom çalışır. <strong>Tüm Şirket</strong> seçildiğinde IT personeline altyapı/yama, İK personeline bordro/izin, Muhasebeye fatura yemleri üretilir; tek departman seçildiğinde ise yalnızca o departmana özel oltalama senaryosu hazırlanır.
                </p>

                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:16px; margin-bottom:16px;">
                    <div class="form-group" style="margin-bottom:0;">
                        <label>Tatbikat Adı</label>
                        <input type="text" id="kampanyaBaslik" value="2026 Güz Çok Kanallı Siber Güvenlik Tatbikatı" placeholder="Örn: 2026 Q4 Habersiz Tatbikat" />
                    </div>
                    <div class="form-group" style="margin-bottom:0;">
                        <label>Hedef Kurum</label>
                        <select id="kampanyaSirket">
                            {sirket_options_html}
                        </select>
                    </div>
                    <div class="form-group" style="margin-bottom:0;">
                        <label>🎯 Hedef Departman (Kapsam)</label>
                        <select id="hedefDepartman" style="border-color:rgba(6,182,212,0.4); background:var(--surface);">
                            <option value="hepsi" selected>🌐 Tüm Şirket (Hepsi - Departmanlara Özel AI Senaryoları)</option>
                            <option value="Bilgi İşlem (IT)">💻 Bilgi İşlem (IT) - Kritik Güvenlik Yaması & SSH</option>
                            <option value="İnsan Kaynakları (İK)">👥 İnsan Kaynakları (İK) - 2026 Yan Haklar & Bordro</option>
                            <option value="Muhasebe ve Finans">💰 Muhasebe ve Finans - E-Arşiv Fatura & IBAN</option>
                            <option value="Satış ve Pazarlama">📈 Satış ve Pazarlama - İhale & Q4 Prim Tablosu</option>
                            <option value="Operasyon ve Tedarik">🚚 Operasyon ve Tedarik - Sevkiyat İrsaliyesi & Yakıt Kartı</option>
                            <option value="Hukuk ve Uyum">⚖️ Hukuk ve Uyum - KVKK & Noter İhtarnamesi</option>
                            <option value="Üst Yönetim">🏛️ Üst Yönetim - Yönetim Kurulu Denetim Raporu</option>
                        </select>
                    </div>
                    <div class="form-group" style="margin-bottom:0;">
                        <label>📡 Saldırı Vektörü (İletim Kanalı)</label>
                        <select id="kampanyaKanal">
                            <option value="email" selected>📧 Kurumsal E-Posta (Simüle / Canlı Relay)</option>
                            <option value="whatsapp">💬 Kurumsal WhatsApp Mesajı (Smishing)</option>
                            <option value="sms">📱 Kurumsal SMS / Mobil İleti (Smishing)</option>
                            <option value="qr">🔳 Ofis / Pano QR Kod Afişi (Quishing)</option>
                        </select>
                    </div>
                </div>

                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-top:20px; padding-top:16px; border-top:1px solid var(--border);">
                    <div style="font-size:12px; color:var(--muted); display:flex; align-items:center; gap:8px;">
                        <span style="color:var(--cyan); font-size:15px;">🛡️</span>
                        <span>Seçilen kanaldan maskelenmiş kurumsal kimlikle eş zamanlı otomatik dağıtım yapılır.</span>
                    </div>
                    <button class="btn-action-main" id="btnKampanya" onclick="yeniKampanyaBaslat()" style="width:auto; padding:12px 28px;">
                        {ICON_SEND} <span>Tatbikatı Başlat & Otonom Dağıt</span>
                    </button>
                </div>
                <div id="kampanyaSonuc" style="display:none; margin-top:15px; background:var(--surface-card); border:1px solid var(--border); border-radius:8px; padding:14px; font-size:13px; color:var(--text);" id="kampanyaSonucMetin"></div>
            </div>

            <div class="section-card">
                <div class="section-header">
                    <div class="section-title">{ICON_USERS} <span>Aktif Kampanya Hedef Takip Masası</span></div>
                    <span style="font-size:12px; color:var(--muted);">{son_kampanya_adi}</span>
                </div>
                <div style="overflow-x:auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Personel</th>
                                <th>Departman</th>
                                <th>Atanan Oltalama Senaryosu</th>
                                <th>Kanal</th>
                                <th>Kümülatif Risk</th>
                                <th>Simülasyon Durumu</th>
                                <th>İşlemler & Test</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    for log in son_hedefler:
        if log.supheli_bildirildi_mi:
            durum_badge = '<span class="badge-status" style="background:rgba(234,179,8,0.15); color:#facc15; border:1px solid rgba(234,179,8,0.3);">Siber Kahraman (İhbar Bildirildi)</span>'
        elif log.egitim_tamamlandi_mi:
            durum_badge = '<span class="badge-status status-completed">Eğitim Tamamlandı</span>'
        elif log.tiklandi_mi:
            durum_badge = '<span class="badge-status status-caught">Bağlantı Açıldı</span>'
        else:
            durum_badge = '<span class="badge-status status-safe">İletildi (Bekliyor)</span>'

        hedef_kanal = getattr(log.kampanya.sablon, "kanal", "email") if (log.kampanya and log.kampanya.sablon) else "email"
        kanal_badge = {
            "email": '<span style="color:#38bdf8; font-weight:600;">E-Posta</span>',
            "whatsapp": '<span style="color:#22c55e; font-weight:600;">WhatsApp</span>',
            "sms": '<span style="color:#fbbf24; font-weight:600;">SMS</span>',
            "qr": '<span style="color:#c084fc; font-weight:600;">QR Kod</span>'
        }.get(hedef_kanal, '<span style="color:#38bdf8;">E-Posta</span>')

        hedef_senaryo = log.senaryo_adi or (log.kampanya.sablon.baslik if (log.kampanya and log.kampanya.sablon) else "Genel Oltalama")

        test_url = f"/tikla/{log.takip_kodu}"
        lan_url = f"http://{lan_ip}:8000/tikla/{log.takip_kodu}"
        calisan_adi_temiz = log.calisan.ad_soyad.replace("'", "\\'")

        if hedef_kanal == "whatsapp":
            aksiyonlar = f"""
                <div style="display:flex; gap:6px; align-items:center;">
                    <a href="{test_url}" target="_blank" class="btn-link" title="Web sekmesinde doğrudan aç">🔗 Aç ↗</a>
                    <button onclick="whatsappTestAc('{calisan_adi_temiz}', '{lan_url}')" class="btn-link" style="background:rgba(34,197,94,0.18); color:#22c55e; border-color:rgba(34,197,94,0.35); cursor:pointer;">💬 WhatsApp Gönder</button>
                </div>
            """
        elif hedef_kanal == "sms":
            aksiyonlar = f"""
                <div style="display:flex; gap:6px; align-items:center;">
                    <a href="{test_url}" target="_blank" class="btn-link" title="Web sekmesinde doğrudan aç">🔗 Aç ↗</a>
                    <button onclick="smsTestAc('{calisan_adi_temiz}', '{lan_url}')" class="btn-link" style="background:rgba(245,158,11,0.18); color:#f59e0b; border-color:rgba(245,158,11,0.35); cursor:pointer;">📱 SMS Testi</button>
                </div>
            """
        elif hedef_kanal == "qr":
            aksiyonlar = f"""
                <div style="display:flex; gap:6px; align-items:center;">
                    <a href="{test_url}" target="_blank" class="btn-link" title="Web sekmesinde doğrudan aç">🔗 Aç ↗</a>
                    <a href="/afis/{log.takip_kodu}" target="_blank" class="btn-link" style="background:rgba(192,132,252,0.18); color:#c084fc; border-color:rgba(192,132,252,0.35);">🔳 Afiş / QR Tara ↗</a>
                </div>
            """
        else:
            aksiyonlar = f"""
                <div style="display:flex; gap:6px; align-items:center;">
                    <a href="{test_url}" target="_blank" class="btn-link">📧 Simüle E-Posta Aç ↗</a>
                </div>
            """

        html += f"""
                            <tr>
                                <td><strong>{log.calisan.ad_soyad}</strong></td>
                                <td style="color:var(--muted);">{log.calisan.departman}</td>
                                <td><span style="font-size:12px; color:var(--text); background:var(--surface); border:1px solid var(--border); padding:3px 8px; border-radius:4px; font-weight:500;">✨ {hedef_senaryo}</span></td>
                                <td>{kanal_badge}</td>
                                <td><span style="color:#f59e0b; font-weight:700;">{log.calisan.risk_puani} Puan</span></td>
                                <td>{durum_badge}</td>
                                <td>{aksiyonlar}</td>
                            </tr>
        """
    html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            function setTheme(name) {
                document.body.className = 'theme-' + name;
                localStorage.setItem('phishaware_theme', name);
                document.querySelectorAll('.theme-btn').forEach(function(b) {
                    b.classList.remove('active');
                });
                const activeBtn = document.getElementById('btnTheme-' + name);
                if (activeBtn) activeBtn.classList.add('active');
            }
            (function() {
                var cur = localStorage.getItem('phishaware_theme') || 'classic';
                var btn = document.getElementById('btnTheme-' + cur);
                if (btn) btn.classList.add('active');
            })();

            function yeniKampanyaBaslat() {
                const baslik = document.getElementById('kampanyaBaslik').value;
                const sirketId = parseInt(document.getElementById('kampanyaSirket').value);
                const hedefDep = document.getElementById('hedefDepartman').value;
                const kanal = document.getElementById('kampanyaKanal').value;
                const btn = document.getElementById('btnKampanya');
                const sonucDiv = document.getElementById('kampanyaSonuc');

                if (!baslik || baslik.trim() === '') {
                    alert('Lütfen tatbikat adı girin!');
                    return;
                }

                if (isNaN(sirketId)) {
                    alert('Lütfen geçerli bir şirket seçin!');
                    return;
                }

                btn.innerHTML = '⏳ Yapay Zeka Hazırlıyor & Dağıtılıyor...';
                btn.style.opacity = '0.7';

                fetch('/kampanyalar/baslat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        ad: baslik.trim(), 
                        sirket_id: sirketId, 
                        hedef_departman: hedefDep, 
                        kanal: kanal, 
                        otomatik_ai: true 
                    })
                })
                .then(r => {
                    if (!r.ok) return r.json().then(e => { throw new Error(e.detail || 'Hata oluştu'); });
                    return r.json();
                })
                .then(data => {
                    btn.innerHTML = '🚀 Tatbikatı Başlat & Otonom Dağıt';
                    btn.style.opacity = '1';
                    if (data.dagitim_raporu && data.dagitim_raporu.loglar) {
                        akisliDagitimGoster(data);
                    } else {
                        sonucDiv.style.display = 'block';
                        sonucDiv.style.borderColor = 'rgba(6, 182, 212, 0.4)';
                        sonucDiv.style.color = '#38bdf8';
                        sonucDiv.innerText = '✅ "' + data.kampanya_adi + '" başarıyla başlatıldı! ' + data.toplam_hedef_calisan + ' personel için departmana özel oltalama paketleri üretildi. Sayfa güncelleniyor...';
                        setTimeout(() => { location.reload(); }, 1200);
                    }
                })
                .catch(err => {
                    btn.innerHTML = '🚀 Tatbikatı Başlat & Otonom Dağıt';
                    btn.style.opacity = '1';
                    sonucDiv.style.display = 'block';
                    sonucDiv.style.borderColor = 'rgba(239, 68, 68, 0.4)';
                    sonucDiv.style.color = '#f87171';
                    let hataMesaji = err.message || 'Bilinmeyen hata';
                    if (hataMesaji.includes('fetch') || hataMesaji.includes('Failed')) {
                        hataMesaji = 'Sunucuya bağlanılamadı (Failed to fetch). Sunucu kapanmış görünüyor. Lütfen PhishAware klasöründeki baslat.bat dosyasını çalıştırın!';
                    }
                    sonucDiv.innerText = '❌ Hata: ' + hataMesaji;
                    setTimeout(() => { alert('Hata: ' + hataMesaji); }, 50);
                });
            }

            let currentWaText = '';
            let currentSmsText = '';

            function whatsappTestAc(calisanAdi, link) {
                currentWaText = 'TrendLojistik A.Ş. Kurumsal Onay Masası\\n\\nSayın ' + calisanAdi + ', şirketiniz adına bekleyen acil onay talebiniz bulunmaktadır. İncelemek ve onaylamak için lütfen bağlantıya tıklayınız:\\n' + link;
                document.getElementById('waPreviewText').innerText = currentWaText;
                document.getElementById('modalWhatsApp').style.display = 'flex';
            }

            function waMesajGonder() {
                let phone = document.getElementById('waPhoneInput').value.replace(/[^0-9]/g, '');
                let text = encodeURIComponent(currentWaText);
                let url = phone ? 'https://wa.me/' + phone + '?text=' + text : 'https://wa.me/?text=' + text;
                window.open(url, '_blank');
            }

            function smsTestAc(calisanAdi, link) {
                currentSmsText = 'Sayin ' + calisanAdi + ', kurumsal hesabiniza erisim talebi tespit edildi. Onaylamiyorsaniz derhal iptal edin: ' + link;
                document.getElementById('smsPreviewBody').innerText = currentSmsText;
                document.getElementById('modalSMS').style.display = 'flex';
            }

            function telefondaSmsAc() {
                window.open('sms:?body=' + encodeURIComponent(currentSmsText), '_blank');
            }

            function smsMetniKopyala() {
                navigator.clipboard.writeText(currentSmsText);
                document.getElementById('smsKopyalandi').style.display = 'block';
                setTimeout(() => { document.getElementById('smsKopyalandi').style.display = 'none'; }, 2000);
            }

            function terminalLogYaz(metin, renk='#34d399') {
                const term = document.getElementById('terminalBody');
                const p = document.createElement('div');
                p.style.color = renk;
                p.innerHTML = metin;
                term.appendChild(p);
                term.scrollTop = term.scrollHeight;
            }

            function terminaliKapatVeYenile() {
                location.reload();
            }

            function akisliDagitimGoster(data) {
                const modal = document.getElementById('modalTerminal');
                const term = document.getElementById('terminalBody');
                term.innerHTML = '';
                document.getElementById('terminalSpinner').innerHTML = '● OTOMATİK DAĞITILIYOR...';
                document.getElementById('terminalSpinner').style.color = '#06b6d4';
                document.getElementById('btnTerminalKapat').style.display = 'none';
                modal.style.display = 'flex';

                terminalLogYaz('<span style="color:#06b6d4;">[SİSTEM]</span> PhishAware Çok Kanallı Otonom Dağıtım Motoru Başlatıldı...');
                terminalLogYaz('<span style="color:#06b6d4;">[TATBİKAT]</span> "' + data.kampanya_adi + '"');

                const rapor = data.dagitim_raporu || {};
                const hedefKapsami = (data.hedef_departman === 'hepsi' || !data.hedef_departman) ? 'Tüm Şirket (Departmanlara Özel AI Senaryoları)' : data.hedef_departman;
                terminalLogYaz('<span style="color:#38bdf8;">[HEDEF KAPSAMI]</span> ' + hedefKapsami + ' (' + data.toplam_hedef_calisan + ' Personel)');
                terminalLogYaz('<span style="color:#f59e0b;">[SALDIRI VEKTÖRÜ]</span> ' + (rapor.kanal || 'email').toUpperCase() + ' | Protokol: ' + (rapor.protokol || 'Kurumsal Gateway'));
                terminalLogYaz('<span style="color:#f59e0b;">[MASKE GÖNDERİCİ]</span> ' + (rapor.maskelenmis_gonderici || 'TrendLojistik Güvenlik Masası'));
                terminalLogYaz('--------------------------------------------------------------------------------', '#475569');

                const loglar = rapor.loglar || [];
                let index = 0;

                function sonrakiHedef() {
                    if (index < loglar.length) {
                        const l = loglar[index];
                        const aiEtiketi = l.sablon_adi ? ' ➔ <span style="color:#facc15;">[AI: ' + l.sablon_adi + ']</span>' : '';
                        terminalLogYaz('<span style="color:#38bdf8;">[' + l.zaman + ']</span> 📤 [' + String(l.sira).padStart(2, '0') + '/' + loglar.length + '] ' + l.calisan_adi + ' (' + l.departman + ')' + aiEtiketi + ' ➔ <strong style="color:#fff;">' + l.hedef_adresi + '</strong> | <span style="color:#10b981;">' + l.durum + '</span>');
                        index++;
                        setTimeout(sonrakiHedef, 60);
                    } else {
                        terminalLogYaz('--------------------------------------------------------------------------------', '#475569');
                        terminalLogYaz('<span style="color:#10b981; font-weight:bold;">[TAMAMLANDI]</span> ' + loglar.length + ' personelin tamamına departmanlarına özel oltalama tatbikatı başarıyla iletildi! (Başarı: %100)');
                        document.getElementById('terminalSpinner').innerHTML = '<span style="color:#10b981;">✔ DAĞITIM TAMAMLANDI</span>';
                        document.getElementById('terminalStatusText').innerText = 'Tüm çalışanlara hedefe özel habersiz simülasyon paketleri iletildi.';
                        document.getElementById('btnTerminalKapat').style.display = 'block';
                    }
                }
                setTimeout(sonrakiHedef, 200);
            }

            function toggleSmtpAyar() {
                const el = document.getElementById('smtpAyarGovde');
                const icon = document.getElementById('smtpHtIkon');
                if (!el) return;
                if (el.style.display === 'none' || !el.style.display) {
                    el.style.display = 'block';
                    if (icon) icon.innerText = '▲';
                } else {
                    el.style.display = 'none';
                    if (icon) icon.innerText = '▼';
                }
            }

            function smtpHazirSecildi() {
                const preset = document.getElementById('smtpHazirPreset').value;
                const hst = document.getElementById('smtpHst');
                const prt = document.getElementById('smtpPrt');
                if (preset === 'gmail') {
                    hst.value = 'smtp.gmail.com';
                    prt.value = '587';
                } else if (preset === 'msku') {
                    hst.value = 'posta.mu.edu.tr';
                    prt.value = '587';
                } else if (preset === 'outlook') {
                    hst.value = 'smtp.office365.com';
                    prt.value = '587';
                } else if (preset === 'yandex') {
                    hst.value = 'smtp.yandex.com';
                    prt.value = '465';
                }
            }

            function canliMailTestiGonder() {
                const email = document.getElementById('testAliciEmail').value.trim();
                const sablonEl = document.getElementById('testSablonSec');
                const sablonId = sablonEl ? parseInt(sablonEl.value) : NaN;
                const btn = document.getElementById('btnMailTestGonder');
                const sonucDiv = document.getElementById('testMailSonuc');

                if (!email || !email.includes('@')) {
                    alert('Lütfen geçerli bir e-posta adresi girin!');
                    return;
                }
                if (!sablonId || isNaN(sablonId)) {
                    alert('Lütfen geçerli bir oltalama şablonu seçin!');
                    return;
                }

                btn.innerHTML = '⏳ Gönderiliyor...';
                btn.style.opacity = '0.7';
                btn.disabled = true;

                let url = '/simulasyon/canli-mail-testi?alici_email=' + encodeURIComponent(email) + '&sablon_id=' + sablonId;
                const hst = document.getElementById('smtpHst') ? document.getElementById('smtpHst').value.trim() : '';
                const prt = document.getElementById('smtpPrt') ? document.getElementById('smtpPrt').value.trim() : '';
                const usr = document.getElementById('smtpUsr') ? document.getElementById('smtpUsr').value.trim() : '';
                const pwd = document.getElementById('smtpPwd') ? document.getElementById('smtpPwd').value.trim() : '';
                const kaydet = document.getElementById('smtpKaydetEnv') ? document.getElementById('smtpKaydetEnv').checked : false;

                if (hst) url += '&smtp_host=' + encodeURIComponent(hst);
                if (prt) url += '&smtp_port=' + encodeURIComponent(prt);
                if (usr) url += '&smtp_user=' + encodeURIComponent(usr);
                if (pwd) url += '&smtp_pass=' + encodeURIComponent(pwd);
                if (kaydet) url += '&kaydet=true';

                fetch(url, {
                    method: 'POST'
                })
                .then(async r => {
                    const data = await r.json();
                    if (!r.ok) {
                        const errMsg = data.detail ? (typeof data.detail === 'object' ? JSON.stringify(data.detail) : data.detail) : 'Gönderim başarısız';
                        throw new Error(errMsg);
                    }
                    return data;
                })
                .then(res => {
                    btn.innerHTML = '🚀 Canlı Test Maili Gönder';
                    btn.style.opacity = '1';
                    btn.disabled = false;
                    sonucDiv.style.display = 'block';
                    if (res.durum === 'basarili') {
                        sonucDiv.style.color = '#10b981';
                        sonucDiv.style.background = 'rgba(16,185,129,0.12)';
                        sonucDiv.style.border = '1px solid rgba(16,185,129,0.3)';
                        sonucDiv.innerHTML = '✔️ <strong>Başarılı (Gerçek İletim):</strong> ' + (res.mesaj || 'E-posta başarıyla iletildi.');
                    } else if (res.durum === 'simule') {
                        sonucDiv.style.color = '#38bdf8';
                        sonucDiv.style.background = 'rgba(6,182,212,0.12)';
                        sonucDiv.style.border = '1px solid rgba(6,182,212,0.3)';
                        sonucDiv.innerHTML = 'ℹ️ <strong>Simüle İletim:</strong> ' + (res.mesaj || 'Test simülasyon kuyruğuna alındı.') + 
                            '<br><br><span style="color:#94a3b8;">Gerçekten e-posta kutunuza mail düşmesi için yukarıdaki <strong>⚙️ Canlı SMTP Gönderici Ayarları</strong> menüsünü açarak e-posta ve şifrenizi giriniz.</span>';
                    } else {
                        sonucDiv.style.color = '#f87171';
                        sonucDiv.style.background = 'rgba(239,68,68,0.12)';
                        sonucDiv.style.border = '1px solid rgba(239,68,68,0.3)';
                        sonucDiv.innerHTML = '⚠️ <strong>Hata / Uyarı:</strong> ' + (res.mesaj || 'İşlem tamamlanamadı.');
                    }
                })
                .catch(err => {
                    btn.innerHTML = '🚀 Canlı Test Maili Gönder';
                    btn.style.opacity = '1';
                    btn.disabled = false;
                    sonucDiv.style.display = 'block';
                    sonucDiv.style.color = '#f87171';
                    sonucDiv.style.background = 'rgba(239,68,68,0.12)';
                    sonucDiv.style.border = '1px solid rgba(239,68,68,0.3)';
                    sonucDiv.innerHTML = '❌ <strong>Hata:</strong> ' + err.message;
                });
            }
        </script>

        <div id="modalWhatsApp" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); backdrop-filter:blur(8px); z-index:9999; align-items:center; justify-content:center;">
            <div style="background:#121b2d; border:1px solid rgba(34,197,94,0.4); border-radius:18px; max-width:520px; width:92%; padding:26px; box-shadow:0 25px 60px rgba(0,0,0,0.8);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:24px;">💬</span>
                        <h3 style="font-size:17px; font-weight:700; color:#fff;">Canlı WhatsApp Test Gönderimi</h3>
                    </div>
                    <button onclick="document.getElementById('modalWhatsApp').style.display='none'" style="background:none; border:none; color:var(--muted); font-size:22px; cursor:pointer;">✕</button>
                </div>
                <p style="font-size:13px; color:var(--muted); line-height:1.5; margin-bottom:14px;">
                    Resmi WhatsApp Web / Mobil protokolüyle doğrudan kendi telefonunuza veya hedef numaraya gerçek bir simülasyon mesajı yollayabilirsiniz.
                </p>
                <div style="background:#090d16; border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:14px; margin-bottom:16px; font-size:13px;">
                    <div style="color:#22c55e; font-weight:700; margin-bottom:6px;">WhatsApp Mesaj Önizlemesi:</div>
                    <div id="waPreviewText" style="color:#e2e8f0; line-height:1.5; white-space:pre-wrap;"></div>
                </div>
                <div class="form-group" style="margin-bottom:16px;">
                    <label>Hedef Telefon Numarası (Örn: 905xxxxxxxxx)</label>
                    <input type="text" id="waPhoneInput" placeholder="905xxxxxxxxx (Boş bırakırsanız WhatsApp'ta kişi seçebilirsiniz)" />
                    <div style="font-size:11px; color:#94a3b8; margin-top:4px;">* Kendi numaranızı yazıp doğrudan kendinize test mesajı yollayabilirsiniz!</div>
                </div>
                <div style="display:flex; gap:10px;">
                    <button onclick="document.getElementById('modalWhatsApp').style.display='none'" style="flex:1; background:rgba(255,255,255,0.08); color:#fff; border:none; padding:12px; border-radius:10px; cursor:pointer; font-weight:600;">İptal</button>
                    <button onclick="waMesajGonder()" style="flex:2; background:linear-gradient(135deg, #16a34a 0%, #22c55e 100%); color:#fff; border:none; padding:12px; border-radius:10px; cursor:pointer; font-weight:700; display:flex; align-items:center; justify-content:center; gap:8px;">
                        <span>🚀</span> WhatsApp'ta Aç & Gönder
                    </button>
                </div>
            </div>
        </div>

        <div id="modalSMS" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); backdrop-filter:blur(8px); z-index:9999; align-items:center; justify-content:center;">
            <div style="background:#121b2d; border:1px solid rgba(245,158,11,0.4); border-radius:18px; max-width:480px; width:92%; padding:26px; box-shadow:0 25px 60px rgba(0,0,0,0.8);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:24px;">📱</span>
                        <h3 style="font-size:17px; font-weight:700; color:#fff;">SMS (Smishing) Test Simülatörü</h3>
                    </div>
                    <button onclick="document.getElementById('modalSMS').style.display='none'" style="background:none; border:none; color:var(--muted); font-size:22px; cursor:pointer;">✕</button>
                </div>

                <div style="background:#090d16; border:1px solid rgba(255,255,255,0.12); border-radius:14px; padding:16px; margin-bottom:18px; box-shadow:0 8px 25px rgba(0,0,0,0.5);">
                    <div style="display:flex; justify-content:space-between; font-size:11px; color:#94a3b8; margin-bottom:8px;">
                        <span>💬 MESAJLAR • B002-TRENDLOJISTIK</span>
                        <span>Şimdi</span>
                    </div>
                    <div id="smsPreviewBody" style="font-size:13px; color:#f8fafc; line-height:1.5;"></div>
                </div>

                <div style="display:flex; gap:10px;">
                    <button onclick="telefondaSmsAc()" style="flex:2; background:linear-gradient(135deg, #d97706 0%, #f59e0b 100%); color:#fff; border:none; padding:12px; border-radius:10px; cursor:pointer; font-weight:700;">
                        📲 Telefonda SMS Aç (sms:)
                    </button>
                    <button onclick="smsMetniKopyala()" style="flex:1; background:rgba(255,255,255,0.08); color:#fff; border:1px solid rgba(255,255,255,0.15); padding:12px; border-radius:10px; cursor:pointer; font-weight:600;">
                        📋 Kopyala
                    </button>
                </div>
                <div id="smsKopyalandi" style="display:none; color:#10b981; font-size:12px; margin-top:10px; text-align:center;">✔️ SMS metni panoya kopyalandı!</div>
            </div>
        </div>

        <div id="modalTerminal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); backdrop-filter:blur(10px); z-index:10000; align-items:center; justify-content:center;">
            <div style="background:#050811; border:1px solid #10b981; border-radius:18px; max-width:720px; width:94%; padding:26px; box-shadow:0 0 50px rgba(16,185,129,0.25); font-family:Consolas, Monaco, monospace;">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(16,185,129,0.3); padding-bottom:14px; margin-bottom:16px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:20px;">⚡</span>
                        <h3 style="font-size:16px; font-weight:700; color:#10b981; letter-spacing:1px;">PHISHAWARE OTONOM DAĞITIM KONSOLU</h3>
                    </div>
                    <span id="terminalSpinner" style="color:#06b6d4; font-size:13px; animation:blink 1s infinite;">● ÇALIŞIYOR</span>
                </div>
                <div id="terminalBody" style="background:#020408; border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:16px; height:320px; overflow-y:auto; color:#34d399; font-size:12px; line-height:1.7;">
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:16px;">
                    <span id="terminalStatusText" style="font-size:12px; color:var(--muted);">Hedeflere habersiz paketler iletiliyor...</span>
                    <button id="btnTerminalKapat" onclick="terminaliKapatVeYenile()" style="display:none; background:#10b981; color:#000; border:none; padding:10px 20px; border-radius:8px; font-weight:700; cursor:pointer;">
                        📊 Canlı Takip Masasına Git ↗
                    </button>
                </div>
            </div>
        </div>

        <div id="modalEpostaTest" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); backdrop-filter:blur(8px); z-index:9999; align-items:center; justify-content:center;">
            <div style="background:#121b2d; border:1px solid rgba(56,189,248,0.4); border-radius:18px; max-width:540px; width:92%; max-height:90vh; overflow-y:auto; padding:24px; box-shadow:0 25px 60px rgba(0,0,0,0.8);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:24px;">✉️</span>
                        <h3 style="font-size:17px; font-weight:700; color:#fff;">Canlı E-Posta Test Gönderimi</h3>
                    </div>
                    <button onclick="document.getElementById('modalEpostaTest').style.display='none'" style="background:none; border:none; color:var(--muted); font-size:22px; cursor:pointer;">✕</button>
                </div>
                <p style="font-size:13px; color:var(--muted); line-height:1.5; margin-bottom:14px;">
                    Hedef e-posta adresinizi girerek canlı oltalama şablonunun e-posta kutunuza nasıl düştüğünü test edebilirsiniz.
                </p>
                <div class="form-group" style="margin-bottom:12px;">
                    <label>Hedef Test E-Posta Adresiniz</label>
                    <input type="email" id="testAliciEmail" placeholder="ornek@sirket.com veya test@alanadi.com" value="" />
                </div>
                <div class="form-group" style="margin-bottom:14px;">
                    <label>Kullanılacak Oltalama Şablonu</label>
                    <select id="testSablonSec">
                        {sablon_options_html}
                    </select>
                </div>

                <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(56,189,248,0.25); border-radius:12px; padding:12px 14px; margin-bottom:16px;">
                    <div onclick="toggleSmtpAyar()" style="display:flex; justify-content:space-between; align-items:center; cursor:pointer; user-select:none;">
                        <span style="font-size:13px; font-weight:600; color:#38bdf8; display:flex; align-items:center; gap:6px;">
                            ⚙️ Canlı SMTP Gönderici Ayarları
                            <small style="color:var(--muted); font-weight:normal;">(Gerçek iletim için)</small>
                        </span>
                        <span id="smtpHtIkon" style="color:#38bdf8; font-size:12px;">▼</span>
                    </div>
                    <div id="smtpAyarGovde" style="display:none; margin-top:12px; padding-top:12px; border-top:1px dashed rgba(255,255,255,0.12);">
                        <div class="form-group" style="margin-bottom:10px;">
                            <label style="font-size:11px; color:var(--muted);">Hazır SMTP Şablonu Seç</label>
                            <select id="smtpHazirPreset" onchange="smtpHazirSecildi()" style="width:100%; padding:8px 12px; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.15); border-radius:8px; color:#fff; font-size:12px;">
                                <option value="gmail" selected>Google Gmail (smtp.gmail.com:587 TLS)</option>
                                <option value="msku">MSKÜ Posta (posta.mu.edu.tr:587)</option>
                                <option value="outlook">Microsoft 365 / Outlook (smtp.office365.com:587)</option>
                                <option value="yandex">Yandex Mail (smtp.yandex.com:465 SSL)</option>
                                <option value="custom">Özel SMTP Sunucusu</option>
                            </select>
                        </div>
                        <div style="display:grid; grid-template-columns:2fr 1fr; gap:8px; margin-bottom:10px;">
                            <div>
                                <label style="font-size:11px; color:var(--muted);">SMTP Sunucu (Host)</label>
                                <input type="text" id="smtpHst" value="{env_smtp_host}" placeholder="smtp.gmail.com" style="width:100%; padding:8px 10px; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.15); border-radius:8px; color:#fff; font-size:12px;" />
                            </div>
                            <div>
                                <label style="font-size:11px; color:var(--muted);">Port</label>
                                <input type="number" id="smtpPrt" value="{env_smtp_port}" placeholder="587" style="width:100%; padding:8px 10px; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.15); border-radius:8px; color:#fff; font-size:12px;" />
                            </div>
                        </div>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:10px;">
                            <div>
                                <label style="font-size:11px; color:var(--muted);">Gönderen E-Posta / Kullanıcı</label>
                                <input type="text" id="smtpUsr" value="{env_smtp_user}" placeholder="ornek@gmail.com" style="width:100%; padding:8px 10px; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.15); border-radius:8px; color:#fff; font-size:12px;" />
                            </div>
                            <div>
                                <label style="font-size:11px; color:var(--muted);">Parola / Uygulama Şifresi</label>
                                <input type="password" id="smtpPwd" placeholder="16 haneli şifre" style="width:100%; padding:8px 10px; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.15); border-radius:8px; color:#fff; font-size:12px;" />
                            </div>
                        </div>
                        <div style="font-size:11px; color:#94a3b8; background:rgba(2,132,199,0.1); border-left:3px solid #0284c7; padding:8px 10px; border-radius:6px; margin-bottom:10px; line-height:1.45;">
                            💡 <strong>Gmail İpucu:</strong> Google standart hesap şifrenizi güvenlik sebebiyle SMTP için kabul etmez. Google Hesabım &gt; Güvenlik &gt; <strong>2 Adımlı Doğrulama</strong> &gt; en alttaki <strong>Uygulama Şifreleri</strong> (App Passwords) kısmından 16 karakterlik bir şifre üretip buraya giriniz.
                        </div>
                        <label style="display:flex; align-items:center; gap:8px; font-size:11px; color:var(--muted); cursor:pointer;">
                            <input type="checkbox" id="smtpKaydetEnv" checked style="accent-color:#0284c7;" />
                            Bu SMTP bilgilerini .env dosyasına kaydet (Gelecek testlerde hatırla)
                        </label>
                    </div>
                </div>

                <div style="display:flex; gap:10px;">
                    <button onclick="document.getElementById('modalEpostaTest').style.display='none'" style="flex:1; background:rgba(255,255,255,0.08); color:#fff; border:none; padding:12px; border-radius:10px; cursor:pointer; font-weight:600;">Kapat</button>
                    <button id="btnMailTestGonder" onclick="canliMailTestiGonder()" style="flex:2; background:linear-gradient(135deg, #0284c7 0%, #06b6d4 100%); color:#fff; border:none; padding:12px; border-radius:10px; cursor:pointer; font-weight:700;">
                        🚀 Canlı Test Maili Gönder
                    </button>
                </div>
                <div id="testMailSonuc" style="display:none; font-size:12px; margin-top:14px; background:#090d16; padding:12px; border-radius:10px; line-height:1.4;"></div>
            </div>
        </div>
    </body>
    </html>
    """
    html = html.replace("{sablon_options_html}", sablon_options_html)
    html = html.replace("{env_smtp_host}", env_smtp_host)
    html = html.replace("{env_smtp_port}", env_smtp_port)
    html = html.replace("{env_smtp_user}", env_smtp_user)
    return HTMLResponse(content=html)


@app.get("/varyantlar", response_class=HTMLResponse, tags=["Genel"])
def varyantlar_showroom():
    html = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhishAware - No-AI-Slop Tasarım Showroom'u</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #080c14;
            color: #f1f5f9;
            min-height: 100vh;
            padding: 40px 20px 60px;
        }
        .container { max-width: 1280px; margin: 0 auto; }
        .hero {
            text-align: center;
            margin-bottom: 40px;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(37, 99, 235, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(37, 99, 235, 0.3);
            font-size: 11px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 12px;
        }
        .hero-title {
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 8px;
        }
        .hero-desc {
            font-size: 14px;
            color: #94a3b8;
            max-width: 700px;
            margin: 0 auto;
            line-height: 1.6;
        }
        .top-nav {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
        }
        .btn-dash {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #1e293b;
            color: #f8fafc;
            border: 1px solid #334155;
            padding: 9px 18px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.15s;
        }
        .btn-dash:hover {
            background: #334155;
        }

        /* 4 Cards Grid */
        .variants-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 22px;
            margin-bottom: 40px;
        }
        .variant-card {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 14px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
            position: relative;
        }
        .variant-card:hover {
            transform: translateY(-4px);
            border-color: #3b82f6;
            box-shadow: 0 12px 30px rgba(0,0,0,0.6);
        }
        .card-header {
            margin-bottom: 16px;
        }
        .card-tag {
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 8px;
            letter-spacing: 0.04em;
        }
        .card-title {
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 6px;
        }
        .card-desc {
            font-size: 12px;
            color: #94a3b8;
            line-height: 1.5;
            margin-bottom: 18px;
        }

        /* Mini Preview Box */
        .mini-preview {
            background: #020617;
            border: 1px solid #1e293b;
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 18px;
            font-size: 11px;
        }
        .preview-stat {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 2px;
        }

        /* Color Swatches */
        .swatches {
            display: flex;
            gap: 6px;
            align-items: center;
            margin-bottom: 16px;
        }
        .swatch {
            width: 22px;
            height: 22px;
            border-radius: 50%;
            border: 1px solid rgba(255,255,255,0.15);
        }

        /* Features List */
        .features-list {
            list-style: none;
            font-size: 12px;
            color: #cbd5e1;
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .features-list li::before {
            content: "✓ ";
            color: #10b981;
            font-weight: bold;
        }

        .btn-select {
            width: 100%;
            padding: 11px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            border: none;
            transition: all 0.15s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        /* Matrix Table */
        .matrix-card {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 14px;
            padding: 26px;
        }
        .matrix-title {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 16px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }
        th {
            padding: 10px 14px;
            color: #94a3b8;
            border-bottom: 1px solid #1e293b;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
        }
        td {
            padding: 12px 14px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            color: #e2e8f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <div class="hero-badge">Peter Yang • No-AI-Slop Tasarım Dönüşümü</div>
            <h1 class="hero-title">PhishAware Arayüz Tasarım Showroom'u</h1>
            <p class="hero-desc">
                Yapay zeka klişelerinden (aşırı neon mor parıltılar, başlıklarda emoji yığınları, panik yaratan abartılı metinler)
                arındırılmış 3 yeni kurumsal tasarım geliştirdik. Dilediğiniz varyantı seçip canlı yönetim panelinde test edebilirsiniz.
            </p>
        </div>

        <div class="top-nav">
            <a href="/dashboard" class="btn-dash">➔ Yönetim Paneline (Dashboard) Dön</a>
        </div>

        <div class="variants-grid">
            <div class="variant-card" style="border-top: 3px solid #2563eb;">
                <div>
                    <div class="card-header">
                        <span class="card-tag" style="background:rgba(37,99,235,0.15); color:#60a5fa;">VARYANT 1 (ÖNERİLEN)</span>
                        <div class="card-title">Enterprise B2B</div>
                        <div class="card-desc">Cloudflare Zero Trust ve GitHub Security tarzı sakin, güvenilir ve otoriter kurumsal SaaS estetiği.</div>
                    </div>

                    <div class="mini-preview" style="background:#0b0f19; border-color:#1f2937;">
                        <div style="color:#94a3b8; font-size:10px; text-transform:uppercase; margin-bottom:4px;">HEDEF PERSONEL</div>
                        <div class="preview-stat" style="color:#f9fafb;">22 Kişi</div>
                        <div style="height:6px; background:#1f2937; border-radius:3px; margin:8px 0; overflow:hidden;">
                            <div style="width:18%; height:100%; background:#2563eb;"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; color:#94a3b8; font-size:10px;">
                            <span>Zaafiyet: %18.2</span>
                            <span style="color:#10b981;">● Güvenli</span>
                        </div>
                    </div>

                    <div style="font-size:11px; color:#94a3b8; margin-bottom:6px;">Renk Paleti:</div>
                    <div class="swatches">
                        <div class="swatch" style="background:#0b0f19;" title="Arka Plan #0b0f19"></div>
                        <div class="swatch" style="background:#111827;" title="Yüzey #111827"></div>
                        <div class="swatch" style="background:#1f2937;" title="Kenarlık #1f2937"></div>
                        <div class="swatch" style="background:#2563eb;" title="Aksan #2563eb"></div>
                    </div>

                    <ul class="features-list">
                        <li>Başlıklarda emoji yerine ince SVG ikonlar</li>
                        <li>Sakin arduvaz zemin, göz yormayan kontrast</li>
                        <li>C-Level ve Jüri sunumu için ideal ağırlık</li>
                        <li>Net 1px kenarlıklar, abartısız gölgeler</li>
                    </ul>
                </div>
                <button class="btn-select" style="background:#2563eb; color:#fff;" onclick="chooseTheme('enterprise')">
                    Bu Varyantı Seç ve Uygula ➔
                </button>
            </div>

            <div class="variant-card" style="border-top: 3px solid #fafafa;">
                <div>
                    <div class="card-header">
                        <span class="card-tag" style="background:#18181b; color:#fafafa; border:1px solid #27272a;">VARYANT 2</span>
                        <div class="card-title">Linear Minimal</div>
                        <div class="card-desc">Raycast, Linear ve modern mühendislik araçları tarzı monokrom, keskin kenarlı ve yüksek veri yoğunluklu.</div>
                    </div>

                    <div class="mini-preview" style="background:#09090b; border-color:#27272a; border-radius:4px;">
                        <div style="color:#71717a; font-size:10px; font-family:monospace; margin-bottom:4px;">TOTAL_TARGETS</div>
                        <div class="preview-stat" style="color:#ededed; font-family:monospace;">22</div>
                        <div style="height:4px; background:#27272a; border-radius:2px; margin:8px 0; overflow:hidden;">
                            <div style="width:18%; height:100%; background:#fafafa;"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; color:#71717a; font-size:10px; font-family:monospace;">
                            <span>VULN_RATE: 18.2%</span>
                            <span style="color:#22c55e;">STATUS: OK</span>
                        </div>
                    </div>

                    <div style="font-size:11px; color:#94a3b8; margin-bottom:6px;">Renk Paleti:</div>
                    <div class="swatches">
                        <div class="swatch" style="background:#09090b;" title="Arka Plan #09090b"></div>
                        <div class="swatch" style="background:#121215;" title="Yüzey #121215"></div>
                        <div class="swatch" style="background:#27272a;" title="Kenarlık #27272a"></div>
                        <div class="swatch" style="background:#fafafa;" title="Aksan #fafafa"></div>
                    </div>

                    <ul class="features-list">
                        <li>Saf monokrom (siyah/çinko/beyaz)</li>
                        <li>Monospace veri metrikleri (JetBrains Mono)</li>
                        <li>Sıfır gradyan, sıfır renkli parıltı</li>
                        <li>Keskin 4px kenarlar, yüksek veri yoğunluğu</li>
                    </ul>
                </div>
                <button class="btn-select" style="background:#fafafa; color:#09090b;" onclick="chooseTheme('linear')">
                    Bu Varyantı Seç ve Uygula ➔
                </button>
            </div>

            <div class="variant-card" style="border-top: 3px solid #238636;">
                <div>
                    <div class="card-header">
                        <span class="card-tag" style="background:rgba(35,134,54,0.15); color:#3fb950;">VARYANT 3</span>
                        <div class="card-title">SOC Console</div>
                        <div class="card-desc">Datadog ve CrowdStrike Falcon tarzı siber güvenlik operasyon merkezi ve olay müdahale kokpiti.</div>
                    </div>

                    <div class="mini-preview" style="background:#0d1117; border-color:#30363d; border-radius:4px;">
                        <div style="color:#8b949e; font-size:10px; font-family:monospace; margin-bottom:4px;">[AUDIT_TARGETS]</div>
                        <div class="preview-stat" style="color:#c9d1d9; font-family:monospace;">22 HOSTS</div>
                        <div style="height:6px; background:#21262d; border-radius:2px; margin:8px 0; overflow:hidden;">
                            <div style="width:18%; height:100%; background:#238636;"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; color:#8b949e; font-size:10px; font-family:monospace;">
                            <span>POSTURE: MONITORED</span>
                            <span style="color:#58a6ff;">SEV-2</span>
                        </div>
                    </div>

                    <div style="font-size:11px; color:#94a3b8; margin-bottom:6px;">Renk Paleti:</div>
                    <div class="swatches">
                        <div class="swatch" style="background:#0d1117;" title="Arka Plan #0d1117"></div>
                        <div class="swatch" style="background:#161b22;" title="Yüzey #161b22"></div>
                        <div class="swatch" style="background:#30363d;" title="Kenarlık #30363d"></div>
                        <div class="swatch" style="background:#238636;" title="Aksan #238636"></div>
                    </div>

                    <ul class="features-list">
                        <li>Güvenlik Operasyon Merkezi (SOC) hissi</li>
                        <li>Terminal etiketleri ve telemetri şeritleri</li>
                        <li>Operasyon yeşili ve telemetri mavisi</li>
                        <li>Savunma ve denetim odaklı sıkı hiyerarşi</li>
                    </ul>
                </div>
                <button class="btn-select" style="background:#238636; color:#fff;" onclick="chooseTheme('soc')">
                    Bu Varyantı Seç ve Uygula ➔
                </button>
            </div>

            <div class="variant-card" style="border-top: 3px solid #8b5cf6;">
                <div>
                    <div class="card-header">
                        <span class="card-tag" style="background:rgba(139,92,246,0.15); color:#a78bfa;">VARYANT 4 (KLASİK)</span>
                        <div class="card-title">Orijinal Neon</div>
                        <div class="card-desc">İlk geliştirdiğimiz canlı camgöbeği ve mor gradyanlı, cam efektli siber güvenlik teması.</div>
                    </div>

                    <div class="mini-preview" style="background:#090d16; border-color:rgba(139,92,246,0.3); border-radius:10px;">
                        <div style="color:#94a3b8; font-size:10px; margin-bottom:4px;">🛡️ TOPLAM ÇALIŞAN</div>
                        <div class="preview-stat" style="color:#06b6d4;">22 Kişi</div>
                        <div style="height:8px; background:rgba(255,255,255,0.06); border-radius:4px; margin:8px 0; overflow:hidden;">
                            <div style="width:18%; height:100%; background:linear-gradient(90deg, #10b981, #06b6d4);"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; color:#a78bfa; font-size:10px;">
                            <span>Zaafiyet: %18.2</span>
                            <span style="color:#10b981;">🚀 Aktif</span>
                        </div>
                    </div>

                    <div style="font-size:11px; color:#94a3b8; margin-bottom:6px;">Renk Paleti:</div>
                    <div class="swatches">
                        <div class="swatch" style="background:#090d16;" title="Arka Plan #090d16"></div>
                        <div class="swatch" style="background:#121b2d;" title="Yüzey #121b2d"></div>
                        <div class="swatch" style="background:#8b5cf6;" title="Mor #8b5cf6"></div>
                        <div class="swatch" style="background:#06b6d4;" title="Camgöbeği #06b6d4"></div>
                    </div>

                    <ul class="features-list">
                        <li>Camgöbeği ve mor renkli gradyanlar</li>
                        <li>Koyu camgöbeği cam efekti (glassmorphism)</li>
                        <li>Canlı ve parıltılı hacker teması</li>
                        <li>Karşılaştırma için erişilebilir durumda</li>
                    </ul>
                </div>
                <button class="btn-select" style="background:linear-gradient(135deg, #0284c7, #06b6d4); color:#fff;" onclick="chooseTheme('classic')">
                    Bu Varyantı Seç ve Uygula ➔
                </button>
            </div>
        </div>

        <div class="matrix-card">
            <div class="matrix-title">📊 Tasarım Varyantları Karşılaştırma Matrisi</div>
            <div style="overflow-x:auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Özellik</th>
                            <th>Enterprise B2B</th>
                            <th>Linear Minimal</th>
                            <th>SOC Console</th>
                            <th>Orijinal Neon</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Tasarım Esinlenmesi</strong></td>
                            <td>Cloudflare Zero Trust, GitHub Security</td>
                            <td>Linear, Raycast, Vercel</td>
                            <td>Datadog, CrowdStrike Falcon</td>
                            <td>Klasik Siber Güvenlik Teması</td>
                        </tr>
                        <tr>
                            <td><strong>İkonografi</strong></td>
                            <td>İnce SVG Vektör İkonlar</td>
                            <td>İnce SVG Vektör İkonlar</td>
                            <td>Monospace Terminal İkonları</td>
                            <td>Renkli Emojiler</td>
                        </tr>
                        <tr>
                            <td><strong>Tipografi</strong></td>
                            <td>Clean System Sans (Inter / SF)</td>
                            <td>Monospace Numerals (Geist / Mono)</td>
                            <td>Consolas / Telemetri Sans</td>
                            <td>Standart Sans-Serif</td>
                        </tr>
                        <tr>
                            <td><strong>Kenar & Yüzey</strong></td>
                            <td>8px Yumuşak Köşeler, 1px Arduvaz</td>
                            <td>4px Keskin Köşeler, Düz Çinko</td>
                            <td>4px Terminal Panelleri</td>
                            <td>14px Yuvarlatılmış Cam Efektleri</td>
                        </tr>
                        <tr>
                            <td><strong>En Uygun Olduğu Alan</strong></td>
                            <td>C-Level Yönetici & Jüri Sunumları</td>
                            <td>Mühendislik & Geliştirici Odaklı</td>
                            <td>Siber Olay Müdahale & Teknik Ekipler</td>
                            <td>Görsel Efekt & Tanıtım</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function chooseTheme(name) {
            localStorage.setItem('phishaware_theme', name);
            window.location.href = '/dashboard';
        }
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html)
