from confluent_kafka import Producer
import json
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")

producer = Producer({"bootstrap.servers": KAFKA_BROKER})


def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Message delivered to {msg.topic()} [{msg.partition()}]")


def publish_price_event(event: dict, topic: str = "price-events"):
    try:
        producer.produce(
            topic,
            key=event["symbol"],
            value=json.dumps(event),
            callback=delivery_report
        )
        producer.flush()
    except Exception as e:
        print(f"❌ Kafka publish error: {e}")
