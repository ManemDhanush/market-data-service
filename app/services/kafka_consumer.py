# kafka_consumer.py
from confluent_kafka import Consumer, KafkaException
from collections import defaultdict, deque
import json
import time
from app.core.db import SessionLocal, MovingAverage
from datetime import datetime
from app.core.db import RawPrice

KAFKA_BROKER = "localhost:9092"
TOPIC = "price-events"

# Memory store for latest 5 prices per symbol
price_history = defaultdict(lambda: deque(maxlen=5))

def calculate_moving_average(prices):
    return round(sum(prices) / len(prices), 2)

def start_consumer():
    consumer = Consumer({
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": "ma-consumer-group",
        "auto.offset.reset": "earliest"
    })

    consumer.subscribe([TOPIC])
    print(f"🟢 Listening to topic '{TOPIC}'...")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            event = json.loads(msg.value().decode("utf-8"))
            symbol = event["symbol"]
            price = event["price"]
            # saving raw price data to DB
            session = SessionLocal()
            try:
                session.add(RawPrice(
                    symbol=symbol,
                    price=price,
                    timestamp=datetime.fromisoformat(event["timestamp"]),
                    source=event["source"],
                    raw_response_id=event["raw_response_id"]
                ))
                session.commit()
            except Exception as e:
                print(f"❌ DB error (raw price): {e}")
            finally:
                session.close()

            # Update price history
            price_history[symbol].append(price)

            if len(price_history[symbol]) == 5:
                ma = calculate_moving_average(price_history[symbol])
                print(f"📈 {symbol} - 5pta MA = {ma}")

                # Save to DB
                session = SessionLocal()
                try:
                    existing = session.query(MovingAverage).filter_by(symbol=symbol).first()
                    if existing:
                        existing.moving_average = ma
                        existing.timestamp = datetime.utcnow()
                    else:
                        session.add(MovingAverage(
                            symbol=symbol,
                            moving_average=ma,
                            timestamp=datetime.utcnow()
                        ))
                    session.commit()
                except Exception as e:
                    print(f"❌ DB error: {e}")
                finally:
                    session.close()

            else:
                print(f"➕ {symbol} - Collected {len(price_history[symbol])}/5 prices")

    except KeyboardInterrupt:
        print("👋 Shutting down consumer.")
    finally:
        consumer.close()

if __name__ == "__main__":
    start_consumer()