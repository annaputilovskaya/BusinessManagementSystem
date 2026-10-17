from uuid import UUID, uuid4

from sqlalchemy import UUID as UUID_SQL
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

naming_convention: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Base abstract class for ORM models.

    Attributes:
        id (UUID): The universally unique identifier for the object.
    """

    __abstract__ = True

    metadata = MetaData(naming_convention=naming_convention)

    id: Mapped[UUID] = mapped_column(
        UUID_SQL(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"
