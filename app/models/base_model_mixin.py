from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean

class BaseModelMixin:
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)