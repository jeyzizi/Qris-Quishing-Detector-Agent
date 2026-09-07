from typing import List, Dict
from pydantic import BaseModel

class GPSLocation(BaseModel):
    latitude: float
    longitude: float
    city: str

class DeviceContext(BaseModel):
    user_id: str
    gps_location: GPSLocation
    ocr_detected_text: List[str]

class QRScanInput(BaseModel):
    transaction_id: str
    timestamp: str
    raw_emvco_payload: str
    device_context: DeviceContext

class AnomalyItem(BaseModel):
    code: str
    severity: str
    description: str

class AgentDecisionOutput(BaseModel):
    transaction_id: str
    agent_decision: str
    risk_score: int
    confidence_level: float
    anomalies_detected: List[AnomalyItem]
    user_message: str

class EMVCoParser:
    @staticmethod
    def parse(payload: str) -> Dict[str, str]:
        parsed_tags = {}
        # Cari Tag 59 (Nama Merchant) & Tag 60 (Kota) secara langsung jika parsing sekuensial terganggu
        import re
        
        # Standard TLV Parsing
        index = 0
        while index < len(payload):
            if index + 4 > len(payload):
                break
            tag = payload[index:index+2]
            length_str = payload[index+2:index+4]
            if not length_str.isdigit():
                index += 1
                continue
            length = int(length_str)
            val = payload[index+4:index+4+length]
            if val:
                parsed_tags[tag] = val
            index += 4 + length

        # Fallback Regex jika Tag 59 terlewat akibat nested payload
        if "59" not in parsed_tags or not parsed_tags["59"]:
            match_59 = re.search(r'59(\d{2})([A-Za-z0-9\s]+?)60', payload)
            if match_59:
                parsed_tags["59"] = match_59.group(2)

        return parsed_tags

class QGuardAgent:
    def evaluate(self, scan_data: QRScanInput) -> AgentDecisionOutput:
        parsed_qris = EMVCoParser.parse(scan_data.raw_emvco_payload)
        anomalies: List[AnomalyItem] = []
        base_risk_score = 0

        merchant_name = parsed_qris.get("59", "Merchant Tidak Terdefinisi").strip()
        registered_city = parsed_qris.get("60", "").strip()
        
        ocr_texts = [text.lower() for text in scan_data.device_context.ocr_detected_text]
        full_ocr_str = " ".join(ocr_texts)

        # 1. Cek Mismatch Kategori (OCR Tempat Ibadah vs Merchant Komersial)
        is_ocr_religious = any(k in full_ocr_str for k in ["masjid", "infaq", "musholla", "gereja", "donasi"])
        is_merchant_commercial = any(k in merchant_name.lower() for k in ["toko", "warung", "sembako", "pulsa", "pribadi"]) or ("masjid" not in merchant_name.lower())

        if is_ocr_religious and is_merchant_commercial:
            anomalies.append(AnomalyItem(
                code="CATEGORY_MISMATCH",
                severity="HIGH",
                description=f"Banner lokasi terdeteksi Tempat Ibadah/Donasi, tetapi QRIS terdaftar atas nama '{merchant_name}'."
            ))
            base_risk_score += 50

        # 2. Cek Geofencing Lokasi
        user_city = scan_data.device_context.gps_location.city.lower()
        if registered_city and registered_city.lower() not in user_city and user_city not in registered_city.lower():
            anomalies.append(AnomalyItem(
                code="LOCATION_MISMATCH",
                severity="MEDIUM",
                description=f"Kota terdaftar QRIS ({registered_city}) tidak sesuai lokasi GPS ({scan_data.device_context.gps_location.city})."
            ))
            base_risk_score += 35

        risk_score = min(base_risk_score, 100)
        
        if risk_score >= 70:
            decision = "BLOCK"
            message = "Transaksi Dihentikan! QRIS terindikasi palsu/ditimpa."
        elif risk_score >= 30:
            decision = "WARN"
            message = f"Perhatian: Nama merchant ({merchant_name}) mungkin tidak sesuai dengan lokasi."
        else:
            decision = "ALLOW"
            message = "QRIS Terverifikasi Aman."

        return AgentDecisionOutput(
            transaction_id=scan_data.transaction_id,
            agent_decision=decision,
            risk_score=risk_score,
            confidence_level=0.92,
            anomalies_detected=anomalies,
            user_message=message
        )