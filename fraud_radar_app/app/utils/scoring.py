import os
import pickle
from typing import Tuple, List
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "model.pkl")

CATS = {
    "country": ["AR", "BR", "CL", "UY", "MX", "CO", "PE"],
    "payment_method": ["card", "pix", "boleto", "transfer", "wallet"],
    "device": ["android", "ios", "web-desktop", "web-mobile"],
}

class RiskScorer:
    def __init__(self):
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
        else:
            self.model = None

    def _vectorize(self, tx: dict) -> np.ndarray:
        vec = [tx["amount"], tx["ip_risk"], tx["account_age_days"], 1.0 if tx["is_new_device"] else 0.0]
        for k, cats in CATS.items():
            for c in cats:
                vec.append(1.0 if tx[k] == c else 0.0)
        return np.array(vec).reshape(1, -1)

    def score(self, tx: dict) -> Tuple[float, str, List[str]]:
        v = self._vectorize(tx)
        if self.model is None:
            raw = 0.6 * (tx["ip_risk"]) + 0.4 * (1.0 if tx["is_new_device"] else 0.0)
            raw += 0.15 if tx["amount"] > 500 else 0.0
            risk = float(max(0.0, min(1.0, raw)))
        else:
            pred = self.model.decision_function(v)
            risk = float(1.0 - (pred - pred.min()) / (pred.max() - pred.min() + 1e-9))

        if risk >= 0.75:
            level = "HIGH"
        elif risk >= 0.45:
            level = "MEDIUM"
        else:
            level = "LOW"
        reasons = self._reasons(tx)
        return risk, level, reasons

    def _reasons(self, tx: dict) -> List[str]:
        reasons = []
        if tx["ip_risk"] > 0.7:
            reasons.append("IP con score de riesgo alto")
        if tx["is_new_device"]:
            reasons.append("Dispositivo no reconocido para el usuario")
        if tx["amount"] > 500:
            reasons.append("Monto elevado fuera del patrón")
        if tx["account_age_days"] < 30:
            reasons.append("Cuenta muy reciente")
        if tx["country"] in ("BR", "MX") and tx["payment_method"] in ("pix", "boleto", "transfer"):
            reasons.append("Combinación país+método con mayor tasa de fraude histórica (simulada)")
        if not reasons:
            reasons.append("Señales débiles acumuladas")
        return reasons

    def explain_reason(self, tx: dict) -> str:
        _, level, reasons = self.score(tx)
        return f"Nivel {level}. Motivos: " + "; ".join(reasons)
