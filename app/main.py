import asyncio
import json
import os
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .db.database import get_session, init_db
from .db.models import Transaction, Alert
from .utils.generator import TransactionGenerator
from .utils.scoring import RiskScorer

app = FastAPI(title="Radar de Fraude en Tiempo Real")
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

scorer = RiskScorer()
generator = TransactionGenerator()

class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, message: dict):
        living = []
        for ws in self.active:
            try:
                await ws.send_text(json.dumps(message))
                living.append(ws)
            except Exception:
                pass
        self.active = living

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    init_db()
    asyncio.create_task(simulation_loop())

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class Metrics(BaseModel):
    total: int
    alerts: int
    last_minute: int
    precision_est: float

@app.get("/api/metrics", response_model=Metrics)
async def metrics(session=Depends(get_session)):
    total = session.query(Transaction).count()
    alerts = session.query(Alert).count()
    one_min_ago = datetime.now(timezone.utc).timestamp() - 60
    last_minute = session.query(Transaction).filter(Transaction.ts >= one_min_ago).count()
    precision_est = 0.0
    if alerts > 0:
        highs = session.query(Alert).filter(Alert.level == "HIGH").count()
        precision_est = round(highs / alerts, 3)
    return Metrics(total=total, alerts=alerts, last_minute=last_minute, precision_est=precision_est)

@app.get("/api/transactions")
async def transactions(limit: int = 100, session=Depends(get_session)):
    rows = session.query(Transaction).order_by(Transaction.id.desc()).limit(limit).all()
    return [r.to_dict() for r in rows]

@app.get("/api/alerts")
async def alerts(limit: int = 100, session=Depends(get_session)):
    rows = session.query(Alert).order_by(Alert.id.desc()).limit(limit).all()
    return [r.to_dict() for r in rows]

@app.get("/api/explain/{tx_id}")
async def explain(tx_id: int, session=Depends(get_session)):
    tx = session.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        return {"ok": False, "message": "Transacción no encontrada"}
    explanation = scorer.explain_reason(tx.to_dict())
    return {"ok": True, "explanation": explanation}

@app.websocket("/ws/stream")
async def ws_stream(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def simulation_loop():
    # Genera transacciones, puntúa riesgo, persiste y emite por WebSocket.
    await asyncio.sleep(1.5)
    session = next(get_session())
    while True:
        tx = generator.next()
        risk, level, reasons = scorer.score(tx)
        t = Transaction.from_dict(tx, risk=risk, level=level)
        session.add(t)
        session.commit()
        if level != "LOW":
            alert = Alert(transaction_id=t.id, level=level, reasons=json.dumps(reasons), ts=t.ts)
            session.add(alert)
            session.commit()
        payload = {"type": "transaction", "data": t.to_dict(), "risk": risk, "level": level, "reasons": reasons}
        await manager.broadcast(payload)
        await asyncio.sleep(0.8)
