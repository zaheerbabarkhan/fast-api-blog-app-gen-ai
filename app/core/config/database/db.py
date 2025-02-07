from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, with_loader_criteria
from sqlalchemy.ext.declarative import declarative_base

from app.models.base_model_mixin import BaseModelMixin

from ..config import settings

Base = declarative_base()

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to attach to the do_orm_execute event of the SessionLocal
# This function will add a filter to the query to exclude soft deleted records
@event.listens_for(SessionLocal, "do_orm_execute")
def _add_filtering_criteria(execute_state):
    skip_filter = execute_state.execution_options.get("skip_filter", False)

    if execute_state.is_select and not skip_filter:
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                BaseModelMixin,
                lambda cls: cls.is_deleted.is_(False),
                include_aliases=True,
            )

        )
# Function to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
