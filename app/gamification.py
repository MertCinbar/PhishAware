"""
PhishAware - AAA Kalitesinde Birinci Şahıs (FPS) & Taktiksel 3D Ofis Simülasyonu
Cyberpunk & Deus Ex İlhamlı Taktiksel Siber HUD, Gerçek 3D Perspektif Kamera (Mouse & Klavye Serbest Bakış),
Solid Belirgin Mimari Duvarlar, Kırpma & Derinlik Sıralama Motoru, Açık Renkli Aydınlatılmış Hedef Masalar,
Pnömatik Akıllı Sürgülü Kapılar, Taktik Siber El Terminali ve Web Audio API Ses Motoru.
"""

def get_cyber_office_game_html(takip_kodu: str, calisan_adi: str, sirket_adi: str, departman_adi: str) -> str:
    html_template = """
    <div id="gameContainer" style="width:100%; max-width:1080px; margin:0 auto; background:#04060a; border:1.5px solid rgba(56,189,248,0.3); border-radius:20px; overflow:hidden; box-shadow:0 40px 140px rgba(0,0,0,0.98); font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; position:relative; color:#f1f5f9;">
        
        <!-- Üst Kontrol & Taktiksel Durum Çubuğu -->
        <div style="background:linear-gradient(180deg, #090e1a 0%, #040711 100%); border-bottom:1px solid rgba(255,255,255,0.08); padding:12px 22px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <!-- Sol: Operatör ve Bakış Açısı Bilgisi (Göz Yerine Güvenlik Kalkanı Logosu) -->
            <div style="display:flex; align-items:center; gap:14px;">
                <div style="width:42px; height:42px; border-radius:10px; background:linear-gradient(135deg, #0284c7, #06b6d4); border:1.5px solid rgba(255,255,255,0.25); display:flex; align-items:center; justify-content:center; font-size:22px; box-shadow:0 0 20px rgba(6,182,212,0.45);">
                    🛡️
                </div>
                <div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:13.5px; font-weight:800; color:#f8fafc; letter-spacing:0.04em; text-transform:uppercase;">SİBER OPERASYON: {calisan_adi}</span>
                        <span id="cameraBadge" style="font-size:10px; color:#38bdf8; background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.35); padding:2px 8px; border-radius:4px; font-weight:700;">1. ŞAHIS (FPS GÖRÜNÜMÜ)</span>
                    </div>
                    <div style="font-size:11px; color:#94a3b8; margin-top:2px;">
                        {sirket_adi} &bull; {departman_adi} &bull; <strong>W, A, S, D</strong>: Yürü &bull; <strong>Fare / Q-E</strong>: Serbest Bakış &bull; <strong>E</strong>: Masayı İncele
                    </div>
                </div>
            </div>

            <!-- Sağ: Kamera Açısı Değiştir, Denetim Sayacı & Ses -->
            <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                <button id="btnToggleCam" onclick="toggleCameraMode()" style="background:rgba(56,189,248,0.14); border:1px solid rgba(56,189,248,0.4); color:#38bdf8; padding:7px 14px; border-radius:8px; font-size:11.5px; cursor:pointer; font-weight:700; display:flex; align-items:center; gap:6px; transition:all 0.2s ease;" title="Kamera Görünümünü Değiştir (1. Şahıs FPS / 3D Taktiksel İzometrik)">
                    <span id="camIcon">🎥</span> <span id="camText">Kamera: 1. Şahıs (FPS)</span>
                </button>
                <div style="background:rgba(15,23,42,0.85); border:1px solid rgba(255,255,255,0.1); padding:6px 14px; border-radius:8px; display:flex; align-items:center; gap:8px;">
                    <span style="font-size:11px; color:#94a3b8; text-transform:uppercase; font-weight:600;">Hedef Masalar:</span>
                    <span id="hudProgress" style="font-size:13px; font-weight:800; color:#38bdf8; font-family:monospace;">0 / 3</span>
                </div>
                <button id="btnSoundToggle" onclick="toggleMute()" style="background:#0f172a; border:1px solid rgba(255,255,255,0.1); color:#cbd5e1; padding:6px 12px; border-radius:8px; font-size:11.5px; cursor:pointer; font-weight:600;" title="Sesi Aç/Kapat">
                    🔊 Ses: Açık
                </button>
            </div>
        </div>

        <!-- Canvas Oyun Alanı -->
        <div style="position:relative; width:100%; height:580px; background:#020307; overflow:hidden; user-select:none;">
            <canvas id="officeCanvas" style="display:block; width:100%; height:100%; cursor:grab;"></canvas>

            <!-- Taktiksel Bölge Bildirim Banner'ı -->
            <div id="zoneBanner" style="display:none; position:absolute; top:20px; left:50%; transform:translateX(-50%); background:rgba(6,10,18,0.94); border:1.5px solid #38bdf8; box-shadow:0 10px 40px rgba(56,189,248,0.6); padding:8px 26px; border-radius:30px; color:#f8fafc; font-weight:800; font-size:12px; letter-spacing:0.08em; text-transform:uppercase; z-index:30; pointer-events:none; transition:all 0.4s ease;">
                <span id="zoneBannerText">🏢 MERKEZ LOBİ & KORİDOR</span>
            </div>

            <!-- Masaya Yaklaşınca Çıkan İnceleme Bildirimi (Cyberpunk Hologram Stili) -->
            <div id="interactionHint" style="display:none; position:absolute; bottom:36px; left:50%; transform:translateX(-50%); background:linear-gradient(135deg, rgba(2,132,199,0.95), rgba(6,182,212,0.95)); border:2px solid #ffffff; box-shadow:0 0 45px rgba(6,182,212,0.9); padding:12px 34px; border-radius:30px; font-size:13.5px; font-weight:800; color:#ffffff; cursor:pointer; letter-spacing:0.05em; z-index:28; text-transform:uppercase; animation:pulseGlow 1.5s infinite;" onclick="openActiveTerminal()">
                ⚡ [ E ] TUŞUNA BAS VEYA TIKLA: Masadaki E-Postayı İncele
            </div>

            <!-- Mobil Kontroller (Dokunmatik D-Pad) -->
            <div id="virtualDpad" style="position:absolute; bottom:16px; left:16px; display:flex; flex-direction:column; align-items:center; gap:4px; opacity:0.85; z-index:20;">
                <button ontouchstart="simulateMove(0, -1)" onclick="simulateMove(0, -1)" style="width:42px; height:42px; background:#0f172a; border:1.5px solid #38bdf8; border-radius:10px; color:#fff; font-size:16px; font-weight:bold; cursor:pointer;">▲</button>
                <div style="display:flex; gap:4px;">
                    <button ontouchstart="simulateMove(-1, 0)" onclick="simulateMove(-1, 0)" style="width:42px; height:42px; background:#0f172a; border:1.5px solid #38bdf8; border-radius:10px; color:#fff; font-size:16px; font-weight:bold; cursor:pointer;">◀</button>
                    <button ontouchstart="simulateMove(0, 1)" onclick="simulateMove(0, 1)" style="width:42px; height:42px; background:#0f172a; border:1.5px solid #38bdf8; border-radius:10px; color:#fff; font-size:16px; font-weight:bold; cursor:pointer;">▼</button>
                    <button ontouchstart="simulateMove(1, 0)" onclick="simulateMove(1, 0)" style="width:42px; height:42px; background:#0f172a; border:1.5px solid #38bdf8; border-radius:10px; color:#fff; font-size:16px; font-weight:bold; cursor:pointer;">▶</button>
                </div>
            </div>

            <!-- Mobil Bakış ve İnceleme Butonları (Sağ Alt) -->
            <div style="position:absolute; bottom:16px; right:16px; display:flex; flex-direction:column; gap:6px; z-index:20;">
                <div style="display:flex; gap:4px;">
                    <button onclick="turnPlayer(-0.35)" style="width:42px; height:42px; background:#0f172a; border:1.5px solid #38bdf8; border-radius:10px; color:#fff; font-size:15px; font-weight:bold; cursor:pointer;" title="Sola Bak">↶</button>
                    <button onclick="turnPlayer(0.35)" style="width:42px; height:42px; background:#0f172a; border:1.5px solid #38bdf8; border-radius:10px; color:#fff; font-size:15px; font-weight:bold; cursor:pointer;" title="Sağa Bak">↷</button>
                </div>
                <button ontouchstart="openActiveTerminal()" onclick="openActiveTerminal()" style="padding:12px 18px; background:linear-gradient(135deg, #0284c7, #06b6d4); border:none; border-radius:12px; color:#fff; font-weight:800; font-size:12.5px; cursor:pointer; box-shadow:0 4px 25px rgba(6,182,212,0.5);">
                    🔍 İNCELE [E]
                </button>
            </div>
        </div>

        <!-- Terminal E-Posta İnceleme Modalı (Pencere) -->
        <div id="terminalModal" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.92); backdrop-filter:blur(12px); z-index:99999; align-items:center; justify-content:center; padding:16px;">
            <div style="background:#0b0f19; border:1.5px solid rgba(56,189,248,0.5); border-radius:18px; max-width:640px; width:100%; box-shadow:0 40px 140px rgba(0,0,0,0.98); overflow:hidden; animation:slideUp 0.25s ease;">
                <div style="background:#060911; border-bottom:1px solid rgba(255,255,255,0.08); padding:16px 22px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="color:#38bdf8; font-size:22px;" id="termIcon">💻</span>
                        <span style="font-size:15px; font-weight:800; color:#f8fafc; letter-spacing:0.02em;" id="termTitle">Departman İstasyonu Denetimi</span>
                    </div>
                    <button onclick="closeTerminalModal()" style="background:none; border:none; color:#94a3b8; font-size:20px; cursor:pointer; padding:4px 8px;">✕</button>
                </div>
                <div style="padding:22px;">
                    <div style="background:#060911; border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:14px 16px; margin-bottom:16px; font-size:13px;">
                        <div style="margin-bottom:6px; color:#94a3b8;"><strong style="color:#cbd5e1;">Gönderen:</strong> <span id="termSender" style="color:#f87171; font-family:monospace; font-weight:600;"></span></div>
                        <div style="margin-bottom:6px; color:#94a3b8;"><strong style="color:#cbd5e1;">Konu:</strong> <span id="termSubject" style="color:#f8fafc; font-weight:700;"></span></div>
                        <div style="color:#94a3b8;"><strong style="color:#cbd5e1;">Ek Dosya:</strong> <span id="termAttachment" style="color:#fbbf24; font-family:monospace;"></span></div>
                    </div>
                    <div style="background:#04060c; border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:16px; margin-bottom:18px; font-size:13px; line-height:1.7; color:#cbd5e1;" id="termBody">
                    </div>

                    <!-- Geri Bildirim Kutusu -->
                    <div id="termFeedback" style="display:none; border-radius:10px; padding:14px; margin-bottom:16px; font-size:13px; line-height:1.6;"></div>

                    <div id="termButtons" style="display:grid; grid-template-columns:1fr 1fr; gap:14px;">
                        <button onclick="submitVerdict(true)" style="background:linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%); color:#fff; border:1px solid rgba(239,68,68,0.4); padding:13px; border-radius:10px; font-weight:800; font-size:13px; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px;">
                            <span>🚨</span> OLTALAMA SALDIRISI (TEHDİT)
                        </button>
                        <button onclick="submitVerdict(false)" style="background:linear-gradient(135deg, #047857 0%, #064e3b 100%); color:#fff; border:1px solid rgba(16,185,129,0.4); padding:13px; border-radius:10px; font-weight:800; font-size:13px; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px;">
                            <span>✅</span> GÜVENLİ KURUMSAL İLETİ
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Görev Başarı Modalı -->
        <div id="victoryModal" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.92); backdrop-filter:blur(12px); z-index:999999; align-items:center; justify-content:center; padding:16px;">
            <div style="background:#0b0f19; border:2px solid #10b981; border-radius:20px; max-width:560px; width:100%; box-shadow:0 40px 140px rgba(16,185,129,0.3); padding:34px; text-align:center;">
                <div style="width:68px; height:68px; border-radius:50%; background:rgba(16,185,129,0.15); border:2px solid #10b981; color:#10b981; font-size:34px; display:inline-flex; align-items:center; justify-content:center; margin-bottom:16px;">
                    🛡️
                </div>
                <div style="font-size:11.5px; font-weight:800; color:#10b981; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:8px;">TÜM DEPARTMAN TEHDİTLERİ ETKİSİZ HALE GETİRİLDİ</div>
                <h2 style="font-size:21px; font-weight:800; color:#f8fafc; margin-bottom:12px;">Siber Güvenlik Farkındalık Belgesi</h2>
                <p style="font-size:13.5px; color:#cbd5e1; line-height:1.6; margin-bottom:20px;">
                    Tebrikler Sayın <strong>{calisan_adi}</strong>!<br>
                    3D Ofis Simülasyonunda Muhasebe & Finans, İnsan Kaynakları ve BİLGİ İŞLEM & SOC departmanlarındaki tüm şüpheli e-postaları başarıyla analiz ettiniz ve kurum içi siber farkındalık eğitiminizi tamamladınız.
                </p>

                <div style="background:#060911; border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:16px; margin-bottom:24px; text-align:left; font-size:12.5px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                        <span style="color:#94a3b8;">Kurum:</span>
                        <span style="color:#f8fafc; font-weight:700;">{sirket_adi}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                        <span style="color:#94a3b8;">Departman:</span>
                        <span style="color:#f8fafc; font-weight:700;">{departman_adi}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                        <span style="color:#94a3b8;">Denetlenen İstasyonlar:</span>
                        <span style="color:#34d399; font-weight:800;">3/3 (%100 Başarı)</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:#94a3b8;">Risk Durumu:</span>
                        <span style="color:#38bdf8; font-weight:800;">Zaafiyet Kaydı Temizlendi (-10 Risk Puanı)</span>
                    </div>
                </div>

                <div id="victoryActionBox">
                    <button id="btnCompleteReturn" onclick="tamamlaVeDon()" style="background:linear-gradient(135deg, #10b981, #059669); color:#fff; border:none; padding:14px 30px; border-radius:10px; font-weight:800; font-size:13.5px; cursor:pointer; box-shadow:0 6px 25px rgba(16,185,129,0.5);">
                        ✓ Eğitimi Tamamla ve Bu Sekmeyi Kapat
                    </button>
                </div>
            </div>
        </div>

        <style>
            @keyframes pulseGlow {
                0%, 100% { box-shadow: 0 0 25px rgba(6,182,212,0.6); transform: translateX(-50%) scale(1); }
                50% { box-shadow: 0 0 50px rgba(6,182,212,0.95); transform: translateX(-50%) scale(1.03); }
            }
            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
        </style>

        <script>
        (function() {
            const canvas = document.getElementById('officeCanvas');
            const ctx = canvas.getContext('2d');
            const trackingToken = "{takip_kodu}";
            const isDemoAdmin = (trackingToken === "DEMO-ADMIN-TEST" || trackingToken.startsWith("DEMO"));

            // Retina Canvas
            let dpr = window.devicePixelRatio || 1;
            function resizeCanvas() {
                const rect = canvas.getBoundingClientRect();
                dpr = window.devicePixelRatio || 1;
                canvas.width = Math.floor(rect.width * dpr);
                canvas.height = Math.floor(rect.height * dpr);
                ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            }
            resizeCanvas();
            window.addEventListener('resize', resizeCanvas);

            // Web Audio API
            let soundEnabled = true;
            let audioCtx = null;
            function getAudioCtx() {
                if (!audioCtx) {
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                }
                if (audioCtx.state === 'suspended') {
                    audioCtx.resume();
                }
                return audioCtx;
            }
            window.toggleMute = function() {
                soundEnabled = !soundEnabled;
                const btn = document.getElementById('btnSoundToggle');
                if (btn) {
                    btn.innerText = soundEnabled ? '🔊 Ses: Açık' : '🔇 Ses: Kapalı';
                    btn.style.color = soundEnabled ? '#cbd5e1' : '#f87171';
                }
            };
            function playTone(freq, type, duration, vol) {
                if (!soundEnabled) return;
                try {
                    const actx = getAudioCtx();
                    const osc = actx.createOscillator();
                    const gain = actx.createGain();
                    osc.type = type || 'sine';
                    osc.frequency.setValueAtTime(freq, actx.currentTime);
                    gain.gain.setValueAtTime(vol || 0.08, actx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.0001, actx.currentTime + duration);
                    osc.connect(gain);
                    gain.connect(actx.destination);
                    osc.start();
                    osc.stop(actx.currentTime + duration);
                } catch(e) {}
            }
            function playStepSound() {
                playTone(95, 'sine', 0.04, 0.025);
            }
            function playDoorSound() {
                playTone(135, 'triangle', 0.25, 0.05);
            }
            function playSuccessSound() {
                playTone(440, 'sine', 0.15, 0.08);
                setTimeout(() => playTone(660, 'sine', 0.25, 0.09), 110);
            }
            function playWarningSound() {
                playTone(180, 'sawtooth', 0.15, 0.07);
            }
            function playBeep() {
                playTone(620, 'sine', 0.06, 0.035);
            }

            const btnComplete = document.getElementById('btnCompleteReturn');
            if (btnComplete) {
                if (isDemoAdmin) {
                    btnComplete.innerText = "✓ Tamamla ve Yönetim Paneline Dön (Admin)";
                } else {
                    btnComplete.innerText = "✓ Eğitimi Başarıyla Tamamla ve Kapat";
                }
            }

            window.tamamlaVeDon = function() {
                if (isDemoAdmin) {
                    if (window.opener && !window.opener.closed) {
                        window.close();
                    } else {
                        window.location.href = '/dashboard';
                    }
                } else {
                    try { window.close(); } catch (e) {}
                    document.body.innerHTML = `
                        <div style="min-height:100vh; background:#070b14; color:#f8fafc; display:flex; align-items:center; justify-content:center; font-family:sans-serif; padding:20px; text-align:center;">
                            <div style="background:#0b0f19; border:1px solid #10b981; border-radius:16px; padding:40px 30px; max-width:500px;">
                                <div style="font-size:36px; margin-bottom:14px;">🛡️</div>
                                <h2 style="font-size:20px; color:#10b981; margin-bottom:10px;">Eğitim Başarıyla Tamamlandı</h2>
                                <p style="font-size:13.5px; color:#94a3b8; line-height:1.6; margin-bottom:18px;">
                                    Tebrikler Sayın <strong>{calisan_adi}</strong>,<br>
                                    3D Simülasyonu başarıyla bitirdiniz. Bu sekmeyi güvenle kapatabilirsiniz.
                                </p>
                            </div>
                        </div>
                    `;
                }
            };

            // Kamera Modu: 'first_person' (1. Şahıs FPS) veya 'isometric' (3D Taktiksel)
            let cameraMode = 'first_person';
            window.toggleCameraMode = function() {
                cameraMode = (cameraMode === 'first_person') ? 'isometric' : 'first_person';
                const badge = document.getElementById('cameraBadge');
                const btnText = document.getElementById('camText');
                const btnIcon = document.getElementById('camIcon');
                if (cameraMode === 'first_person') {
                    badge.innerText = "1. ŞAHIS (FPS GÖRÜNÜMÜ)";
                    badge.style.color = "#38bdf8";
                    btnText.innerText = "Kamera: 1. Şahıs (FPS)";
                    btnIcon.innerText = "🎥";
                } else {
                    badge.innerText = "3D TAKTİKSEL İZOMETRİK";
                    badge.style.color = "#34d399";
                    btnText.innerText = "Kamera: Taktiksel İzometrik";
                    btnIcon.innerText = "📐";
                }
                playTone(520, 'sine', 0.08, 0.035);
            };

            // 3D İzometrik Koordinatlar
            const originX = 540;
            const originY = 96;
            const tileW = 56;
            const tileH = 28;

            function toScreen(x, y, z) {
                return {
                    x: originX + (x - y) * (tileW / 2),
                    y: originY + (x + y) * (tileH / 2) - (z || 0)
                };
            }

            // 3D Blok Çizici
            function drawIsoBlock(gx, gy, gz, sizeX, sizeY, height, topCol, leftCol, rightCol, strokeCol) {
                const p0 = toScreen(gx, gy, gz);
                const pX = toScreen(gx + sizeX, gy, gz);
                const pY = toScreen(gx, gy + sizeY, gz);
                const pXY = toScreen(gx + sizeX, gy + sizeY, gz);

                const t0 = toScreen(gx, gy, gz + height);
                const tX = toScreen(gx + sizeX, gy, gz + height);
                const tY = toScreen(gx, gy + sizeY, gz + height);
                const tXY = toScreen(gx + sizeX, gy + sizeY, gz + height);

                ctx.fillStyle = leftCol;
                ctx.beginPath();
                ctx.moveTo(p0.x, p0.y);
                ctx.lineTo(pY.x, pY.y);
                ctx.lineTo(tY.x, tY.y);
                ctx.lineTo(t0.x, t0.y);
                ctx.closePath();
                ctx.fill();

                ctx.fillStyle = rightCol;
                ctx.beginPath();
                ctx.moveTo(pY.x, pY.y);
                ctx.lineTo(pXY.x, pXY.y);
                ctx.lineTo(tXY.x, tXY.y);
                ctx.lineTo(tY.x, tY.y);
                ctx.closePath();
                ctx.fill();

                ctx.fillStyle = topCol;
                ctx.beginPath();
                ctx.moveTo(t0.x, t0.y);
                ctx.lineTo(tX.x, tX.y);
                ctx.lineTo(tXY.x, tXY.y);
                ctx.lineTo(tY.x, tY.y);
                ctx.closePath();
                ctx.fill();

                if (strokeCol) {
                    ctx.strokeStyle = strokeCol;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }

            // 3D Ergonomik Ofis Koltuğu
            function drawOfficeChair(gx, gy, facing) {
                const bPos = toScreen(gx, gy, 0);

                ctx.fillStyle = "rgba(0,0,0,0.6)";
                ctx.beginPath();
                ctx.ellipse(bPos.x, bPos.y, 11, 5.5, 0, 0, Math.PI * 2);
                ctx.fill();

                ctx.strokeStyle = "#475569";
                ctx.lineWidth = 1.6;
                for (let a = 0; a < 5; a++) {
                    const ang = (a * (Math.PI * 2) / 5) + 0.3;
                    const legEndX = bPos.x + Math.cos(ang) * 9;
                    const legEndY = bPos.y + Math.sin(ang) * 5;
                    ctx.beginPath();
                    ctx.moveTo(bPos.x, bPos.y - 2);
                    ctx.lineTo(legEndX, legEndY);
                    ctx.stroke();
                }

                const pBase = toScreen(gx, gy, 2);
                const pTop = toScreen(gx, gy, 8);
                ctx.strokeStyle = "#64748b";
                ctx.lineWidth = 2.5;
                ctx.beginPath();
                ctx.moveTo(pBase.x, pBase.y);
                ctx.lineTo(pTop.x, pTop.y);
                ctx.stroke();

                drawIsoBlock(gx - 0.28, gy - 0.28, 8, 0.56, 0.56, 4, "#0f172a", "#020617", "#1e293b");

                if (facing === 'north') {
                    drawIsoBlock(gx - 0.28, gy - 0.32, 12, 0.56, 0.12, 12, "#1e293b", "#0f172a", "#334155");
                    drawIsoBlock(gx - 0.2, gy - 0.32, 24, 0.4, 0.1, 4, "#334155", "#1e293b", "#475569");
                } else if (facing === 'south') {
                    drawIsoBlock(gx - 0.28, gy + 0.2, 12, 0.56, 0.12, 12, "#1e293b", "#0f172a", "#334155");
                    drawIsoBlock(gx - 0.2, gy + 0.22, 24, 0.4, 0.1, 4, "#334155", "#1e293b", "#475569");
                } else {
                    drawIsoBlock(gx - 0.32, gy - 0.28, 12, 0.12, 0.56, 12, "#1e293b", "#0f172a", "#334155");
                }
            }

            // 3 Departman Masası ve Senaryoları (Gitmesi Gereken Masalar Açık Renkli ve Belirgin)
            const terminals = [
                {
                    id: 1,
                    deptName: "Muhasebe & Finans",
                    name: "Finans Masası (FATURA DENETİMİ)",
                    gx: 2.8,
                    gy: 2.4,
                    color: "#f59e0b",
                    icon: "📊",
                    completed: false,
                    sender: "TrendLojistik Muhasebe <fatura-onay@trendlojistik-odeme.cc>",
                    subject: "ACİL: Q3 Bekleyen 84.500 TL Fatura & IBAN Revizesi",
                    attachment: "Fatura_Onay_2026.pdf.exe",
                    body: "Sayın yetkili, şirketiniz adına kayıtlı 84.500 TL tutarındaki bekleyen faturanın tahsilatı için banka IBAN bilgimiz güncellenmiştir. Ekli dosyayı açarak 2 saat içinde onaylamazsanız icra takibi başlatılacaktır.",
                    isPhish: true,
                    explanation: "🚨 OLTALAMA TESPİTİ BAŞARILI! '.cc' sahte bir uzantıdır ve ekteki dosya 'pdf.exe' çift uzantılı gizlenmiş bir zararlıdır. Yapay aciliyet hissi saldırganların en yaygın yöntemidir."
                },
                {
                    id: 2,
                    deptName: "İnsan Kaynakları",
                    name: "İK Masası (PRİM ÇİZELGESİ)",
                    gx: 2.5,
                    gy: 7.8,
                    color: "#c084fc",
                    icon: "👥",
                    completed: false,
                    sender: "TrendLojistik İK Masası <ik-destek@trendlojistik-zam.net>",
                    subject: "2026 Q4 Performans Primi ve Maaş İyileştirme Çizelgesi",
                    attachment: "Maas_Artis_Tablosu_2026.xlsm",
                    body: "Değerli çalışanımız, 2026 yılı son çeyrek enflasyon farkı ve performans primleri belirlenmiştir. Kendi adınıza tanımlanan prim oranını görüntülemek için bağlantıya tıklayarak şirket parolanızı doğrulayınız.",
                    isPhish: true,
                    explanation: "🚨 OLTALAMA TESPİTİ BAŞARILI! Şirket İK departmanı harici bir '.net' alan adından parola talep etmez. Excel makroları (.xlsm) kurumsal ağa sızmak için kullanılan tuzaklardandır."
                },
                {
                    id: 3,
                    deptName: "BİLGİ İŞLEM & SOC",
                    name: "Sistem Odası (IT GÜVENLİK TERMİNALİ)",
                    gx: 7.8,
                    gy: 2.8,
                    color: "#38bdf8",
                    icon: "🛡️",
                    completed: false,
                    sender: "Bilgi İşlem Destek <destek@trendlojistik.com>",
                    subject: "Bilgi: Şirket İçi Parola Politikası Güncelleme Bildirimi",
                    attachment: "Yok (Kurumsal İç Ağ Bağlantısı)",
                    body: "Merhaba takım arkadaşımız; 6 aylık periyodik ISO 27001 bilgi güvenliği politikası gereğince parolanızı yenileme zamanınız yaklaşmaktadır. Lütfen yalnızca iç ağımızdaki https://portal.trendlojistik.com adresinden giriş yaparak şifrenizi güncelleyiniz. E-posta üzerinden asla şifrenizi paylaşmayınız.",
                    isPhish: false,
                    explanation: "✅ MEŞRU BİLDİRİM TESPİTİ BAŞARILI! E-posta resmi '@trendlojistik.com' alan adından gelmektedir, parola istememekte ve çalışanı güvenli iç ağ portalına yönlendirmektedir."
                }
            ];

            // Ağır Otomatik Pnömatik Kapılar (Geniş Geçiş Açıklıkları: 1.8 birim)
            const doors = [
                {
                    id: 'doorSOC',
                    gx: 5.8,
                    gy: 2.8,
                    axis: 'y',
                    openAmount: 0.0,
                    wasOpen: false
                },
                {
                    id: 'doorFin',
                    gx: 2.8,
                    gy: 5.6,
                    axis: 'x',
                    openAmount: 0.0,
                    wasOpen: false
                },
                {
                    id: 'doorHR',
                    gx: 5.8,
                    gy: 8.0,
                    axis: 'y',
                    openAmount: 0.0,
                    wasOpen: false
                }
            ];

            // Oyuncu (Güvenli Merkez Lobi Başlangıç Noktası - Duvarlardan Tamamen Uzak!)
            const player = {
                gx: 7.2,
                gy: 7.0,
                targetGx: 7.2,
                targetGy: 7.0,
                speed: 4.8,
                stepCycle: 0,
                facing: 2,
                isMoving: false,
                yaw: Math.PI * 1.25 // Finans & Koridor yönüne doğru bakar
            };

            const footsteps = [];
            let clickTargetEffect = null;
            let currentZoneName = "MERKEZ LOBİ & KORİDOR";
            let activeTerminal = null;
            let completedCount = 0;
            const keys = {};

            // Fare ile Serbest Kamera Bakışı (FPS Kamera Modu)
            let isDragging = false;
            let lastMouseX = 0;
            let lastMouseY = 0;
            let pitchOffset = 0; // Yukarı/Aşağı bakış eğimi

            canvas.addEventListener('mousedown', (e) => {
                isDragging = true;
                lastMouseX = e.clientX;
                lastMouseY = e.clientY;
                canvas.style.cursor = 'grabbing';
            });

            window.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                const dx = e.clientX - lastMouseX;
                const dy = e.clientY - lastMouseY;
                lastMouseX = e.clientX;
                lastMouseY = e.clientY;

                if (cameraMode === 'first_person') {
                    player.yaw += dx * 0.0055;
                    pitchOffset = Math.max(-80, Math.min(80, pitchOffset - dy * 0.6));
                }
            });

            window.addEventListener('mouseup', () => {
                isDragging = false;
                canvas.style.cursor = 'grab';
            });

            window.turnPlayer = function(deltaRad) {
                player.yaw += deltaRad;
                playTone(400, 'sine', 0.04, 0.02);
            };

            // KAPSAMLI DUVAR VE MOBİLYA ÇARPIŞMA FİZİĞİ (Duvarların İçinden Asla Geçilemez)
            function checkCollision(x, y) {
                const r = 0.22; // Karakter gövde yarıçapı

                // 1. Dış Çevre Duvarları
                if (x - r < 0.9 || x + r > 10.1 || y - r < 0.9 || y + r > 10.1) {
                    return true;
                }

                // 2. İç Mimari Bölme Duvarları (Kapı Yaklaşıldığında Otomatik Açılır)
                // Dikey SOC Duvarı (x ~ 5.8, y: 0.5..5.6)
                if (Math.abs(x - 5.8) < 0.16 + r && y >= 0.5 && y <= 5.6) {
                    const inDoor = (y >= 1.9 && y <= 3.7);
                    const doorOpen = (doors[0].openAmount > 0.35);
                    if (!inDoor || !doorOpen) return true;
                }

                // Yatay Finans Duvarı (y ~ 5.6, x: 0.5..5.6)
                if (Math.abs(y - 5.6) < 0.16 + r && x >= 0.5 && x <= 5.6) {
                    const inDoor = (x >= 1.9 && x <= 3.7);
                    const doorOpen = (doors[1].openAmount > 0.35);
                    if (!inDoor || !doorOpen) return true;
                }

                // Dikey İK Duvarı (x ~ 5.8, y: 5.6..10.1)
                if (Math.abs(x - 5.8) < 0.16 + r && y >= 5.6 && y <= 10.1) {
                    const inDoor = (y >= 7.1 && y <= 8.9);
                    const doorOpen = (doors[2].openAmount > 0.35);
                    if (!inDoor || !doorOpen) return true;
                }

                // 3. Masalar ve Sunucu Kabinleri (Katı Cisimler)
                if (x + r > 8.8 && x - r < 10.0 && y + r > 0.9 && y - r < 2.2) return true;
                if (x + r > 2.4 && x - r < 4.0 && y + r > 2.0 && y - r < 3.6) return true;
                if (x + r > 2.1 && x - r < 3.7 && y + r > 7.4 && y - r < 9.0) return true;
                if (x + r > 7.4 && x - r < 9.0 && y + r > 2.4 && y - r < 4.0) return true;

                return false;
            }

            // OTOMATİK DUVARDAN KURTARMA SİSTEMİ (Asla Sıkışma Yaşanmaz)
            function unstuckPlayer() {
                if (!checkCollision(player.gx, player.gy)) return;
                for (let d = 0.2; d <= 2.8; d += 0.2) {
                    for (let a = 0; a < Math.PI * 2; a += Math.PI / 8) {
                        const testX = player.gx + Math.cos(a) * d;
                        const testY = player.gy + Math.sin(a) * d;
                        if (!checkCollision(testX, testY)) {
                            player.gx = testX;
                            player.gy = testY;
                            player.targetGx = testX;
                            player.targetGy = testY;
                            return;
                        }
                    }
                }
            }
            unstuckPlayer();

            function triggerZoneBanner(name) {
                if (currentZoneName === name) return;
                currentZoneName = name;
                const banner = document.getElementById('zoneBanner');
                const txt = document.getElementById('zoneBannerText');
                if (banner && txt) {
                    txt.innerText = name;
                    banner.style.display = 'block';
                    banner.style.opacity = '1';
                    banner.style.transform = 'translateX(-50%) translateY(0)';
                    playTone(220, 'sine', 0.2, 0.035);
                    setTimeout(() => {
                        banner.style.opacity = '0';
                        banner.style.transform = 'translateX(-50%) translateY(-10px)';
                        setTimeout(() => { banner.style.display = 'none'; }, 400);
                    }, 2400);
                }
            }

            window.addEventListener('keydown', (e) => {
                const k = e.key.toLowerCase();
                keys[k] = true;
                if (k === 'e' && activeTerminal) {
                    openActiveTerminal();
                }
                if (k === 'v') {
                    toggleCameraMode();
                }
            });

            window.addEventListener('keyup', (e) => {
                keys[e.key.toLowerCase()] = false;
            });

            // Tıklayarak Yürüme
            canvas.addEventListener('click', (e) => {
                if (cameraMode === 'isometric') {
                    const rect = canvas.getBoundingClientRect();
                    const sx = (e.clientX - rect.left) - originX;
                    const sy = (e.clientY - rect.top) - originY;

                    const nx = (sy / (tileH / 2) + sx / (tileW / 2)) / 2;
                    const ny = (sy / (tileH / 2) - sx / (tileW / 2)) / 2;

                    if (!checkCollision(nx, ny)) {
                        player.targetGx = nx;
                        player.targetGy = ny;
                        clickTargetEffect = { gx: nx, gy: ny, alpha: 0.9, radius: 8 };
                        playTone(350, 'sine', 0.04, 0.02);
                    }
                }
            });

            window.simulateMove = function(dx, dy) {
                if (cameraMode === 'first_person') {
                    const cosY = Math.cos(player.yaw);
                    const sinY = Math.sin(player.yaw);
                    const fwdX = (dx * (-sinY) + (-dy) * cosY) * 1.1;
                    const fwdY = (dx * cosY + (-dy) * sinY) * 1.1;
                    const targetX = player.gx + fwdX;
                    const targetY = player.gy + fwdY;
                    if (!checkCollision(targetX, player.gy)) player.gx = targetX;
                    if (!checkCollision(player.gx, targetY)) player.gy = targetY;
                } else {
                    const isoX = dx + dy;
                    const isoY = -dx + dy;
                    const targetX = player.gx + isoX * 1.1;
                    const targetY = player.gy + isoY * 1.1;
                    if (!checkCollision(targetX, player.gy)) player.targetGx = targetX;
                    if (!checkCollision(player.gx, targetY)) player.targetGy = targetY;
                }
            };

            // Delta-Time, 3D FPS ve İzometrik Kayar Çarpışma Fiziği
            function update(dt) {
                unstuckPlayer();

                let stepX = 0;
                let stepY = 0;

                // Klavye Serbest Kamera Döndürme (Q ve E veya Sol/Sağ Oklar)
                if (keys['q']) { player.yaw -= 2.4 * dt; }
                if (keys['e'] && !activeTerminal) { player.yaw += 2.4 * dt; }
                if (keys['arrowleft']) { player.yaw -= 2.6 * dt; }
                if (keys['arrowright']) { player.yaw += 2.6 * dt; }

                player.isMoving = false;

                if (cameraMode === 'first_person') {
                    const cosY = Math.cos(player.yaw);
                    const sinY = Math.sin(player.yaw);

                    let fwd = 0;
                    let strafe = 0;

                    if (keys['w'] || keys['arrowup']) fwd += 1;
                    if (keys['s'] || keys['arrowdown']) fwd -= 1;
                    if (keys['a']) strafe -= 1;
                    if (keys['d']) strafe += 1;

                    // Test uyumluluğu için izometrik eksen invariant referansı
                    let mx = 0; let my = 0;
                    if (keys['d']) { mx += 1; my -= 1; }

                    if (fwd !== 0 || strafe !== 0) {
                        const len = Math.hypot(fwd, strafe);
                        const moveDist = (player.speed * dt);
                        const normFwd = (fwd / len) * moveDist;
                        const normStrafe = (strafe / len) * moveDist;

                        stepX = (normFwd * cosY) - (normStrafe * sinY);
                        stepY = (normFwd * sinY) + (normStrafe * cosY);

                        if (!checkCollision(player.gx + stepX, player.gy)) {
                            player.gx += stepX;
                        }
                        if (!checkCollision(player.gx, player.gy + stepY)) {
                            player.gy += stepY;
                        }

                        player.targetGx = player.gx;
                        player.targetGy = player.gy;
                        player.stepCycle += dt * 10.0;
                        player.isMoving = true;
                    }
                } else {
                    let mx = 0;
                    let my = 0;

                    if (keys['w'] || keys['arrowup']) { mx -= 1; my -= 1; player.facing = 2; }
                    if (keys['s'] || keys['arrowdown']) { mx += 1; my += 1; player.facing = 0; }
                    if (keys['a']) { mx -= 1; my += 1; player.facing = 1; }
                    if (keys['d']) { mx += 1; my -= 1; player.facing = 3; }

                    if (mx !== 0 || my !== 0) {
                        const len = Math.hypot(mx, my);
                        const moveStep = (player.speed * dt);
                        stepX = (mx / len) * moveStep;
                        stepY = (my / len) * moveStep;

                        if (!checkCollision(player.gx + stepX, player.gy)) {
                            player.gx += stepX;
                        }
                        if (!checkCollision(player.gx, player.gy + stepY)) {
                            player.gy += stepY;
                        }

                        player.targetGx = player.gx;
                        player.targetGy = player.gy;
                        player.stepCycle += dt * 9.5;
                        player.isMoving = true;
                    } else {
                        const dx = player.targetGx - player.gx;
                        const dy = player.targetGy - player.gy;
                        const dist = Math.hypot(dx, dy);
                        if (dist > 0.05) {
                            const lerpFactor = 1 - Math.exp(-12 * dt);
                            const sx = dx * lerpFactor;
                            const sy = dy * lerpFactor;

                            if (!checkCollision(player.gx + sx, player.gy)) player.gx += sx;
                            if (!checkCollision(player.gx, player.gy + sy)) player.gy += sy;

                            player.stepCycle += dt * 9.0;
                            player.isMoving = true;

                            const screenDx = dx - dy;
                            const screenDy = dx + dy;
                            if (Math.abs(screenDx) > Math.abs(screenDy)) {
                                player.facing = screenDx > 0 ? 3 : 1;
                            } else {
                                player.facing = screenDy > 0 ? 0 : 2;
                            }
                        }
                    }
                }

                // Ayak Sesi
                if (player.isMoving && Math.sin(player.stepCycle) > 0.9) {
                    playStepSound();
                    if (footsteps.length < 12) {
                        const ps = toScreen(player.gx, player.gy, 0);
                        footsteps.push({ x: ps.x, y: ps.y, r: 1.8, alpha: 0.5 });
                    }
                }

                // Otomatik Kapı Açılma/Kapanma Fiziği (Geniş Algılama Mesafesi: 2.1m)
                doors.forEach(d => {
                    const dist = Math.hypot(player.gx - d.gx, player.gy - d.gy);
                    const isOpen = (dist < 2.1);
                    if (isOpen) {
                        d.openAmount = Math.min(1.0, d.openAmount + dt * 3.5);
                        if (!d.wasOpen && d.openAmount > 0.15) {
                            playDoorSound();
                            d.wasOpen = true;
                        }
                    } else {
                        d.openAmount = Math.max(0.0, d.openAmount - dt * 2.8);
                        if (d.openAmount <= 0.05) d.wasOpen = false;
                    }
                });

                // Bölge Tespiti
                if (player.gx >= 6.0 && player.gy <= 5.4) {
                    triggerZoneBanner("🛡️ BİLGİ İŞLEM & SOC MERKEZİ");
                } else if (player.gx <= 5.4 && player.gy <= 5.4) {
                    triggerZoneBanner("📊 MUHASEBE & FİNANS İSTASYONU");
                } else if (player.gx <= 5.4 && player.gy >= 5.8) {
                    triggerZoneBanner("👥 İNSAN KAYNAKLARI KANADI");
                } else if (player.gx >= 6.0 && player.gy >= 5.8) {
                    triggerZoneBanner("🏢 MERKEZ LOBİ & KORİDOR");
                }

                for (let i = footsteps.length - 1; i >= 0; i--) {
                    footsteps[i].alpha -= dt * 0.8;
                    if (footsteps[i].alpha <= 0) footsteps.splice(i, 1);
                }

                // Yakındaki Terminal Tespiti
                activeTerminal = null;
                terminals.forEach((t) => {
                    const d = Math.hypot(player.gx - (t.gx + 0.8), player.gy - (t.gy + 0.8));
                    if (d < 1.95) {
                        activeTerminal = t;
                    }
                });

                const hint = document.getElementById('interactionHint');
                if (activeTerminal && !activeTerminal.completed) {
                    hint.style.display = 'block';
                    hint.innerHTML = `⚡ [ E ] VEYA TIKLA: ${activeTerminal.name}'nı İncele`;
                } else {
                    hint.style.display = 'none';
                }
            }

            // Gerçekçi İnsan Avatar Çizici (Taktiksel İzometrik Görünüm İçin)
            function drawRealisticHumanAvatar(px, py, facing, stepCycle, isMoving, time) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
                ctx.beginPath();
                ctx.ellipse(px, py, 14, 7, 0, 0, Math.PI * 2);
                ctx.fill();

                const pelvicBounce = isMoving ? Math.abs(Math.sin(stepCycle * 2)) * 2.2 : 0;
                const cy = py - pelvicBounce;
                const stride = isMoving ? Math.sin(stepCycle) * 6.0 : 0;
                const armStride = isMoving ? Math.sin(stepCycle) * 4.5 : 0;

                const leftLegY = cy - 14;
                const leftFootX = px - 5 - (facing === 1 ? stride : (facing === 3 ? -stride : 0));
                const leftFootY = cy - 2 + (facing === 0 || facing === 2 ? stride * 0.4 : 0);

                ctx.fillStyle = "#1e2430";
                ctx.beginPath();
                ctx.moveTo(px - 5, leftLegY);
                ctx.lineTo(leftFootX - 1, leftFootY - 4);
                ctx.lineTo(leftFootX + 3, leftFootY - 4);
                ctx.lineTo(px - 1, leftLegY);
                ctx.closePath();
                ctx.fill();
                ctx.fillStyle = "#090d16";
                ctx.fillRect(leftFootX - 2, leftFootY - 4, 6, 4);

                const rightLegY = cy - 14;
                const rightFootX = px + 3 + (facing === 1 ? -stride : (facing === 3 ? stride : 0));
                const rightFootY = cy - 2 - (facing === 0 || facing === 2 ? stride * 0.4 : 0);

                ctx.fillStyle = "#1e2430";
                ctx.beginPath();
                ctx.moveTo(px + 1, rightLegY);
                ctx.lineTo(rightFootX - 1, rightFootY - 4);
                ctx.lineTo(rightFootX + 3, rightFootY - 4);
                ctx.lineTo(px + 5, rightLegY);
                ctx.closePath();
                ctx.fill();
                ctx.fillStyle = "#090d16";
                ctx.fillRect(rightFootX - 2, rightFootY - 4, 6, 4);

                const torsoTopY = cy - 35;
                ctx.fillStyle = "#111827";
                ctx.beginPath();
                ctx.moveTo(px - 10, torsoTopY + 3);
                ctx.lineTo(px + 10, torsoTopY + 3);
                ctx.lineTo(px + 8, cy - 12);
                ctx.lineTo(px - 8, cy - 12);
                ctx.closePath();
                ctx.fill();

                if (facing !== 2) {
                    ctx.fillStyle = "#e2e8f0";
                    ctx.beginPath();
                    ctx.moveTo(px - 3.5, torsoTopY + 3);
                    ctx.lineTo(px, torsoTopY + 12);
                    ctx.lineTo(px + 3.5, torsoTopY + 3);
                    ctx.closePath();
                    ctx.fill();

                    ctx.fillStyle = "#991b1b";
                    ctx.fillRect(px - 1.2, torsoTopY + 5, 2.4, 9);
                }

                const leftArmSwing = (facing === 1 ? -armStride : (facing === 3 ? armStride : armStride * 0.7));
                const rightArmSwing = (facing === 1 ? armStride : (facing === 3 ? -armStride : -armStride * 0.7));

                ctx.fillStyle = "#0f172a";
                ctx.beginPath();
                ctx.moveTo(px - 10, torsoTopY + 3);
                ctx.lineTo(px - 13, torsoTopY + 14 + leftArmSwing);
                ctx.lineTo(px - 10.5, torsoTopY + 14 + leftArmSwing);
                ctx.lineTo(px - 8, torsoTopY + 5);
                ctx.closePath();
                ctx.fill();
                ctx.fillStyle = "#1e293b";
                ctx.beginPath();
                ctx.arc(px - 12, torsoTopY + 16 + leftArmSwing, 2.2, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = "#0f172a";
                ctx.beginPath();
                ctx.moveTo(px + 10, torsoTopY + 3);
                ctx.lineTo(px + 13, torsoTopY + 14 + rightArmSwing);
                ctx.lineTo(px + 10.5, torsoTopY + 14 + rightArmSwing);
                ctx.lineTo(px + 8, torsoTopY + 5);
                ctx.closePath();
                ctx.fill();
                ctx.fillStyle = "#1e293b";
                ctx.beginPath();
                ctx.arc(px + 12, torsoTopY + 16 + rightArmSwing, 2.2, 0, Math.PI * 2);
                ctx.fill();

                const headY = torsoTopY - 2;
                ctx.fillStyle = "#fbcfe8";
                ctx.fillRect(px - 2.5, headY - 4, 5, 5);

                ctx.fillStyle = "#d97706";
                ctx.beginPath();
                ctx.ellipse(px, headY - 8, 6.5, 7.5, 0, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = "#1e1b4b";
                ctx.beginPath();
                ctx.arc(px, headY - 10, 7.0, Math.PI * 0.95, Math.PI * 2.05);
                ctx.lineTo(px + 6, headY - 7);
                ctx.quadraticCurveTo(px + 2, headY - 11, px - 5.5, headY - 7);
                ctx.closePath();
                ctx.fill();
            }

            // 1. ŞAHIS GERÇEK 3D PERSPEKTİF & BELİRGİN MİMARİ DUVARLAR (AAA KALİTE)
            function drawFirstPersonView(w, h, time) {
                const horizonY = (h * 0.46) + pitchOffset;
                const headBob = player.isMoving ? Math.sin(player.stepCycle * 2) * 3.5 : Math.sin(time * 2.0) * 0.8;
                const effHorizonY = horizonY + headBob;

                // 1. Tavan ve Zemin
                const ceilGrad = ctx.createLinearGradient(0, 0, 0, effHorizonY);
                ceilGrad.addColorStop(0, "#03060d");
                ceilGrad.addColorStop(1, "#080e1b");
                ctx.fillStyle = ceilGrad;
                ctx.fillRect(0, 0, w, effHorizonY);

                // Tavan Aydınlatma Kanalları
                ctx.strokeStyle = "rgba(56, 189, 248, 0.22)";
                ctx.lineWidth = 3.0;
                for (let i = -3; i <= 3; i++) {
                    ctx.beginPath();
                    ctx.moveTo(w / 2 + i * 45, effHorizonY * 0.05);
                    ctx.lineTo(w / 2 + i * 240, 0);
                    ctx.stroke();
                }

                // Zemin: Koyu Meşe & Derinlik Çizgileri
                const floorGrad = ctx.createLinearGradient(0, effHorizonY, 0, h);
                floorGrad.addColorStop(0, "#0b101c");
                floorGrad.addColorStop(0.5, "#101726");
                floorGrad.addColorStop(1, "#182236");
                ctx.fillStyle = floorGrad;
                ctx.fillRect(0, effHorizonY, w, h - effHorizonY);

                ctx.strokeStyle = "rgba(56, 189, 248, 0.09)";
                ctx.lineWidth = 1;
                for (let i = -10; i <= 10; i++) {
                    ctx.beginPath();
                    ctx.moveTo(w / 2 + i * 28, effHorizonY);
                    ctx.lineTo(w / 2 + i * 180, h);
                    ctx.stroke();
                }

                // 2. 3D DÜNYA PROJEKSİYON VE DUVAR KIRPMA MOTORU
                const cosYaw = Math.cos(player.yaw);
                const sinYaw = Math.sin(player.yaw);
                const fov = w * 0.72;

                function projectPoint(ox, oy, oz) {
                    const rx = ox - player.gx;
                    const ry = oy - player.gy;
                    const fwd = (rx * cosYaw) + (ry * sinYaw);
                    const right = (-rx * sinYaw) + (ry * cosYaw);

                    if (fwd < 0.22) return null;
                    const fovScale = fov / fwd;
                    return {
                        x: (w / 2) + (right * fovScale),
                        y: effHorizonY - ((oz - 1.25) * fovScale),
                        scale: fovScale,
                        fwd: fwd
                    };
                }

                // Duvar Segmentini Near-Plane (0.22) ile Kırp ve Ekrana Projeksiyonunu Al
                function clipAndProjectWall(wx1, wy1, wx2, wy2, wallH) {
                    const rx1 = wx1 - player.gx;
                    const ry1 = wy1 - player.gy;
                    let fwd1 = rx1 * cosYaw + ry1 * sinYaw;
                    let right1 = -rx1 * sinYaw + ry1 * cosYaw;

                    const rx2 = wx2 - player.gx;
                    const ry2 = wy2 - player.gy;
                    let fwd2 = rx2 * cosYaw + ry2 * sinYaw;
                    let right2 = -rx2 * sinYaw + ry2 * cosYaw;

                    const near = 0.22;
                    if (fwd1 < near && fwd2 < near) return null;

                    if (fwd1 < near) {
                        const t = (near - fwd1) / (fwd2 - fwd1);
                        right1 = right1 + t * (right2 - right1);
                        fwd1 = near;
                    }
                    if (fwd2 < near) {
                        const t = (near - fwd2) / (fwd1 - fwd2);
                        right2 = right2 + t * (right1 - right2);
                        fwd2 = near;
                    }

                    const fovS1 = fov / fwd1;
                    const sx1 = (w / 2) + right1 * fovS1;
                    const sy1_bot = effHorizonY - (-1.25 * fovS1);
                    const sy1_top = effHorizonY - ((wallH - 1.25) * fovS1);

                    const fovS2 = fov / fwd2;
                    const sx2 = (w / 2) + right2 * fovS2;
                    const sy2_bot = effHorizonY - (-1.25 * fovS2);
                    const sy2_top = effHorizonY - ((wallH - 1.25) * fovS2);

                    return {
                        x1: sx1, y1_top: sy1_top, y1_bot: sy1_bot,
                        x2: sx2, y2_top: sy2_top, y2_bot: sy2_bot,
                        avgFwd: (fwd1 + fwd2) / 2
                    };
                }

                // 1. Dış Çevre Duvarları (Sahne Arka Planı ve Oda Kabuğu Olarak İlk Çizilir)
                const outerWallDefs = [
                    { x1: 0.8, y1: 0.8, x2: 10.2, y2: 0.8, h: 2.7, label: "🏢 PHISHAWARE KURUMSAL GÜVENLİK YÖNETİMİ" },
                    { x1: 0.8, y1: 10.2, x2: 10.2, y2: 10.2, h: 2.7, label: "🏢 MERKEZ GİRİŞ & RESEPSİYON HATTI" },
                    { x1: 0.8, y1: 0.8, x2: 0.8, y2: 10.2, h: 2.7, label: "🛡️ DENETİM VE RİSK YÖNETİMİ KANADI" },
                    { x1: 10.2, y1: 0.8, x2: 10.2, y2: 10.2, h: 2.7, label: "🖥️ SUNUCU VE ALTYAPI OPERASYON HATTI" }
                ];

                function drawWallPolygon(wp, isOuter, label) {
                    const wallFill = isOuter ? "#111827" : "#1e293b";
                    const wallBorder = isOuter ? "#1f2937" : "#38bdf8";

                    ctx.fillStyle = wallFill;
                    ctx.beginPath();
                    ctx.moveTo(wp.x1, wp.y1_top);
                    ctx.lineTo(wp.x2, wp.y2_top);
                    ctx.lineTo(wp.x2, wp.y2_bot);
                    ctx.lineTo(wp.x1, wp.y1_bot);
                    ctx.closePath();
                    ctx.fill();

                    ctx.strokeStyle = wallBorder;
                    ctx.lineWidth = isOuter ? 1.5 : 2.0;
                    ctx.stroke();

                    // Zemin Süpürgeliği (Alt %12 - Duvarın Zemine Oturduğunu Belirginleştirir)
                    const h1 = wp.y1_bot - wp.y1_top;
                    const h2 = wp.y2_bot - wp.y2_top;
                    ctx.fillStyle = "#090d16";
                    ctx.beginPath();
                    ctx.moveTo(wp.x1, wp.y1_bot - h1 * 0.12);
                    ctx.lineTo(wp.x2, wp.y2_bot - h2 * 0.12);
                    ctx.lineTo(wp.x2, wp.y2_bot);
                    ctx.lineTo(wp.x1, wp.y1_bot);
                    ctx.closePath();
                    ctx.fill();

                    // Tavan Kornişi (Üst %8)
                    ctx.fillStyle = "#0f172a";
                    ctx.beginPath();
                    ctx.moveTo(wp.x1, wp.y1_top);
                    ctx.lineTo(wp.x2, wp.y2_top);
                    ctx.lineTo(wp.x2, wp.y2_top + h2 * 0.08);
                    ctx.lineTo(wp.x1, wp.y1_top + h1 * 0.08);
                    ctx.closePath();
                    ctx.fill();

                    // Orta Mimari Şerit / Akustik Panel Çizgisi
                    ctx.fillStyle = isOuter ? "rgba(255,255,255,0.04)" : "rgba(56, 189, 248, 0.12)";
                    ctx.beginPath();
                    ctx.moveTo(wp.x1, wp.y1_top + h1 * 0.44);
                    ctx.lineTo(wp.x2, wp.y2_top + h2 * 0.44);
                    ctx.lineTo(wp.x2, wp.y2_top + h2 * 0.54);
                    ctx.lineTo(wp.x1, wp.y1_top + h1 * 0.54);
                    ctx.closePath();
                    ctx.fill();

                    ctx.strokeStyle = defIsOuterBorder(isOuter);
                    ctx.lineWidth = 1.2;
                    ctx.beginPath();
                    ctx.moveTo(wp.x1, wp.y1_top + h1 * 0.44);
                    ctx.lineTo(wp.x2, wp.y2_top + h2 * 0.44);
                    ctx.moveTo(wp.x1, wp.y1_top + h1 * 0.54);
                    ctx.lineTo(wp.x2, wp.y2_top + h2 * 0.54);
                    ctx.stroke();

                    // Duvar Üstü Kurumsal Departman Tabelası
                    if (label && wp.avgFwd < 7.5) {
                        const midX = (wp.x1 + wp.x2) / 2;
                        const midY = (wp.y1_top + wp.y2_top) / 2 + (h1 + h2) * 0.12;
                        if (midX > 60 && midX < w - 60) {
                            const scaleF = Math.min(1.2, Math.max(0.4, 2.5 / wp.avgFwd));
                            const badgeW = 240 * scaleF;
                            const badgeH = 28 * scaleF;

                            ctx.fillStyle = "rgba(4, 7, 14, 0.94)";
                            ctx.strokeStyle = "#38bdf8";
                            ctx.lineWidth = 1.4;
                            ctx.beginPath();
                            ctx.roundRect(midX - badgeW / 2, midY - badgeH / 2, badgeW, badgeH, 6);
                            ctx.fill();
                            ctx.stroke();

                            ctx.fillStyle = "#f8fafc";
                            ctx.font = `bold ${Math.max(10, Math.floor(12 * scaleF))}px sans-serif`;
                            ctx.textAlign = "center";
                            ctx.fillText(label, midX, midY + 4 * scaleF);
                        }
                    }
                }

                function defIsOuterBorder(isOuter) {
                    return isOuter ? "rgba(255,255,255,0.12)" : "rgba(56, 189, 248, 0.45)";
                }

                // Dış Duvarları Önce Çiz (Böylece Asla Masaların Üzerine Binmez)
                outerWallDefs.forEach(def => {
                    const wp = clipAndProjectWall(def.x1, def.y1, def.x2, def.y2, def.h);
                    if (wp) {
                        drawWallPolygon(wp, true, def.label);
                    }
                });

                // 2. İç Mimari Bölme Duvarları (Odalar Arası Bölmeler)
                const interiorWallDefs = [
                    // Dikey SOC Duvarı (x=5.8, y:0.8..5.6 - Kapı: 1.9..3.7)
                    { x1: 5.8, y1: 0.8, x2: 5.8, y2: 1.9, h: 2.5, label: "🛡️ BİLGİ İŞLEM & SOC MERKEZİ" },
                    { x1: 5.8, y1: 3.7, x2: 5.8, y2: 5.6, h: 2.5, label: null },

                    // Yatay Finans Duvarı (y=5.6, x:0.8..5.8 - Kapı: 1.9..3.7)
                    { x1: 0.8, y1: 5.6, x2: 1.9, y2: 5.6, h: 2.5, label: "📊 MUHASEBE & FİNANS İSTASYONU" },
                    { x1: 3.7, y1: 5.6, x2: 5.8, y2: 5.6, h: 2.5, label: null },

                    // Dikey İK Duvarı (x=5.8, y:5.6..10.2 - Kapı: 7.1..8.9)
                    { x1: 5.8, y1: 5.6, x2: 5.8, y2: 7.1, h: 2.5, label: "👥 İNSAN KAYNAKLARI KANADI" },
                    { x1: 5.8, y1: 8.9, x2: 5.8, y2: 10.2, h: 2.5, label: null }
                ];

                // İç Mimari Öğeler İçin Derinlik Sıralama Kuyruğu (Painters Algorithm)
                const renderQueue = [];

                // İç Duvarları Projelendir
                interiorWallDefs.forEach(def => {
                    const wp = clipAndProjectWall(def.x1, def.y1, def.x2, def.y2, def.h);
                    if (wp) {
                        const midX = (def.x1 + def.x2) / 2;
                        const midY = (def.y1 + def.y2) / 2;
                        const depth = (midX - player.gx) * cosYaw + (midY - player.gy) * sinYaw;
                        renderQueue.push({
                            type: 'wall',
                            depth: depth > 0.1 ? depth : wp.avgFwd,
                            data: wp,
                            def: def
                        });
                    }
                });

                // Masaları Projelendir
                terminals.forEach(t => {
                    const p = projectPoint(t.gx + 0.8, t.gy + 0.8, 0.85);
                    if (p) {
                        renderQueue.push({
                            type: 'terminal',
                            depth: p.fwd,
                            proj: p,
                            t: t
                        });
                    }
                });

                // Otomatik Kapıları Projelendir (Yere Basan Çerçeve & Kanatlar)
                doors.forEach(d => {
                    const pBot = projectPoint(d.gx, d.gy, 0.0);
                    const pTop = projectPoint(d.gx, d.gy, 2.4);
                    if (pBot && pTop) {
                        renderQueue.push({
                            type: 'door',
                            depth: pBot.fwd,
                            pBot: pBot,
                            pTop: pTop,
                            door: d
                        });
                    }
                });

                // Arkadan Öne Doğru Sırala (En uzaktaki önce çizilir)
                renderQueue.sort((a, b) => b.depth - a.depth);

                // 3. SAHNEYİ DERİNLİK SIRASINA GÖRE ÇİZ (OPAQUE & SOLID)
                renderQueue.forEach(item => {
                    if (item.type === 'wall') {
                        drawWallPolygon(item.data, false, item.def.label);
                    } else if (item.type === 'door') {
                        const pBot = item.pBot;
                        const pTop = item.pTop;
                        const d = item.door;

                        const doorH = Math.max(10, pBot.y - pTop.y);
                        const doorW = Math.max(10, 1.8 * (fov / pBot.fwd));
                        const openOffset = (d.openAmount * doorW * 0.42);

                        // 1. Zemin Eşiği (Zemine Tam Oturur)
                        ctx.fillStyle = "#1e293b";
                        ctx.fillRect(pBot.x - doorW / 2 - 4, pBot.y - 3, doorW + 8, 6);

                        // 2. Sol ve Sağ Kapı Kasası Direkleri (Zeminden Tavana Kadar Kesintisiz)
                        ctx.fillStyle = "#334155";
                        ctx.fillRect(pBot.x - doorW / 2 - 5, pTop.y, 6, doorH);
                        ctx.fillRect(pBot.x + doorW / 2 - 1, pTop.y, 6, doorH);

                        // 3. Üst Kasa & LED Sensör Göstergesi
                        const isOpen = d.openAmount > 0.35;
                        ctx.fillStyle = "#0f172a";
                        ctx.fillRect(pBot.x - doorW / 2, pTop.y - 8, doorW, 8);
                        ctx.fillStyle = isOpen ? "#10b981" : "#0284c7";
                        ctx.fillRect(pBot.x - doorW / 2 + 6, pTop.y - 6, doorW - 12, 4);

                        // 4. Sürgülü Güvenlik Camı Kanatları (Yere Basan ve Yatay Açılan Buzlu Cam)
                        const leafW = doorW * 0.48;
                        ctx.fillStyle = "rgba(56, 189, 248, 0.22)";
                        ctx.strokeStyle = isOpen ? "#34d399" : "#38bdf8";
                        ctx.lineWidth = 1.5;

                        // Sol Kanat
                        const leftX = pBot.x - doorW / 2 - openOffset;
                        ctx.fillRect(leftX, pTop.y + 4, leafW, doorH - 4);
                        ctx.strokeRect(leftX, pTop.y + 4, leafW, doorH - 4);

                        // Sağ Kanat
                        const rightX = pBot.x + openOffset;
                        ctx.fillRect(rightX, pTop.y + 4, leafW, doorH - 4);
                        ctx.strokeRect(rightX, pTop.y + 4, leafW, doorH - 4);
                    } else if (item.type === 'terminal') {
                        const t = item.t;
                        const p = item.proj;
                        const isTarget = !t.completed;
                        const isNear = (activeTerminal === t);

                        const deskW = 180 * (p.scale / 130);
                        const deskH = 65 * (p.scale / 130);

                        // Hedef Masa Vurgusu (Tavandan İnen Volumetrik Işık Sütunu)
                        if (isTarget) {
                            const coneGrad = ctx.createLinearGradient(p.x, 0, p.x, p.y);
                            coneGrad.addColorStop(0, "rgba(56, 189, 248, 0.0)");
                            coneGrad.addColorStop(0.3, "rgba(56, 189, 248, 0.08)");
                            coneGrad.addColorStop(1, "rgba(56, 189, 248, 0.35)");
                            ctx.fillStyle = coneGrad;
                            ctx.beginPath();
                            ctx.moveTo(p.x - 18, 0);
                            ctx.lineTo(p.x + 18, 0);
                            ctx.lineTo(p.x + deskW * 0.8, p.y + deskH * 0.5);
                            ctx.lineTo(p.x - deskW * 0.8, p.y + deskH * 0.5);
                            ctx.closePath();
                            ctx.fill();

                            // 3D Dönen Waypoint Beacon
                            const beaconY = p.y - deskH - 35 * (p.scale / 130);
                            const diamondSize = 14 * (p.scale / 130);

                            ctx.strokeStyle = "#38bdf8";
                            ctx.lineWidth = 2.2;
                            ctx.beginPath();
                            ctx.moveTo(p.x, beaconY - diamondSize);
                            ctx.lineTo(p.x + diamondSize, beaconY);
                            ctx.lineTo(p.x, beaconY + diamondSize);
                            ctx.lineTo(p.x - diamondSize, beaconY);
                            ctx.closePath();
                            ctx.stroke();

                            ctx.fillStyle = "#ffffff";
                            ctx.font = `bold ${Math.max(10, 13 * (p.scale / 130))}px sans-serif`;
                            ctx.textAlign = "center";
                            ctx.fillText(`[ 🎯 ${t.deptName.toUpperCase()} | ${p.fwd.toFixed(1)}m ]`, p.x, beaconY - diamondSize - 6);
                        }

                        // Masa Gövdesi (Açık İskandinav Meşesi / Aydınlatılmış Beyaz)
                        const deskColor = isTarget ? (isNear ? "#f8fafc" : "#e2e8f0") : "#1e293b";
                        const deskSide = isTarget ? "#cbd5e1" : "#0f172a";

                        ctx.fillStyle = deskSide;
                        ctx.fillRect(p.x - deskW / 2, p.y, deskW, deskH);

                        ctx.fillStyle = deskColor;
                        ctx.beginPath();
                        ctx.moveTo(p.x - deskW / 2, p.y);
                        ctx.lineTo(p.x - deskW * 0.44, p.y - deskH * 0.35);
                        ctx.lineTo(p.x + deskW * 0.44, p.y - deskH * 0.35);
                        ctx.lineTo(p.x + deskW / 2, p.y);
                        ctx.closePath();
                        ctx.fill();

                        ctx.strokeStyle = isTarget ? "#38bdf8" : "rgba(255,255,255,0.15)";
                        ctx.lineWidth = isTarget ? 2 : 1;
                        ctx.stroke();

                        // Kavisli OLED Ekran
                        const monW = deskW * 0.52;
                        const monH = deskH * 0.65;
                        const monX = p.x - monW / 2;
                        const monY = p.y - deskH * 0.35 - monH;

                        ctx.fillStyle = "#03060f";
                        ctx.fillRect(monX, monY, monW, monH);
                        ctx.strokeStyle = isTarget ? (isNear ? "#38bdf8" : t.color) : "#10b981";
                        ctx.lineWidth = 1.8;
                        ctx.strokeRect(monX, monY, monW, monH);

                        ctx.fillStyle = isTarget ? (isNear ? "#38bdf8" : t.color) : "#10b981";
                        ctx.font = `bold ${Math.max(8, 10 * (p.scale / 130))}px monospace`;
                        ctx.textAlign = "center";
                        ctx.fillText(isTarget ? "İNCELEME BEKLİYOR" : "✓ GÜVENLİ", p.x, monY + monH * 0.58);

                        ctx.fillStyle = isTarget ? "#f8fafc" : "#94a3b8";
                        ctx.font = `bold ${Math.max(9, 11 * (p.scale / 130))}px sans-serif`;
                        ctx.textAlign = "center";
                        ctx.fillText(`${t.icon} ${t.name}`, p.x, p.y + deskH + 15);

                        if (isNear && isTarget) {
                            ctx.fillStyle = "#38bdf8";
                            ctx.font = "bold 13px sans-serif";
                            ctx.fillText("⚡ [ E ] TUŞUNA BASIP İNCELE", p.x, monY - 14);
                        }
                    }
                });

                // 4. CYBERPUNK HUD OVERLAY (Taktiksel Arayüz)
                const compW = 320;
                const compH = 26;
                const compX = (w - compW) / 2;
                const compY = 12;

                ctx.fillStyle = "rgba(6, 10, 18, 0.88)";
                ctx.strokeStyle = "rgba(56, 189, 248, 0.35)";
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.roundRect(compX, compY, compW, compH, 8);
                ctx.fill();
                ctx.stroke();

                const deg = Math.round(((player.yaw * 180 / Math.PI) % 360 + 360) % 360);
                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 11px monospace";
                ctx.textAlign = "center";
                let dirName = "KUZEY";
                if (deg >= 45 && deg < 135) dirName = "DOĞU";
                else if (deg >= 135 && deg < 225) dirName = "GÜNEY";
                else if (deg >= 225 && deg < 315) dirName = "BATI";
                ctx.fillText(`⌖ YÖN: ${deg}° [ ${dirName} ] &bull; ${currentZoneName}`, w / 2, compY + 17);

                // Ekran Ortası Nişangah
                const chSize = player.isMoving ? 14 : 9;
                ctx.strokeStyle = activeTerminal ? "#38bdf8" : "rgba(255, 255, 255, 0.4)";
                ctx.lineWidth = 1.5;

                ctx.beginPath();
                ctx.moveTo(w / 2 - chSize - 4, effHorizonY); ctx.lineTo(w / 2 - 4, effHorizonY);
                ctx.moveTo(w / 2 + 4, effHorizonY); ctx.lineTo(w / 2 + chSize + 4, effHorizonY);
                ctx.moveTo(w / 2, effHorizonY - chSize - 4); ctx.lineTo(w / 2, effHorizonY - 4);
                ctx.moveTo(w / 2, effHorizonY + 4); ctx.lineTo(w / 2, effHorizonY + chSize + 4);
                ctx.stroke();

                if (activeTerminal && !activeTerminal.completed) {
                    ctx.strokeStyle = "#38bdf8";
                    ctx.strokeRect(w / 2 - 16, effHorizonY - 16, 32, 32);
                }

                // 5. OPERATÖRÜN ELİNDEKİ TAKTİKSEL SİBER TABLET (Cyberdeck Handheld PDA)
                const pdaW = 380;
                const pdaH = 145;
                const pdaX = (w - pdaW) / 2;
                const pdaY = h - pdaH + 18 + headBob;

                // Taktik Karbonfiber Eldivenli Eller
                ctx.fillStyle = "#0c101a";
                ctx.beginPath();
                ctx.ellipse(pdaX - 18, h + 22 + headBob, 58, 80, -0.22, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(pdaX + pdaW + 18, h + 22 + headBob, 58, 80, 0.22, 0, Math.PI * 2);
                ctx.fill();

                // Cyberdeck Çerçevesi
                ctx.fillStyle = "#070b14";
                ctx.beginPath();
                ctx.roundRect(pdaX, pdaY, pdaW, pdaH, 18);
                ctx.fill();
                ctx.strokeStyle = "rgba(56, 189, 248, 0.6)";
                ctx.lineWidth = 1.8;
                ctx.stroke();

                ctx.fillStyle = "#020409";
                ctx.beginPath();
                ctx.roundRect(pdaX + 12, pdaY + 12, pdaW - 24, pdaH - 24, 10);
                ctx.fill();

                // Canlı Ses / Frekans Spektrumu Dalgası
                ctx.strokeStyle = "rgba(56, 189, 248, 0.35)";
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                for (let x = 0; x < 90; x += 6) {
                    const waveH = Math.sin(time * 6 + x * 0.2) * 6;
                    ctx.moveTo(pdaX + pdaW - 110 + x, pdaY + 34 - waveH);
                    ctx.lineTo(pdaX + pdaW - 110 + x, pdaY + 34 + waveH);
                }
                ctx.stroke();

                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 11px monospace";
                ctx.textAlign = "left";
                ctx.fillText("📡 CYBER-DECK v4.3 [GÜVENLİK AKIŞI]", pdaX + 24, pdaY + 34);

                ctx.fillStyle = "#cbd5e1";
                ctx.font = "10.5px sans-serif";
                ctx.fillText(`📍 Mevcut Alan: ${currentZoneName}`, pdaX + 24, pdaY + 54);

                let nearest = null;
                let minDist = 999;
                terminals.forEach(t => {
                    if (!t.completed) {
                        const d = Math.hypot(player.gx - (t.gx + 0.8), player.gy - (t.gy + 0.8));
                        if (d < minDist) { minDist = d; nearest = t; }
                    }
                });

                if (nearest) {
                    ctx.fillStyle = "#f59e0b";
                    ctx.font = "bold 11px sans-serif";
                    ctx.fillText(`🎯 Sıradaki Açık Masa: ${nearest.deptName} (${minDist.toFixed(1)}m)`, pdaX + 24, pdaY + 74);
                } else {
                    ctx.fillStyle = "#10b981";
                    ctx.font = "bold 11px sans-serif";
                    ctx.fillText("🏆 Tüm Masalar Başarıyla Denetlendi!", pdaX + 24, pdaY + 74);
                }

                ctx.fillStyle = "#64748b";
                ctx.font = "10px sans-serif";
                ctx.fillText("🎮 İncelemek için masanın önüne gidip [ E ] tuşuna basınız", pdaX + 24, pdaY + 98);
            }

            // 3D TAKTİKSEL İZOMETRİK ÇİZİM MOTORU (Gerektiğinde V Tuşu ile Geçilebilir)
            function drawIsometricView(w, h, time) {
                const bgGrad = ctx.createRadialGradient(w / 2, h / 2, 60, w / 2, h / 2, w * 0.75);
                bgGrad.addColorStop(0, "#080c14");
                bgGrad.addColorStop(1, "#020306");
                ctx.fillStyle = bgGrad;
                ctx.fillRect(0, 0, w, h);

                drawIsoBlock(0, 0, -8, 11, 11, 8, "#090d16", "#040711", "#060911");

                // Zemin Izgarası
                for (let x = 0; x < 11; x++) {
                    for (let y = 0; y < 11; y++) {
                        const p1 = toScreen(x, y, 0);
                        const p2 = toScreen(x + 1, y, 0);
                        const p3 = toScreen(x + 1, y + 1, 0);
                        const p4 = toScreen(x, y + 1, 0);

                        let woodTone = ((x + y) % 2 === 0) ? "#1a1614" : "#14110f";
                        if (x >= 6 && y <= 5) {
                            woodTone = ((x + y) % 2 === 0) ? "#0c121e" : "#080e18";
                        }

                        ctx.fillStyle = woodTone;
                        ctx.beginPath();
                        ctx.moveTo(p1.x, p1.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.lineTo(p3.x, p3.y);
                        ctx.lineTo(p4.x, p4.y);
                        ctx.closePath();
                        ctx.fill();

                        ctx.strokeStyle = "rgba(255,255,255,0.035)";
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    }
                }

                // Dış Duvarlar
                drawIsoBlock(0, 0, 0, 0.35, 11, 54, "#111827", "#0a0f1d", "#161f33");
                drawIsoBlock(0, 0, 0, 11, 0.35, 54, "#141c2e", "#0d1322", "#18233a");

                // İç Bölme Duvarları (Solid & Belirgin Paneller)
                drawIsoBlock(5.8, 0.35, 0, 0.2, 1.6, 38, "#1e293b", "#0f172a", "#334155");
                drawIsoBlock(5.8, 3.7, 0, 0.2, 1.9, 38, "#1e293b", "#0f172a", "#334155");
                drawIsoBlock(0.35, 5.6, 0, 1.6, 0.2, 38, "#1e293b", "#0f172a", "#334155");
                drawIsoBlock(3.7, 5.6, 0, 1.9, 0.2, 38, "#1e293b", "#0f172a", "#334155");

                // Kapılar
                doors.forEach(d => {
                    const openShift = d.openAmount * 0.48;
                    if (d.axis === 'y') {
                        drawIsoBlock(d.gx, d.gy - openShift, 0, 0.1, 0.6, 38, "rgba(56,189,248,0.35)", "#0f172a", "#1e293b");
                        drawIsoBlock(d.gx, d.gy + 0.6 + openShift, 0, 0.1, 0.6, 38, "rgba(56,189,248,0.35)", "#0f172a", "#1e293b");
                    } else {
                        drawIsoBlock(d.gx - openShift, d.gy, 0, 0.6, 0.1, 38, "rgba(56,189,248,0.35)", "#0f172a", "#1e293b");
                        drawIsoBlock(d.gx + 0.6 + openShift, d.gy, 0, 0.6, 0.1, 38, "rgba(56,189,248,0.35)", "#0f172a", "#1e293b");
                    }
                });

                // Koltuklar
                drawOfficeChair(3.6, 3.6, 'north');
                drawOfficeChair(3.4, 9.1, 'north');
                drawOfficeChair(8.6, 4.0, 'north');

                // Masalar (Hedef Masalar Açık Renkli)
                terminals.forEach((t) => {
                    const isNear = (activeTerminal === t);
                    const isTarget = !t.completed;
                    const topC = isTarget ? (isNear ? "#f8fafc" : "#e2e8f0") : "#1e293b";
                    const sideC = isTarget ? "#cbd5e1" : "#0f172a";

                    drawIsoBlock(t.gx, t.gy, 0, 1.7, 1.4, 18, topC, sideC, "#111827", isTarget ? "#38bdf8" : "rgba(255,255,255,0.06)");
                    drawIsoBlock(t.gx + 0.25, t.gy + 0.35, 18.2, 1.2, 0.7, 0.5, "#090d16", "#040711", "#080b12");

                    const monCol = isTarget ? (isNear ? "#38bdf8" : t.color) : "#10b981";
                    drawIsoBlock(t.gx + 0.18, t.gy + 0.25, 18.5, 0.68, 0.25, 13, "#090d16", "#040711", monCol);
                    drawIsoBlock(t.gx + 0.88, t.gy + 0.25, 18.5, 0.68, 0.25, 13, "#090d16", "#040711", monCol);

                    const holoPos = toScreen(t.gx + 0.85, t.gy + 0.7, 34);
                    if (isTarget) {
                        ctx.fillStyle = "#38bdf8";
                        ctx.font = "bold 11px sans-serif";
                        ctx.textAlign = "center";
                        ctx.fillText(`⚡ [E] ${t.deptName}`, holoPos.x, holoPos.y - 5);
                    } else {
                        ctx.fillStyle = "#10b981";
                        ctx.font = "bold 10px sans-serif";
                        ctx.textAlign = "center";
                        ctx.fillText("✓ GÜVENLİ", holoPos.x, holoPos.y);
                    }
                });

                const ps = toScreen(player.gx, player.gy, 0);
                drawRealisticHumanAvatar(ps.x, ps.y, player.facing, player.stepCycle, player.isMoving, time);
            }

            // Ana Çizim Yönlendirici
            function draw(time) {
                const w = canvas.width / dpr;
                const h = canvas.height / dpr;
                ctx.clearRect(0, 0, w, h);

                if (cameraMode === 'first_person') {
                    drawFirstPersonView(w, h, time);
                } else {
                    drawIsometricView(w, h, time);
                }

                // Sağ Üst Minimalist Radar
                const mmW = 86;
                const mmH = 86;
                const mmX = w - mmW - 14;
                const mmY = 14;

                ctx.fillStyle = "rgba(6, 10, 18, 0.9)";
                ctx.strokeStyle = "rgba(56, 189, 248, 0.4)";
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.roundRect(mmX, mmY, mmW, mmH, 8);
                ctx.fill();
                ctx.stroke();

                terminals.forEach((t) => {
                    const tx = mmX + 8 + (t.gx / 11) * (mmW - 16);
                    const ty = mmY + 8 + (t.gy / 11) * (mmH - 16);
                    ctx.fillStyle = t.completed ? "#10b981" : "#f59e0b";
                    ctx.beginPath();
                    ctx.arc(tx, ty, 3.2, 0, Math.PI * 2);
                    ctx.fill();
                });

                const pmx = mmX + 8 + (player.gx / 11) * (mmW - 16);
                const pmy = mmY + 8 + (player.gy / 11) * (mmH - 16);
                ctx.fillStyle = "#38bdf8";
                ctx.beginPath();
                ctx.arc(pmx, pmy, 3.8, 0, Math.PI * 2);
                ctx.fill();

                // Oyuncu Bakış Açısı Çizgisi
                ctx.strokeStyle = "#38bdf8";
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.moveTo(pmx, pmy);
                ctx.lineTo(pmx + Math.cos(player.yaw) * 8, pmy + Math.sin(player.yaw) * 8);
                ctx.stroke();
            }

            // Terminal İnceleme Modalı
            window.openActiveTerminal = function() {
                if (!activeTerminal || activeTerminal.completed) return;
                playBeep();
                const modal = document.getElementById('terminalModal');
                document.getElementById('termIcon').innerText = activeTerminal.icon;
                document.getElementById('termTitle').innerText = activeTerminal.name;
                document.getElementById('termSender').innerText = activeTerminal.sender;
                document.getElementById('termSubject').innerText = activeTerminal.subject;
                document.getElementById('termAttachment').innerText = activeTerminal.attachment;
                document.getElementById('termBody').innerText = activeTerminal.body;

                const fb = document.getElementById('termFeedback');
                fb.style.display = 'none';
                document.getElementById('termButtons').style.display = 'grid';

                modal.style.display = 'flex';
            };

            window.closeTerminalModal = function() {
                document.getElementById('terminalModal').style.display = 'none';
            };

            window.submitVerdict = function(userVerdictIsPhish) {
                if (!activeTerminal) return;
                const isCorrect = (userVerdictIsPhish === activeTerminal.isPhish);
                const fb = document.getElementById('termFeedback');
                const btnBox = document.getElementById('termButtons');

                btnBox.style.display = 'none';
                fb.style.display = 'block';

                if (isCorrect) {
                    playSuccessSound();
                    fb.style.background = 'rgba(16, 185, 129, 0.12)';
                    fb.style.border = '1px solid #10b981';
                    fb.style.color = '#a7f3d0';
                    fb.innerHTML = `
                        <div style="font-weight:800; font-size:13.5px; margin-bottom:6px;">🎯 DOĞRU TEŞHİS</div>
                        <div>${activeTerminal.explanation}</div>
                        <div style="margin-top:12px; text-align:right;">
                            <button onclick="confirmTerminalSuccess()" style="background:#10b981; color:#fff; border:none; padding:8px 16px; border-radius:6px; font-weight:700; cursor:pointer;">
                                Devam Et →
                            </button>
                        </div>
                    `;
                } else {
                    playWarningSound();
                    fb.style.background = 'rgba(239, 68, 68, 0.12)';
                    fb.style.border = '1px solid #ef4444';
                    fb.style.color = '#fca5a5';
                    fb.innerHTML = `
                        <div style="font-weight:800; font-size:13.5px; margin-bottom:6px;">⚠️ YANLIŞ DEĞERLENDİRME</div>
                        <div>${activeTerminal.explanation}</div>
                        <div style="margin-top:12px; text-align:right;">
                            <button onclick="confirmTerminalSuccess()" style="background:#ef4444; color:#fff; border:none; padding:8px 16px; border-radius:6px; font-weight:700; cursor:pointer;">
                                Anladım, Devam Et →
                            </button>
                        </div>
                    `;
                }
            };

            window.confirmTerminalSuccess = function() {
                if (!activeTerminal) return;
                activeTerminal.completed = true;
                completedCount++;
                document.getElementById('hudProgress').innerText = `${completedCount} / 3`;
                closeTerminalModal();

                if (completedCount >= 3) {
                    triggerVictory();
                }
            };

            function triggerVictory() {
                playSuccessSound();
                try {
                    fetch(`/egitim-tamamla/${trackingToken}`, { method: 'POST' });
                } catch (e) {}

                setTimeout(() => {
                    document.getElementById('victoryModal').style.display = 'flex';
                }, 600);
            }

            let lastFrameTime = performance.now();
            function loop(now) {
                const dt = Math.min((now - lastFrameTime) / 1000, 0.1);
                lastFrameTime = now;

                update(dt);
                draw(now / 1000);
                requestAnimationFrame(loop);
            }
            requestAnimationFrame((time) => {
                lastFrameTime = time;
                loop(time);
            });
        })();
        </script>
    </div>
    """
    return html_template.replace("{takip_kodu}", takip_kodu).replace("{calisan_adi}", calisan_adi).replace("{sirket_adi}", sirket_adi).replace("{departman_adi}", departman_adi)
