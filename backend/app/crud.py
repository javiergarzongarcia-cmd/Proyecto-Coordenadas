from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from . import models
from .schemas import RouteCreate
from .utils import total_distance_meters


def create_route(db: Session, route_in: RouteCreate) -> models.Route:
    # Ensure waypoints are ordered by provided 'order'
    sorted_waypoints = sorted(route_in.waypoints, key=lambda w: w.order)

    db_route = models.Route(name=route_in.name)
    db.add(db_route)
    db.flush()  # obtain route id

    for wp in sorted_waypoints:
        db_wp = models.Waypoint(
            route_id=db_route.id,
            latitude=wp.latitude,
            longitude=wp.longitude,
            order_index=wp.order,
        )
        db.add(db_wp)

    db.commit()
    db.refresh(db_route)
    return db_route


def get_routes(db: Session) -> List[models.Route]:
    stmt = select(models.Route).options(selectinload(models.Route.waypoints))
    return list(db.scalars(stmt).all())


def get_route_by_id(db: Session, route_id: int) -> Optional[models.Route]:
    stmt = (
        select(models.Route)
        .where(models.Route.id == route_id)
        .options(selectinload(models.Route.waypoints))
    )
    return db.scalars(stmt).first()


def compute_route_total_distance(route: models.Route) -> float:
    coords = [(float(w.latitude), float(w.longitude)) for w in route.waypoints]
    return total_distance_meters(coords)
