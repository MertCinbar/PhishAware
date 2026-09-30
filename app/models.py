import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Sirket(Base):
    __tablename__ = "sirketler"

    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String(100), nullable=False)
    sektor = Column(String(50), nullable=False)
    olusturuldugu_tarih = Column(DateTime, default=datetime.utcnow)

    calisanlar = relationship("Calisan", back_populates="sirket", cascade="all, delete-orphan")
    kampanyalar = relationship("Kampanya", back_populates="sirket", cascade="all, delete-orphan")


class Calisan(Base):
    __tablename__ = "calisanlar"

    id = Column(Integer, primary_key=True, index=True)
    sirket_id = Column(Integer, ForeignKey("sirketler.id"), nullable=False)
    ad_soyad = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, index=True)
    departman = Column(String(50), nullable=False)
    risk_puani = Column(Integer, default=0)

    sirket = relationship("Sirket", back_populates="calisanlar")
    simulasyon_loglari = relationship("SimulasyonLog", back_populates="calisan")


class Sablon(Base):
    __tablename__ = "sablonlar"

    id = Column(Integer, primary_key=True, index=True)
    baslik = Column(String(100), nullable=False)
    konu = Column(String(200), nullable=False)
    gonderen_adi = Column(String(100), nullable=False)
    icerik_html = Column(Text, nullable=False)
    yapay_zeka_ile_mi = Column(Boolean, default=False)
    kanal = Column(String(20), default="email")


class Kampanya(Base):
    __tablename__ = "kampanyalar"

    id = Column(Integer, primary_key=True, index=True)
    sirket_id = Column(Integer, ForeignKey("sirketler.id"), nullable=False)
    sablon_id = Column(Integer, ForeignKey("sablonlar.id"), nullable=False)
    ad = Column(String(100), nullable=False)
    durum = Column(String(20), default="taslak")
    olusturuldugu_tarih = Column(DateTime, default=datetime.utcnow)

    sirket = relationship("Sirket", back_populates="kampanyalar")
    sablon = relationship("Sablon")
    simulasyon_loglari = relationship("SimulasyonLog", back_populates="kampanya")


class SimulasyonLog(Base):
    __tablename__ = "simulasyon_loglari"

    id = Column(Integer, primary_key=True, index=True)
    kampanya_id = Column(Integer, ForeignKey("kampanyalar.id"), nullable=False)
    calisan_id = Column(Integer, ForeignKey("calisanlar.id"), nullable=False)

    takip_kodu = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)

    mail_gonderildi_mi = Column(Boolean, default=False)
    tiklandi_mi = Column(Boolean, default=False)
    tiklanma_tarihi = Column(DateTime, nullable=True)
    egitim_tamamlandi_mi = Column(Boolean, default=False)
    supheli_bildirildi_mi = Column(Boolean, default=False)
    senaryo_adi = Column(String(200), nullable=True)

    kampanya = relationship("Kampanya", back_populates="simulasyon_loglari")
    calisan = relationship("Calisan", back_populates="simulasyon_loglari")
