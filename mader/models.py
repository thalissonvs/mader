from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: int = mapped_column(init=False, primary_key=True)
    username: str = mapped_column(unique=True)
    email: str = mapped_column(unique=True)
    password: str
    created_at: datetime = mapped_column(init=False, server_default=func.now())
    updated_at: datetime = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
