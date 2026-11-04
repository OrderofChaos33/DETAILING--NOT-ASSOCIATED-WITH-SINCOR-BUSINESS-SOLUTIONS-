from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class AppointmentModel(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    service_type: Mapped[str] = mapped_column(String(100), nullable=False)
    scheduled_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    estimated_duration_hours: Mapped[int] = mapped_column(default=4)
    buffer_minutes: Mapped[int] = mapped_column(default=30)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    deposit_paid: Mapped[bool] = mapped_column(Boolean, default=False)  # no-deposit model by owner decision
    status: Mapped[str] = mapped_column(String(30), default="scheduled")
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    review_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    vehicle: Mapped["VehicleModel"] = relationship(back_populates="appointments")
