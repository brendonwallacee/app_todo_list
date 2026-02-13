from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api_acess_alterdata.settings import Settings

setting = Settings()

engine = create_engine(setting.DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session
