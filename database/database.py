import os
from typing import override
import dotenv
from sqlmodel import SQLModel, create_engine


def create_db_and_tables():
    dotenv.load_dotenv(override=True)

    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    host = os.getenv("HOST")
    port = os.getenv("POSTGRES_PORT")
    db_name = os.getenv("DB_NAME")

    url = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
    engine = create_engine(url)

    SQLModel.metadata.create_all(engine)

    print("DATABASE USERNAME -------", username)
