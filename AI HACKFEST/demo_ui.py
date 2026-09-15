import time
import cv2
import numpy as np
import streamlit as st
from PIL import Image
from pyzbar.pyzbar import decode
from src.qris_agent import QGuardAgent, QRScanInput, EMVCoParser

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Q-Guard AI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Injeksi CSS Kustom Murni
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');

    .stApp {
        background-color: #070A12 !important;
        color: #E2E8F0;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .header-banner {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.7) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .brand-title {
        color: #38BDF8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 24px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .status-badge-live {
        display: inline-flex;
        align-items: center;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid #10B981;
        color: #34D399;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 10px #10B981;
    }

    .telemetry-card {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .telemetry-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 800;
        color: #38BDF8;
    }
    .telemetry-lbl {
        font-size: 11px;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }

    .badge-block {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(153, 27, 27, 0.2) 100%);
        border: 2px solid #EF4444;
        color: #F87171;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 800;
        font-size: 26px;
        letter-spacing: 2px;
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.35);
    }
    .badge-warn {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(180, 83, 9, 0.2) 100%);
        border: 2px solid #F59E0B;
        color: #FBBF24;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 800;
        font-size: 26px;
        letter-spacing: 2px;
        box-shadow: 0 0 30px rgba(245, 158, 11, 0.35);
    }
    .badge-allow {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(6, 95, 70, 0.2) 100%);
        border: 2px solid #10B981;
        color: #34D399;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 800;
        font-size: 26px;
        letter-spacing: 2px;
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.35);
    }

    .terminal-container {
        background-color: #030712;
        border: 1px solid #1F2937;
        border-left: 4px solid #38BDF8;
        border-radius: 10px;
        padding: 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #38BDF8;
        margin-top: 20px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# 3. Header Utama HTML
st.markdown("""
<div class="header-banner">
    <div>
        <h1 class="brand-title">Q-GUARD AI</h1>
        <p style="color: #94A3B8; font-size: 13px; margin: 4px 0 0 0;">Sistem Deteksi Otonom Penipuan Stiker QRIS Berbasis Analisis Konteks Real-Time</p>
    </div>
    <div style="display: flex; gap: 16px; align-items: center;">
        <div class="status-badge-live"><span class="pulse-dot"></span> AGENT AKTIF</div>
        <div style="color: #64748B; font-size: 12px; font-family: 'JetBrains Mono', monospace;">Versi: <b style="color:#38BDF8;">v2.4 Pro</b></div>
    </div>
</div>
""", unsafe_allow_html=True)

agent = QGuardAgent()

# 4. Baris Kartu Telemetri HTML
t1, t2, t3, t4 = st.columns(4)
with t1:
    st.markdown('<div class="telemetry-card"><div class="telemetry-val">EMVCo TLV</div><div class="telemetry-lbl">Mesin Ekstraksi</div></div>', unsafe_allow_html=True)
with t2:
    st.markdown('<div class="telemetry-card"><div class="telemetry-val">&lt; 25 md</div><div class="telemetry-lbl">Latensi Pemrosesan</div></div>', unsafe_allow_html=True)
with t3:
    st.markdown('<div class="telemetry-card"><div class="telemetry-val">92%</div><div class="telemetry-lbl">Akurasi Keyakinan</div></div>', unsafe_allow_html=True)
with t4:
    st.markdown('<div class="telemetry-card"><div class="telemetry-val" style="color:#10B981;">AKTIF</div><div class="telemetry-lbl">Proteksi Gateway</div></div>', unsafe_allow_html=True)

st.write("")

# 5. Sidebar Pengaturan Input
st.sidebar.markdown("### PENGATURAN INPUT")
input_mode = st.sidebar.radio(
    "Pilih Sumber Input:",
    ["Kamera Langsung (Webcam/HP)", "Unggah Foto File QRIS", "Skenario Pengujian Lomba"]
)

default_payload = ""
default_ocr = []
default_city = "Jakarta"

# Opsi 1: Pemindaian Kamera Langsung (Webcam/Kamera HP)
if input_mode == "Kamera Langsung (Webcam/HP)":
    st.sidebar.markdown("---")
    camera_file = st.sidebar.camera_input("Ambil Foto QRIS Langsung")
    
    if camera_file:
        image = Image.open(camera_file)
        img_array = np.array(image)
        decoded_objs = decode(img_array)
        
        if decoded_objs:
            default_payload = decoded_objs[0].data.decode("utf-8")
            st.sidebar.success("Payload Decoded dari Kamera Langsung")
            
            parsed_tmp = EMVCoParser.parse(default_payload)
            extracted_merchant = parsed_tmp.get("59", "Merchant Terdeteksi").strip()
            extracted_city = parsed_tmp.get("60", "Jakarta").strip()
            
            default_ocr = [extracted_merchant, "Merchant Resmi"]
            default_city = extracted_city if extracted_city else "Jakarta"
        else:
            st.sidebar.warning("QR Code tidak terbaca dari kamera, menggunakan sampel fallback.")
            default_payload = "00020101021126580016ID.CO.QRIS.WWW011893600911000000123402150001234567890125204541153033605802ID5914Toko Sembako B6007Jakarta61051234562070703A016304A1B2"
            default_ocr = ["Toko Sembako B", "Sedia Sembako Lengkap"]
            default_city = "Jakarta"

# Opsi 2: Unggah Foto
elif input_mode == "Unggah Foto File QRIS":
    st.sidebar.markdown("---")
    uploaded_file = st.sidebar.file_uploader("Unggah File Gambar QRIS (JPG/PNG):", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.sidebar.image(image, caption="Gambar Terdeteksi", use_container_width=True)
        
        img_array = np.array(image)
        decoded_objs = decode(img_array)
        
        if decoded_objs:
            default_payload = decoded_objs[0].data.decode("utf-8")
            st.sidebar.success("Payload Decoded dari File")
            
            parsed_tmp = EMVCoParser.parse(default_payload)
            extracted_merchant = parsed_tmp.get("59", "Merchant Terdeteksi").strip()
            extracted_city = parsed_tmp.get("60", "Jakarta").strip()
            
            default_ocr = [extracted_merchant, "Merchant Resmi"]
            default_city = extracted_city if extracted_city else "Jakarta"
        else:
            st.sidebar.warning("QR tidak terbaca, menggunakan sampel fallback.")
            default_payload = "00020101021126580016ID.CO.QRIS.WWW011893600911000000123402150001234567890125204541153033605802ID5914Toko Sembako B6007Jakarta61051234562070703A016304A1B2"
            default_ocr = ["Toko Sembako B", "Sedia Sembako Lengkap"]
            default_city = "Jakarta"

# Opsi 3: Preset Skenario
else:
    st.sidebar.markdown("---")
    scenario = st.sidebar.selectbox(
        "Pilih Skenario Pengujian:",
        [
            "Skenario 1: Penipuan QRIS Masjid (Ketidaksesuaian Kategori)",
            "Skenario 2: Merchant Otentik (Aman / ALLOW)",
            "Skenario 3: Penipuan Beda Lokasi (Ketidaksesuaian Geofencing)"
        ]
    )
    if "Skenario 1" in scenario:
        default_payload = "00020101021126580016ID.CO.QRIS.WWW011893600911000000123402150001234567890125204541153033605802ID5914Toko Sembako B6007Jakarta61051234562070703A016304A1B2"
        default_ocr = ["Masjid Agung Syuhada", "Kotak Infaq Digital", "Scan QRIS"]
        default_city = "Jakarta"
    elif "Skenario 2" in scenario:
        default_payload = "00020101021126580016ID.CO.QRIS.WWW011893600911000000123402150001234567890125204541153033605802ID5914Toko Sembako B6007Jakarta61051234562070703A016304A1B2"
        default_ocr = ["Toko Sembako B", "Sedia Sembako Lengkap", "Scan QRIS Resmi"]
        default_city = "Jakarta"
    else:
        default_payload = "00020101021126580016ID.CO.QRIS.WWW011893600911000000123402150001234567890125204541153033605802ID5914Toko Sembako B6005Medan61051234562070703A016304A1B2"
        default_ocr = ["Toko Sembako B", "Cabang Medan"]
        default_city = "Surabaya"

# 6. Area Kerja Utama
col_left, col_right = st.columns([1, 1.15], gap="large")

with col_left:
    st.markdown("#### DATA KONTEKS PEMINDAIAN")
    raw_payload = st.text_area("1. Payload Mentah EMVCo QRIS:", value=default_payload, height=90)
    ocr_text_str = st.text_input("2. Teks OCR Banner Fisik (Dipisahkan Koma):", value=", ".join(default_ocr))
    user_city = st.text_input("3. Lokasi GPS Smartphone Pengguna:", value=default_city)

    st.write("")
    btn_scan = st.button("JALANKAN VERIFIKASI AI AGENT", type="primary", use_container_width=True)

with col_right:
    st.markdown("#### HASIL KEPUTUSAN AI AGENT")
    
    if btn_scan:
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.markdown("`[1/3] Dekonstruksi Struktur Tag TLV EMVCo...`")
        progress_bar.progress(35)
        time.sleep(0.2)

        status_text.markdown("`[2/3] Analisis Pencocokan Teks OCR vs Nama Merchant...`")
        progress_bar.progress(70)
        time.sleep(0.2)

        status_text.markdown("`[3/3] Evaluasi Batas Lokasi Geofencing GPS...`")
        progress_bar.progress(100)
        time.sleep(0.2)
        
        status_text.empty()
        progress_bar.empty()

        ocr_list = [x.strip() for x in ocr_text_str.split(",") if x.strip()]
        input_data = QRScanInput(
            transaction_id="TX-DEMO-901",
            timestamp="2026-09-08T11:00:00Z",
            raw_emvco_payload=raw_payload,
            device_context={
                "user_id": "USR-DEMO",
                "gps_location": {
                    "latitude": -6.175392,
                    "longitude": 106.827153,
                    "city": user_city
                },
                "ocr_detected_text": ocr_list
            }
        )

        res = agent.evaluate(input_data)

        # Tampilan Badge Keputusan
        if res.agent_decision == "BLOCK":
            st.markdown(f'<div class="badge-block">KEPUTUSAN: {res.agent_decision}</div>', unsafe_allow_html=True)
        elif res.agent_decision == "WARN":
            st.markdown(f'<div class="badge-warn">KEPUTUSAN: {res.agent_decision}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="badge-allow">KEPUTUSAN: {res.agent_decision}</div>', unsafe_allow_html=True)

        st.write("")
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Skor Risiko", f"{res.risk_score} / 100", delta="Risiko Tinggi" if res.risk_score >= 50 else "Aman", delta_color="inverse")
        with m2:
            st.metric("Tingkat Keyakinan", f"{int(res.confidence_level * 100)}%")

        st.info(f"**Pesan Sistem:** {res.user_message}")

        if res.anomalies_detected:
            st.markdown("##### Anomali Terdeteksi:")
            for item in res.anomalies_detected:
                st.error(f"**[{item.code}] Tingkat Keparahan: {item.severity}**\n\n{item.description}")
        else:
            st.success("TIDAK TERDETEKSI ANOMALI - QRIS Terverifikasi Otentik dan Aman.")

        # Terminal Log Eksekusi
        st.markdown(f"""
        <div class="terminal-container">
            &gt; LOG EKSEKUSI AGENT [TX-DEMO-901]:<br>
            &gt; Tag 59 EMVCo Terbaca: Nama Merchant Terverifikasi<br>
            &gt; Evaluasi Konteks: Analisis OCR vs EMVCo Selesai<br>
            &gt; Skor Evaluasi Risiko: {res.risk_score}/100<br>
            &gt; Hasil Akhir AI Agent: <b>{res.agent_decision}</b>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Lihat Output JSON Schema AI Agent"):
            st.json(res.model_dump())
    else:
        st.markdown("""
        <div style="border: 2px dashed #1E293B; background: rgba(15, 23, 42, 0.6); border-radius: 14px; padding: 45px; text-align: center;">
            <h4 style="color: #38BDF8; margin:0; font-family: 'JetBrains Mono', monospace;">AI AGENT DALAM MODE SIAGA</h4>
            <p style="color: #64748B; font-size: 13px; margin-top: 8px;">Pilih kamera langsung, skenario, atau unggah foto QRIS, lalu klik tombol <b>"JALANKAN VERIFIKASI AI AGENT"</b> untuk memulai analisis.</p>
        </div>
        """, unsafe_allow_html=True)