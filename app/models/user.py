import uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Boolean, String, text
from sqlalchemy.dialects.postgresql import UUID
from app.core.db import Base
from sqlalchemy import Enum
import enum

class AccountType(enum.Enum):
        ADMIN = "admin"
        AUTHOR = "author"
        READER = "reader"

        def __str__(self):
            return self.value


class User(Base):
    __tablename__= "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100),unique=True)
    user_name: Mapped[str] = mapped_column(String(20),unique=True)
    password: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    _account_role: Mapped[str] = mapped_column("account_role", String(50), default=AccountType.READER.value)

    @property
    def account_role(self) -> AccountType:
        return AccountType(self._account_role)

    @account_role.setter
    def account_role(self, value: AccountType):
        self._account_role = value.value


