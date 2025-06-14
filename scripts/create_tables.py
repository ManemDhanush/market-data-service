from app.core.db import Base, engine

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("✅ Tables created.")