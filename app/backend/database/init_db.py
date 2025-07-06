from sqlalchemy import create_engine

from database import Base

engine = create_engine('sqlite:///finsight_app.db', connect_args={"check_same_thread": False})

# Create tables
Base.metadata.create_all(engine)