import asyncio
from typing import Dict, Optional
from app.models import Bin

# In-memory bin store: bin_id -> Bin
bins: Dict[str, Bin] = {}

# Simulation active flag
simulation_active: bool = False

# Reference to the running background task
_simulation_task: Optional[asyncio.Task] = None


def get_bins() -> Dict[str, Bin]:
    return bins


def set_bins(new_bins: Dict[str, Bin]) -> None:
    global bins
    bins = new_bins


def is_simulation_active() -> bool:
    return simulation_active


def set_simulation_active(value: bool) -> None:
    global simulation_active
    simulation_active = value


def get_simulation_task() -> Optional[asyncio.Task]:
    return _simulation_task


def set_simulation_task(task: Optional[asyncio.Task]) -> None:
    global _simulation_task
    _simulation_task = task
