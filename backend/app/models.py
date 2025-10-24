from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import relationship

from .database import Base


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)

    waypoints = relationship(
        "Waypoint",
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="Waypoint.order_index.asc()",
    )


class Waypoint(Base):
    __tablename__ = "waypoints"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    order_index = Column(Integer, nullable=False)

    route = relationship("Route", back_populates="waypoints")
