import random


def random_coordinate(lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> tuple[float, float]:
    latitude = round(random.uniform(lat_min, lat_max), 6)
    longitude = round(random.uniform(lon_min, lon_max), 6)
    return latitude, longitude
