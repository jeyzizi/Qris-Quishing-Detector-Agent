import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Import agent dan model dari struktur folder milikmu
from src.qris_agent import QGuardAgent, QRScanInput

app = FastAPI(title="AI GuardAgent API")

# =========================================================================
# 1. SETUP CORS (Mencegah Error 'blocked by CORS policy' di Browser)
# =========================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Mengizinkan frontend dari Netlify/Live Server
    allow_credentials=True,
    allow_methods=["*"],            # Mengizinkan HTTP POST, OPTIONS, GET
    allow_headers=["*"],
)

# Inisialisasi Agent sekali saat server nyala
agent = QGuardAgent()

# Schema request yang dikirimkan oleh index.html
class FrontendScanPayload(BaseModel):
    url: Optional[str] = ""
    dom_data: Dict[str, Any]
    page_text: Optional[str] = ""

@app.get("/")
def root():
    return {"status": "active", "message": "AI GuardAgent Backend Is Running!"}

@app.post("/scan")
async def scan_qris(payload: FrontendScanPayload):
    try:
        # 1. Ekstrak string QRIS dari payload frontend
        qr_payload_text = payload.dom_data.get("qrPayload", "")
        has_otp = payload.dom_data.get("hasOtpInput", False)
        has_pin = payload.dom_data.get("hasPinInput", False)

        # 2. Petakan ke Pydantic Model 'QRScanInput' milik QGuardAgent kamu
        # (Sesuaikan nama field di bawah jika QRScanInput kamu menggunakan nama atribut berbeda)
        scan_input = QRScanInput(
            qr_payload=qr_payload_text,
            url=payload.url,
            has_otp_input=has_otp,
            has_pin_input=has_pin,
            raw_dom=payload.dom_data
        )

        # 3. Panggil Agent & Evaluasi
        result = agent.evaluate(scan_input)

        # 4. Kembalikan hasil evaluasi ke Frontend
        # Jika result adalah Pydantic model, gunakan .model_dump()
        if hasattr(result, "model_dump"):
            return {"success": True, "financial_threat_analysis": result.model_dump()}
        return {"success": True, "financial_threat_analysis": result}

    except Exception as e:
        print(f"Error saat memproses scan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
