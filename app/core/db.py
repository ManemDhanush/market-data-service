from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, DateTime, Integer
from datetime import datetime
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/market_data")

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class MovingAverage(Base):
    __tablename__ = "symbol_averages"

    symbol: Mapped[str] = mapped_column(String, primary_key=True)
    moving_average: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime)

class RawPrice(Base):
    __tablename__ = "raw_price_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String, index=True)
    price: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    source: Mapped[str] = mapped_column(String)
    raw_response_id: Mapped[str] = mapped_column(String)