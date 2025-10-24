import math
from typing import Iterable, Tuple


EARTH_RADIUS_M = 6371000.0


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two WGS84 coords in meters."""
    rlat1 = math.radians(lat1)
    rlon1 = math.radians(lon1)
    rlat2 = math.radians(lat2)
    rlon2 = math.radians(lon2)

    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1

    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_M * c


def total_distance_meters(sequence_of_coords: Iterable[Tuple[float, float]]) -> float:
    """Sum distances between consecutive coordinates.

    sequence_of_coords: iterable of (lat, lon)
    """
    coords = list(sequence_of_coords)
    if len(coords) < 2:
        return 0.0

    total = 0.0
    for (lat1, lon1), (lat2, lon2) in zip(coords, coords[1:]):
        total += haversine_distance_meters(lat1, lon1, lat2, lon2)
    return total
