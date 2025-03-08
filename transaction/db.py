import os
import dotenv
from sqlmodel import create_engine, Session

dotenv.load_dotenv(override=True)
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}?sslmode=require"

# Create the database engine with connection pooling
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)

def get_session():
    with Session(engine) as session:
        yield session
