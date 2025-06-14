from fastapi import FastAPI, Query, HTTPException, status, Depends
import yfinance as yf
from app.schemas.schema import MovingAverageResponse, PriceResponse
from app.schemas.schema import PollRequest, PollResponse, PriceHistoryItem
from fastapi.responses import JSONResponse
import uuid
from app.services.kafka_producer import publish_price_event
from sqlalchemy.orm import Session
from app.core.db import SessionLocal, MovingAverage, RawPrice
from typing import List
from datetime import datetime


app = FastAPI()


@app.get("/prices/latest", response_model=PriceResponse)
def get_latest_price(symbol: str = Query(..., min_length=1)):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1m")

        if data.empty:
            raise HTTPException(status_code=404, detail="No data found")

        latest = data.tail(1).iloc[0]
        return {
            "symbol": symbol.upper(),
            "price": round(latest["Close"], 2),
            "timestamp": latest.name.isoformat(),  # type: ignore
            "provider": 'yfinance'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prices/poll", response_model=PollResponse, status_code=202)
def poll_prices(req: PollRequest):
    job_id = f"poll_{uuid.uuid4().hex[:6]}"

    for symbol in req.symbols:
        try:

            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")

            if data.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for symbol '{symbol}'")

            latest = data.tail(1).iloc[0]

            event = {
                "symbol": symbol.upper(),
                "price": round(latest["Close"], 2),
                "timestamp": datetime
                .fromisoformat(str(latest.name))
                .isoformat(),
                "source": 'yfinance',
                "raw_response_id": str(uuid.uuid4())
            }

            publish_price_event(event)

        except Exception as e:
            print(f"❌ Error fetching price for {symbol}: {e}")

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "job_id": job_id,
            "status": "accepted",
            "config": req.model_dump()
        }
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/moving-average", response_model=MovingAverageResponse)
def get_moving_average(symbol: str, db: Session = Depends(get_db)):
    result = db.query(MovingAverage).filter(
        MovingAverage.symbol == symbol.upper()).first()
    if not result:
        raise HTTPException(status_code=404, detail="No moving average found")

    return {
        "symbol": result.symbol,
        "moving_average": result.moving_average,
        "timestamp": result.timestamp.isoformat()
    }


@app.get("/prices/history", response_model=List[PriceHistoryItem])
def get_price_history(symbol: str, db: Session = Depends(get_db)):
    results = (
        db.query(RawPrice)
        .filter(RawPrice.symbol == symbol.upper())
        .order_by(RawPrice.timestamp.asc())
        .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail="No price history found")

    return [
        {
            "symbol": r.symbol,
            "price": r.price,
            "timestamp": r.timestamp.isoformat(),
            "source": r.source
        }
        for r in results
    ]
