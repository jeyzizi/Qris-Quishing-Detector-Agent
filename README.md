# 🛡️ Q-Guard — AI Agent for Real-Time QRIS Quishing Detection

**Q-Guard** adalah sistem *AI Agent* otonom yang dirancang untuk mendeteksi penipuan QRIS Statis (Quishing / stiker QRIS ditimpa) secara *real-time* sebelum transaksi pembayaran diproses.

---

## 🚀 Fitur Utama

- **EMVCo Payload Parsing:** Dekonstruksi struktur data QRIS (Tag-Length-Value) untuk mengestrasi nama merchant, kota, dan ID acquirer secara instan.
- **Contextual NLP & OCR Matching:** Membandingkan teks hasil OCR pada banner/stiker lokasi (misal: Tempat Ibadah/Donasi) dengan kategori nama merchant resmi di payload QRIS.
- **Geofencing Cross-Check:** Memverifikasi kesesuaian antara koordinat GPS pengguna dengan lokasi kota terdaftar merchant QRIS.
- **Automated Risk Scoring & Decision:** Menghasilkan skor risiko (0–100) dan keputusan otomatis (`ALLOW`, `WARN`, `BLOCK`).

---

## 📁 Struktur Proyek

```text
AI HACKFEST/
├── data/
│   ├── case_blocked.json
│   ├── case_safe.json
│   ├── case_warning.json
│   ├── qris_agent_input_payload.json
│   └── qris_agent_output_payload.json
│
├── src/
│   ├── __init__.py
│   └── qris_agent.py
│
├── README.md
├── app.py
└── main.py
