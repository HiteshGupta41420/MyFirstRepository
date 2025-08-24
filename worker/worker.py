
import os, time, enum
from sqlalchemy import create_engine, Column, Integer, String, Float, Enum as SAEnum
from sqlalchemy.orm import sessionmaker, declarative_base

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
    status = Column(SAEnum(StatusEnum), default=StatusEnum.PENDING, nullable=False)

# safety: ensure table exists if backend not yet initialized
Base.metadata.create_all(bind=engine)

def main():
    print("Worker started. Polling for PENDING invoices...")
    while True:
        db = SessionLocal()
        try:
            inv = db.query(Invoice).filter(Invoice.status == StatusEnum.PENDING).first()
            if inv:
                print(f"Processing invoice {inv.id} for {inv.customer} amount={inv.amount}")
                # simulate heavy work
                time.sleep(2)
                inv.status = StatusEnum.COMPLETED
                db.commit()
                print(f"Invoice {inv.id} marked COMPLETED")
            else:
                time.sleep(3)
        except Exception as e:
            print("Worker error:", e)
            time.sleep(5)
        finally:
            db.close()

if __name__ == "__main__":
    main()
