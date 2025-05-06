from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base abstract class for ORM models.

    Attributes:
        id (int): The unique identifier for the object.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
