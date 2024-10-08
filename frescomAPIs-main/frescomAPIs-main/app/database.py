from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# Initiate "thick mode"
# Instantclient name should be changed according to OS
thick_mode = {"lib_dir": "./instantclient_23_4"}

# Init the db engine
engine = create_engine(
    f"{settings.database_provider}+{settings.database_driver}://{settings.database_username}:{settings.database_password}@{settings.database_host}:{settings.database_port}/?service_name={settings.database_service_name}",
    thick_mode=thick_mode,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Db session connection function
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
