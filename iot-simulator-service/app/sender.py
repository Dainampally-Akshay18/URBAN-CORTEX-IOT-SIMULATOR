import asyncio
import logging

import httpx

from app.config import settings
from app.models import Bin, BinUpdatePayload

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BASE_BACKOFF = 1.0


async def send_bin_update(client: httpx.AsyncClient, bin: Bin) -> None:
    payload = BinUpdatePayload(
        bin_id=bin.bin_id,
        city=bin.city,
        latitude=bin.latitude,
        longitude=bin.longitude,
        fill_level=bin.fill_level,
        timestamp=bin.last_updated.isoformat(),
    )
    url = f"{settings.BACKEND_URL}/api/bin-update"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.post(url, json=payload.model_dump(), timeout=10.0)
            response.raise_for_status()
            return
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "HTTP error sending update for %s (attempt %d/%d): %s",
                bin.bin_id, attempt, MAX_RETRIES, exc,
            )
        except Exception as exc:
            logger.warning(
                "Request error sending update for %s (attempt %d/%d): %s",
                bin.bin_id, attempt, MAX_RETRIES, exc,
            )

        if attempt < MAX_RETRIES:
            backoff = BASE_BACKOFF * (2 ** (attempt - 1))
            await asyncio.sleep(backoff)

    logger.error("Failed to send update for %s after %d attempts.", bin.bin_id, MAX_RETRIES)
