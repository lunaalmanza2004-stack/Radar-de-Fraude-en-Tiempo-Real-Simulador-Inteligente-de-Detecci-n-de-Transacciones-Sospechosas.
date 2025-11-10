import os
import pickle
import numpy as np
from sklearn.ensemble import IsolationForest

rng = np.random.default_rng(42)
N = 12000
amount = rng.gamma(shape=2.0, scale=40.0, size=N)
ip_risk = rng.uniform(0, 1, size=N)
account_age = rng.exponential(scale=300, size=N)
is_new_device = (rng.uniform(0, 1, size=N) < 0.18).astype(float)

def dummies(vals, cats):
    out = np.zeros((len(vals), len(cats)))
    m = {c:i for i,c in enumerate(cats)}
    for i,v in enumerate(vals):
        out[i, m[v]] = 1.0
    return out

countries = np.array(rng.choice(["AR","BR","CL","UY","MX","CO","PE"], size=N))
payments = np.array(rng.choice(["card","pix","boleto","transfer","wallet"], size=N))
devices = np.array(rng.choice(["android","ios","web-desktop","web-mobile"], size=N))

X = np.column_stack([amount, ip_risk, account_age, is_new_device,
                     dummies(countries, ["AR","BR","CL","UY","MX","CO","PE"]),
                     dummies(payments, ["card","pix","boleto","transfer","wallet"]),
                     dummies(devices, ["android","ios","web-desktop","web-mobile"])
                     ])

for i in rng.choice(N, size=int(N*0.07), replace=False):
    amount[i] *= rng.uniform(3, 9)
    ip_risk[i] = np.maximum(ip_risk[i], rng.uniform(0.7, 0.99))
    account_age[i] *= rng.uniform(0.01, 0.2)
    is_new_device[i] = 1.0
X = np.column_stack([amount, ip_risk, account_age, is_new_device,
                     dummies(countries, ["AR","BR","CL","UY","MX","CO","PE"]),
                     dummies(payments, ["card","pix","boleto","transfer","wallet"]),
                     dummies(devices, ["android","ios","web-desktop","web-mobile"])])

clf = IsolationForest(n_estimators=200, contamination=0.08, random_state=42)
clf.fit(X)

MODEL_DIR = os.path.dirname(__file__)
with open(os.path.join(MODEL_DIR, "model.pkl"), "wb") as f:
    pickle.dump(clf, f)

print("Modelo entrenado y guardado en app/ml/model.pkl")
