import random
from datetime import datetime, timezone
from typing import Dict

from app.config import settings
from app.models import Bin
from app.utils.geo import random_coordinate


def initialize_bins() -> Dict[str, Bin]:
    bins: Dict[str, Bin] = {}
    for i in range(1, settings.BIN_COUNT + 1):
        bin_id = f"BIN_{i:03d}"
        lat, lon = random_coordinate(
            settings.LAT_MIN,
            settings.LAT_MAX,
            settings.LON_MIN,
            settings.LON_MAX,
        )
        fill_level = round(
            random.uniform(settings.INITIAL_FILL_MIN, settings.INITIAL_FILL_MAX), 2
        )
        fill_rate = round(random.uniform(0.1, 0.5), 3)
        bins[bin_id] = Bin(
            bin_id=bin_id,
            city=settings.CITY_NAME,
            latitude=lat,
            longitude=lon,
            fill_level=fill_level,
            fill_rate=fill_rate,
            last_updated=datetime.now(timezone.utc),
        )
    return bins


def update_bin_fill(bin: Bin, delta_time: float) -> Bin:
    noise = round(random.uniform(-0.5, 0.5), 3)
    new_fill = bin.fill_level + (bin.fill_rate * delta_time) + noise
    new_fill = round(min(new_fill, settings.MAX_CAPACITY), 2)
    new_fill = max(new_fill, 0.0)
    return bin.model_copy(
        update={
            "fill_level": new_fill,
            "last_updated": datetime.now(timezone.utc),
        }
    )
