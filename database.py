from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Nombre de la base de datos (igual que en tu appsettings.json original pero con extensión .db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./checador_python.db"

# connect_args={"check_same_thread": False} es necesario solo para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para obtener la sesión de base de datos en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()