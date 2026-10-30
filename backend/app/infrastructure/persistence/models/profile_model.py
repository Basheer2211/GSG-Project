
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.db.base import Base



class ProfileModel(Base):
    __tablename__ = "profile"

    profile_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("app_user.user_id"),
        unique=True,
        nullable=False
    )

    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    country_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("country.country_id"),
        nullable=True
    )

    country: Mapped["CountryModel | None"] = relationship(
        "CountryModel",
        back_populates="profiles"
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="profile"
    )
    source_files: Mapped[list["SourceFileModel"]] = relationship(
    "SourceFileModel",
    back_populates="profile"
)
