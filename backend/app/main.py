from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from sqlalchemy.sql import func
import math
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/route_planner")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    waypoints = relationship("Waypoint", back_populates="route", cascade="all, delete-orphan", order_by="Waypoint.order_index")

class Waypoint(Base):
    __tablename__ = "waypoints"
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    order_index = Column(Integer, nullable=False)
    route = relationship("Route", back_populates="waypoints")

# Pydantic models
class WaypointCreate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    order: int = Field(..., ge=1)

class RouteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    waypoints: List[WaypointCreate]

class WaypointOut(BaseModel):
    id: int
    latitude: float
    longitude: float
    order: int
    class Config:
        from_attributes = True
        json_encoders = {
            # Ensure Decimal to float
        }

class RouteSummary(BaseModel):
    id: int
    name: str
    waypoint_count: int
    total_distance_km: float
    created_at: Optional[str]

class RouteOut(BaseModel):
    id: int
    name: str
    total_distance_km: float
    waypoints: List[WaypointOut]
    created_at: Optional[str]

# Distance calculation (Haversine)
R_EARTH_KM = 6371.0

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R_EARTH_KM * c


def calc_total_distance_km(ordered_waypoints: List[Waypoint]) -> float:
    if not ordered_waypoints or len(ordered_waypoints) < 2:
        return 0.0
    total = 0.0
    for i in range(1, len(ordered_waypoints)):
        a = ordered_waypoints[i - 1]
        b = ordered_waypoints[i]
        total += haversine_km(float(a.latitude), float(a.longitude), float(b.latitude), float(b.longitude))
    return round(total, 3)

# FastAPI app
app = FastAPI(title="Route Planning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables if not exist (for local dev convenience)
Base.metadata.create_all(bind=engine)

# Endpoints
@app.post("/api/routes", response_model=RouteOut)
def create_route(payload: RouteCreate, db: Session = Depends(get_db)):
    if not payload.waypoints or len(payload.waypoints) < 1:
        raise HTTPException(status_code=400, detail="Se requiere al menos un waypoint")

    # Sort by provided 'order'
    sorted_wps = sorted(payload.waypoints, key=lambda w: w.order)

    route = Route(name=payload.name)
    db.add(route)
    db.flush()  # get route id

    created_wps: List[Waypoint] = []
    for wp in sorted_wps:
        created_wp = Waypoint(
            route_id=route.id,
            latitude=wp.latitude,
            longitude=wp.longitude,
            order_index=wp.order,
        )
        db.add(created_wp)
        created_wps.append(created_wp)

    db.commit()
    db.refresh(route)

    distance_km = calc_total_distance_km(created_wps)

    return RouteOut(
        id=route.id,
        name=route.name,
        total_distance_km=distance_km,
        waypoints=[
            WaypointOut(id=wp.id, latitude=float(wp.latitude), longitude=float(wp.longitude), order=wp.order_index)
            for wp in created_wps
        ],
        created_at=route.created_at.isoformat() if route.created_at else None,
    )


@app.get("/api/routes", response_model=List[RouteSummary])
def list_routes(db: Session = Depends(get_db)):
    routes = db.query(Route).all()
    results: List[RouteSummary] = []
    for route in routes:
        ordered = list(route.waypoints)
        distance_km = calc_total_distance_km(ordered)
        results.append(
            RouteSummary(
                id=route.id,
                name=route.name,
                waypoint_count=len(ordered),
                total_distance_km=distance_km,
                created_at=route.created_at.isoformat() if route.created_at else None,
            )
        )
    return results


@app.get("/api/routes/{route_id}", response_model=RouteOut)
def get_route(route_id: int, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    ordered = list(route.waypoints)
    distance_km = calc_total_distance_km(ordered)
    return RouteOut(
        id=route.id,
        name=route.name,
        total_distance_km=distance_km,
        waypoints=[
            WaypointOut(id=wp.id, latitude=float(wp.latitude), longitude=float(wp.longitude), order=wp.order_index)
            for wp in ordered
        ],
        created_at=route.created_at.isoformat() if route.created_at else None,
    )


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
