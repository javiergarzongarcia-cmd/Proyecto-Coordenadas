from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from sqlalchemy.sql import func
import math
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/route_planner")

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
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    order_index = Column(Integer, nullable=False)

    route = relationship("Route", back_populates="waypoints")

# Pydantic Schemas
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
            # Ensure Decimals convert to float
        }

class RouteOut(BaseModel):
    id: int
    name: str
    total_distance_km: float
    created_at: Optional[str]
    waypoint_count: int

    class Config:
        from_attributes = True

class RouteDetailOut(BaseModel):
    id: int
    name: str
    total_distance_km: float
    created_at: Optional[str]
    waypoints: List[WaypointOut]

    class Config:
        from_attributes = True

# Distance calculations
EARTH_RADIUS_KM = 6371.0088

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c

# DB utils

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD helpers

def compute_total_distance_km(waypoints: List[Waypoint]) -> float:
    total = 0.0
    for i in range(1, len(waypoints)):
        a = waypoints[i - 1]
        b = waypoints[i]
        total += haversine_km(float(a.latitude), float(a.longitude), float(b.latitude), float(b.longitude))
    return round(total, 3)

# FastAPI App
app = FastAPI(title="Route Planning API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Endpoints
@app.post("/api/routes", response_model=RouteDetailOut)
def create_route(payload: RouteCreate, db: Session = Depends(get_db)):
    if not payload.waypoints or len(payload.waypoints) < 1:
        raise HTTPException(status_code=400, detail="Se requieren al menos 1 waypoint")

    # Validate unique order
    orders = [wp.order for wp in payload.waypoints]
    if len(orders) != len(set(orders)):
        raise HTTPException(status_code=400, detail="Los 'order' de waypoints deben ser únicos")

    route = Route(name=payload.name)
    db.add(route)
    db.flush()

    # Create Waypoints
    for wp in payload.waypoints:
        db.add(Waypoint(route_id=route.id, latitude=wp.latitude, longitude=wp.longitude, order_index=wp.order))
    db.flush()

    # Load waypoints ordered
    db.refresh(route)
    waypoints_ordered = route.waypoints

    total_distance = compute_total_distance_km(waypoints_ordered)

    db.commit()

    return RouteDetailOut(
        id=route.id,
        name=route.name,
        total_distance_km=total_distance,
        created_at=str(route.created_at) if route.created_at else None,
        waypoints=[WaypointOut(id=w.id, latitude=float(w.latitude), longitude=float(w.longitude), order=w.order_index) for w in waypoints_ordered]
    )

@app.get("/api/routes", response_model=List[RouteOut])
def list_routes(db: Session = Depends(get_db)):
    routes = db.query(Route).all()
    results: List[RouteOut] = []
    for r in routes:
        total_distance = compute_total_distance_km(r.waypoints)
        results.append(RouteOut(
            id=r.id,
            name=r.name,
            total_distance_km=total_distance,
            created_at=str(r.created_at) if r.created_at else None,
            waypoint_count=len(r.waypoints)
        ))
    return results

@app.get("/api/routes/{route_id}", response_model=RouteDetailOut)
def get_route(route_id: int, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    total_distance = compute_total_distance_km(route.waypoints)
    return RouteDetailOut(
        id=route.id,
        name=route.name,
        total_distance_km=total_distance,
        created_at=str(route.created_at) if route.created_at else None,
        waypoints=[WaypointOut(id=w.id, latitude=float(w.latitude), longitude=float(w.longitude), order=w.order_index) for w in route.waypoints]
    )

