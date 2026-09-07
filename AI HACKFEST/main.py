import json
from pathlib import Path
from src.qris_agent import QGuardAgent, QRScanInput

def main():
    # 1. Tentukan path file input
    json_path = Path("qris_agent_input_payload.json")
    
    if not json_path.exists():
        print(f"Error: File '{json_path}' tidak ditemukan!")
        return

    # 2. Baca file JSON
    with open(json_path, "r") as f:
        raw_data = json.load(f)

    # 3. Masukkan data ke Pydantic Model
    scan_input = QRScanInput(**raw_data)

    # 4. Panggil Agent & Evaluasi
    agent = QGuardAgent()
    result = agent.evaluate(scan_input)

    # 5. Cetak Hasil
    print("=" * 40)
    print(" HASIL EVALUASI Q-GUARD AI AGENT")
    print("=" * 40)
    print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    main()