from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )


@table_registry.mapped_as_dataclass
class Book:
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    year: Mapped[str]
    romancist_id: Mapped[int] = mapped_column(ForeignKey('romancists.id'))
    romancist: Mapped['Romancist'] = relationship(
        init=False,
        back_populates='books',
    )


@table_registry.mapped_as_dataclass
class Romancist:
    __tablename__ = 'romancists'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    books: Mapped[list['Book']] = relationship(
        init=False,
        back_populates='romancist',
        cascade='all, delete-orphan',
        # lazy='joined',
    )
