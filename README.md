# 🧠 Market Data Microservice – Blockhouse Intern Project

This is a production-grade FastAPI microservice that fetches real-time market prices, streams them via Kafka, calculates moving averages, and exposes REST endpoints to access raw and processed data.

## 🚀 Features

- `GET /prices/latest` – fetches the latest price for a symbol using `yfinance`
- `POST /prices/poll` – streams price events to Kafka topic `price-events`
- Kafka consumer calculates 5-point moving averages and stores them in PostgreSQL
- `GET /moving-average` – returns the latest moving average for a symbol
- `GET /prices/history` – returns all raw price events for a symbol
- Full Docker Compose setup for Kafka, Zookeeper, and PostgreSQL
- Basic automated tests using `pytest`

## 🛠️ Tech Stack

- **FastAPI** – REST API framework  
- **Kafka** – Event streaming (via `confluent-kafka-python`)  
- **PostgreSQL** – Data storage  
- **SQLAlchemy** – ORM for DB interaction  
- **yfinance** – Real-time market data provider  
- **Docker Compose** – For orchestration  
- **pytest** – Test runner

## 📦 Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd market-data-service
2. Create and activate a virtual environment
bash
Copy
Edit
python -m venv venv
venv\Scripts\activate  # On Windows
3. Install Python dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Start infrastructure with Docker
bash
Copy
Edit
docker compose up -d
5. Create database tables
bash
Copy
Edit
python create_tables.py
6. Start the Kafka Consumer (in a separate terminal)
bash
Copy
Edit
python kafka_consumer.py
7. Start the FastAPI server
bash
Copy
Edit
uvicorn main:app --reload
Visit the docs at: http://localhost:8000/docs

🔌 API Endpoints
GET /prices/latest
Fetch the latest stock price:

bash
Copy
Edit
/prices/latest?symbol=AAPL
POST /prices/poll
Send symbols to be polled and streamed to Kafka:

json
Copy
Edit
{
  "symbols": ["AAPL", "MSFT"],
  "interval": 60,
  "provider": "yfinance"
}
GET /moving-average
Return the latest 5-point moving average:

bash
Copy
Edit
/moving-average?symbol=AAPL
GET /prices/history
Return all raw price events for a symbol:

bash
Copy
Edit
/prices/history?symbol=AAPL
🧪 Running Tests
bash
Copy
Edit
pytest
📁 Project Structure
graphql
Copy
Edit
market-data-service/
├── main.py                  # FastAPI app
├── kafka_consumer.py        # Kafka consumer logic
├── kafka_producer.py        # Kafka producer logic
├── db.py                    # SQLAlchemy models
├── schema.py                # Pydantic request/response models
├── create_tables.py         # One-time DB setup script
├── docker-compose.yml       # Kafka, Zookeeper, Postgres services
├── tests/
│   └── test_main.py         # Test suite (pytest)
└── README.md                # Project docs
✅ Status
✅ Feature complete

✅ Tested with real market data

✅ Docker-ready stack

✅ Clean and production-style structure

🙌 Author
[Your Name]
Blockhouse Capital – Software Engineer Intern Assignment

yaml
Copy
Edit

---

You're good to drop this directly into `README.md`. Everything is now perfectly structured with **proper line spacing between code blocks and headers**.

Want a `.gitignore` or final review checklist next?