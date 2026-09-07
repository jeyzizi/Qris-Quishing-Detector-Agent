from fastapi import FastAPI
from src.qris_agent import QGuardAgent, QRScanInput, AgentDecisionOutput

app = FastAPI(title="Q-Guard AI Agent API")
agent = QGuardAgent()

@app.post("/api/v1/scan-qris", response_model=AgentDecisionOutput)
def analyze_qris(scan_data: QRScanInput):
    return agent.evaluate(scan_data)