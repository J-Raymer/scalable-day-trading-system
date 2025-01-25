import os
import dotenv
from sqlmodel import SQLModel, create_engine

dotenv.load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")
db_name = os.getenv("DB_NAME")

url = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
engine = create_engine(url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)