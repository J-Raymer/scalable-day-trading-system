from sqlmodel import SQLModel, create_engine

postgres_username = "admin"
postgres_password = "isolated-dean-primal-starving"
postgres_host = "localhost"
postgres_port = "5432"
postgres_db = "day_trader"

postgres_url = f"postgresql://{postgres_username}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

engine = create_engine(postgres_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

