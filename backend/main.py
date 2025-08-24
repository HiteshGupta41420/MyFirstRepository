import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Enum
from sqlalchemy.orm import sessionmaker, declarative_base
import enum

# ----- Environment -----
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "invoices")
DB_USER = os.getenv("DB_USER", "invoice_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "invoice_pass")

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class StatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    customer = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.PENDING, nullable=False)

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Invoice Backend", version="1.0.0")

class InvoiceIn(BaseModel):
    customer: str
    amount: float

# --- Simplified healthcheck (no DB dependency) ---
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/invoices")
def create_invoice(invoice: InvoiceIn):
    db = SessionLocal()
    try:
        inv = Invoice(customer=invoice.customer, amount=invoice.amount, status=StatusEnum.PENDING)
        db.add(inv)
        db.commit()
        db.refresh(inv)
        return {"id": inv.id, "status": inv.status}
    finally:
        db.close()

@app.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int):
    db = SessionLocal()
    try:
        inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not inv:
            raise HTTPException(status_code=404, detail="not found")
        return {"id": inv.id, "customer": inv.customer, "amount": inv.amount, "status": inv.status}
    finally:
        db.close()
