import random
import time

COUNTRIES = ["AR", "BR", "CL", "UY", "MX", "CO", "PE"]
PAYMENTS = ["card", "pix", "boleto", "transfer", "wallet"]
DEVICES = ["android", "ios", "web-desktop", "web-mobile"]

class TransactionGenerator:
    def __init__(self, seed: int = 13):
        random.seed(seed)

    def next(self) -> dict:
        amount = round(random.triangular(5, 600, 45), 2)
        is_new_device = random.random() < 0.18
        ip_risk = round(random.random(), 3)
        account_age_days = round(random.triangular(0, 3650, 400), 1)

        # Inyectar fraudes simulados
        if random.random() < 0.07:
            amount *= random.uniform(3, 9)
            is_new_device = True
            ip_risk = max(ip_risk, random.uniform(0.7, 0.99))
            account_age_days = max(0, account_age_days - random.uniform(100, 400))

        return {
            "user_id": f"user_{random.randint(1, 5000)}",
            "country": random.choice(COUNTRIES),
            "amount": float(amount),
            "payment_method": random.choice(PAYMENTS),
            "device": random.choice(DEVICES),
            "ip_risk": float(ip_risk),
            "account_age_days": float(account_age_days),
            "is_new_device": bool(is_new_device),
            "ts": time.time()
        }
