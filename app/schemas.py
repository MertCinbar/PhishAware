from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class SirketOlustur(BaseModel):
    ad: str = Field(default="TrendLojistik A.Ş.", description="Şirketin adı")
    sektor: str = Field(default="E-Ticaret ve Lojistik", description="Faaliyet sektörü")

    model_config = {
        "json_schema_extra": {
            "example": {
                "ad": "TrendLojistik A.Ş.",
                "sektor": "E-Ticaret ve Lojistik"
            }
        }
    }

class SirketCevap(SirketOlustur):
    id: int
    olusturuldugu_tarih: datetime

    class Config:
        from_attributes = True


class CalisanOlustur(BaseModel):
    sirket_id: int = Field(default=1, description="Çalışanın bağlı olduğu şirket ID'si")
    ad_soyad: str = Field(default="Zeynep Kaya", description="Çalışanın adı soyadı")
    email: str = Field(default="zeynep@trendlojistik.com", description="E-posta adresi")
    departman: str = Field(default="Pazarlama", description="Çalıştığı departman")

    model_config = {
        "json_schema_extra": {
            "example": {
                "sirket_id": 1,
                "ad_soyad": "Zeynep Kaya",
                "email": "zeynep@trendlojistik.com",
                "departman": "Pazarlama"
            }
        }
    }

class CalisanCevap(CalisanOlustur):
    id: int
    risk_puani: int

    class Config:
        from_attributes = True


class SablonOlustur(BaseModel):
    baslik: str = Field(default="Acil Kargo İade Bildirimi", description="Şablon başlığı")
    konu: str = Field(default="[ÖNEMLİ] Gönderiniz teslim edilemedi!", description="E-posta konusu")
    gonderen_adi: str = Field(default="Hızlı Kargo Müşteri Hizmetleri", description="Görünen gönderici adı")
    icerik_html: str = Field(default="<p>Paketiniz şubede bekliyor. Güncellemek için: <a href='{{LINK}}'>Tıklayın</a></p>", description="E-posta HTML içeriği")
    yapay_zeka_ile_mi: bool = False
    kanal: str = Field(default="email", description="Oltalama iletim kanalı: email, sms, whatsapp, qr")

    model_config = {
        "json_schema_extra": {
            "example": {
                "baslik": "Acil Kargo İade Bildirimi",
                "konu": "[ÖNEMLİ] Gönderiniz teslim edilemedi!",
                "gonderen_adi": "Hızlı Kargo Müşteri Hizmetleri",
                "icerik_html": "<p>Paketiniz şubede bekliyor. Güncellemek için: <a href='{{LINK}}'>Tıklayın</a></p>",
                "yapay_zeka_ile_mi": False,
                "kanal": "email"
            }
        }
    }

class SablonCevap(SablonOlustur):
    id: int

    class Config:
        from_attributes = True


class KampanyaOlustur(BaseModel):
    sirket_id: int = Field(default=1, description="Hedef şirket ID (Veritabanındaki ID)")
    sablon_id: Optional[int] = Field(default=1, description="Kullanılacak şablon ID")
    ad: str = Field(default="2026 Güz Dönemi İlk Oltalama Tatbikatı", description="Kampanyaya verilecek isim")
    hedef_departman: Optional[str] = Field(default="hepsi", description="hepsi veya hedef departman")
    kanal: Optional[str] = Field(default="email", description="email, whatsapp, sms, qr")
    otomatik_ai: Optional[bool] = Field(default=True, description="Departmana özel otonom AI senaryosu eşle")

    model_config = {
        "json_schema_extra": {
            "example": {
                "sirket_id": 1,
                "sablon_id": 1,
                "ad": "2026 Güz Dönemi İlk Oltalama Tatbikatı",
                "hedef_departman": "hepsi",
                "kanal": "email",
                "otomatik_ai": True
            }
        }
    }

class KampanyaCevap(KampanyaOlustur):
    id: int
    durum: str
    olusturuldugu_tarih: datetime

    class Config:
        from_attributes = True


class SimulasyonLogDetay(BaseModel):
    id: int
    calisan_adi: str
    calisan_email: str
    departman: str
    takip_kodu: str
    simule_link: str
    tiklandi_mi: bool
    egitim_tamamlandi_mi: bool
    senaryo_adi: Optional[str] = None

class KampanyaOzet(BaseModel):
    kampanya_id: int
    kampanya_adi: str
    durum: str
    hedef_departman: Optional[str] = "hepsi"
    toplam_hedef_calisan: int
    tiklayan_sayisi: int
    egitim_tamamlayan_sayisi: int
    tiklanma_orani_yuzde: float
    hedefler: List[SimulasyonLogDetay]
    dagitim_raporu: Optional[Dict[str, Any]] = None


class AISablonIstek(BaseModel):
    sektor: str = Field(default="Finans ve Bankacılık", description="Şirketin faaliyet sektörü")
    departman: str = Field(default="Muhasebe", description="Hedef çalışan departmanı")
    zorluk: str = Field(default="orta", description="kolay, orta veya zor")
    kanal: str = Field(default="email", description="email, sms, whatsapp, qr")

    model_config = {
        "json_schema_extra": {
            "example": {
                "sektor": "Finans ve Bankacılık",
                "departman": "Muhasebe",
                "zorluk": "orta",
                "kanal": "whatsapp"
            }
        }
    }
