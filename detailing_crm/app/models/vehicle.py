from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VehicleModel(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    make: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    paint_color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vin: Mapped[str | None] = mapped_column(String(17), unique=True, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    client: Mapped["ClientModel"] = relationship(back_populates="vehicles")
    appointments: Mapped[list["AppointmentModel"]] = relationship(back_populates="vehicle")
