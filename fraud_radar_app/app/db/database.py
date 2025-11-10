import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Base del proyecto: .../fraud_radar_app
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Asegurar que 'data' exista
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Ruta absoluta al archivo de base de datos
DB_PATH = os.path.join(DATA_DIR, "fraud.db")

# En Windows conviene normalizar a barras forward para SQLAlchemy
DB_URL = "sqlite:///" + DB_PATH.replace("\\", "/")

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from . import models  # noqa
    Base.metadata.create_all(bind=engine)
