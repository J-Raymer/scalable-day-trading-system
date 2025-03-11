import os
import dotenv
from sqlmodel import create_engine, Session
from sqlalchemy.pool import NullPool  # Disable connection pooling

dotenv.load_dotenv(override=True)
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@pgbouncer:6432/{DB_NAME}"

# Disable connection pooling (use PgBouncer instead)
engine = create_engine(DATABASE_URL, echo=False, poolclass=NullPool)

def get_session():
    with Session(engine) as session:
        yield session
