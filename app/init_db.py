from core.db import engine
from core.db import Base

# Create all tables
Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
