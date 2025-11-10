from sqlalchemy import Column, Integer, Float, String
from .database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    country = Column(String, index=True)
    amount = Column(Float)
    payment_method = Column(String)
    device = Column(String)
    ip_risk = Column(Float)
    account_age_days = Column(Float)
    is_new_device = Column(String)  # "Y"/"N"
    ts = Column(Float, index=True)  # epoch seconds
    risk = Column(Float)
    level = Column(String)  # LOW / MEDIUM / HIGH

    @staticmethod
    def from_dict(d: dict, risk: float, level: str):
        t = Transaction()
        t.user_id = d["user_id"]
        t.country = d["country"]
        t.amount = float(d["amount"])
        t.payment_method = d["payment_method"]
        t.device = d["device"]
        t.ip_risk = float(d["ip_risk"])
        t.account_age_days = float(d["account_age_days"])
        t.is_new_device = "Y" if d["is_new_device"] else "N"
        t.ts = float(d["ts"])
        t.risk = float(risk)
        t.level = level
        return t

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "country": self.country,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "device": self.device,
            "ip_risk": self.ip_risk,
            "account_age_days": self.account_age_days,
            "is_new_device": self.is_new_device == "Y",
            "ts": self.ts,
            "risk": self.risk,
            "level": self.level,
        }

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, index=True)
    level = Column(String, index=True)  # MEDIUM / HIGH
    reasons = Column(String)            # JSON list of strings
    ts = Column(Float, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "level": self.level,
            "reasons": self.reasons,
            "ts": self.ts,
        }
