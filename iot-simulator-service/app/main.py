import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from app.config import settings
from app.models import Bin, HealthResponse, MessageResponse
from app.simulator import initialize_bins
from app.scheduler import start_simulation, stop_simulation, reset_simulation
import app.state as state

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    logger.info("Initializing %d bins...", settings.BIN_COUNT)
    bins = initialize_bins()
    state.set_bins(bins)
    logger.info("Bins initialized. Starting simulation automatically.")
    await start_simulation()
    yield
    logger.info("Shutting down — stopping simulation.")
    await stop_simulation()


app = FastAPI(
    title="IoT Simulator Service",
    description="Simulates smart waste bins and pushes fill-level updates to the backend.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="running",
        bins=len(state.get_bins()),
        simulation_active=state.is_simulation_active(),
    )


# ---------------------------------------------------------------------------
# Bins
# ---------------------------------------------------------------------------

@app.get("/bins", response_model=list[Bin], tags=["Bins"])
async def get_bins() -> list[Bin]:
    return list(state.get_bins().values())


@app.get("/bins/{bin_id}", response_model=Bin, tags=["Bins"])
async def get_bin(bin_id: str) -> Bin:
    bin = state.get_bins().get(bin_id)
    if bin is None:
        raise HTTPException(status_code=404, detail=f"Bin '{bin_id}' not found.")
    return bin


# ---------------------------------------------------------------------------
# Simulation control
# ---------------------------------------------------------------------------

@app.post("/simulation/start", response_model=MessageResponse, tags=["Simulation"])
async def simulation_start() -> MessageResponse:
    started = await start_simulation()
    if not started:
        return MessageResponse(message="Simulation already running.")
    return MessageResponse(message="Simulation started.")


@app.post("/simulation/stop", response_model=MessageResponse, tags=["Simulation"])
async def simulation_stop() -> MessageResponse:
    stopped = await stop_simulation()
    if not stopped:
        return MessageResponse(message="Simulation is not running.")
    return MessageResponse(message="Simulation stopped.")


@app.post("/simulation/reset", response_model=MessageResponse, tags=["Simulation"])
async def simulation_reset() -> MessageResponse:
    await reset_simulation()
    return MessageResponse(message="Simulation reset. All bins re-initialized.")
