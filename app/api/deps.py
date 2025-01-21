from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.db import get_db

SessionDep = Annotated[Session, Depends(get_db)]