import asyncio
import logging
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.simulator import initialize_bins, update_bin_fill
from app.sender import send_bin_update
import app.state as state

logger = logging.getLogger(__name__)


async def _simulation_loop() -> None:
    last_tick = datetime.now(timezone.utc)

    async with httpx.AsyncClient() as client:
        while state.is_simulation_active():
            await asyncio.sleep(settings.UPDATE_INTERVAL)

            if not state.is_simulation_active():
                break

            now = datetime.now(timezone.utc)
            delta_time = (now - last_tick).total_seconds()
            last_tick = now

            current_bins = state.get_bins()
            updated_bins = {}

            for bin_id, bin in current_bins.items():
                updated_bin = update_bin_fill(bin, delta_time)
                updated_bins[bin_id] = updated_bin

            state.set_bins(updated_bins)

            send_tasks = [
                send_bin_update(client, bin) for bin in updated_bins.values()
            ]
            await asyncio.gather(*send_tasks, return_exceptions=True)

            logger.info("Simulation tick completed. Bins updated: %d", len(updated_bins))


async def start_simulation() -> bool:
    if state.is_simulation_active():
        return False

    state.set_simulation_active(True)
    task = asyncio.create_task(_simulation_loop())
    state.set_simulation_task(task)
    logger.info("Simulation started.")
    return True


async def stop_simulation() -> bool:
    if not state.is_simulation_active():
        return False

    state.set_simulation_active(False)
    task = state.get_simulation_task()
    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    state.set_simulation_task(None)
    logger.info("Simulation stopped.")
    return True


async def reset_simulation() -> None:
    await stop_simulation()
    new_bins = initialize_bins()
    state.set_bins(new_bins)
    logger.info("Simulation reset. %d bins re-initialized.", len(new_bins))
