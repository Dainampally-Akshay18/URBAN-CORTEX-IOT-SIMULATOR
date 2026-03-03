# 📄 PRODUCT REQUIREMENTS DOCUMENT (PRD)

# IoT Simulation Service

Repository Name: `iot-simulator-service`
Tech Stack: Python + FastAPI

---

# 1️⃣ PURPOSE

The IoT Simulation Service simulates smart waste bins in a city and periodically sends bin fill-level updates to the main Smart Waste backend system.

This service represents a **virtual IoT hardware layer** and must:

* Simulate 100+ bins
* Update fill levels over time
* Send updates to backend via REST
* Run independently
* Be stateless (no database)
* Be restart-safe

This service does NOT handle:

* Truck routing
* Bin collection logic
* Complaints
* Predictions
* Assignment logic
* Database persistence

All state persistence happens in the main backend.

---

# 2️⃣ SYSTEM ROLE IN OVERALL ARCHITECTURE

```
IoT Simulator Service
        ↓
Main Backend (Source of Truth)
        ↓
Database
```

The simulator:

* Generates bin state changes
* Pushes updates
* Does not own bin truth

The backend:

* Stores bin data
* Controls state
* Handles truck collection

---

# 3️⃣ FUNCTIONAL REQUIREMENTS

---

## 3.1 Bin Initialization

On service startup:

* Generate N bins (default: 100)
* Each bin must contain:

```
bin_id (unique string)
city (string)
latitude (float)
longitude (float)
fill_level (float)
fill_rate (float)
last_updated (timestamp)
```

Coordinates must be randomly generated within a configurable city bounding box.

Initial fill_level must be randomly generated between configurable range (e.g., 0–30%).

---

## 3.2 Fill Simulation Engine

The service must run a background asynchronous loop.

Every `UPDATE_INTERVAL` seconds:

For each bin:

1. Calculate time delta
2. Increase fill_level using:

```
new_fill = old_fill + (fill_rate × delta_time) + random_noise
```

3. Cap fill_level at 100
4. Update last_updated timestamp
5. Send updated bin data to backend

---

## 3.3 Backend Communication

After each bin update, service must send:

```
POST {BACKEND_URL}/api/bin-update
```

Payload format:

```
{
  "bin_id": "BIN_001",
  "city": "Hyderabad",
  "latitude": 17.385,
  "longitude": 78.486,
  "fill_level": 67.3,
  "timestamp": "ISO_UTC_TIMESTAMP"
}
```

Backend URL must be configurable via environment variable.

---

## 3.4 Simulation Control API

The FastAPI service must expose the following endpoints:

---

### GET /health

Returns:

```
{
  "status": "running",
  "bins": 100,
  "simulation_active": true
}
```

---

### POST /simulation/start

Starts background simulation loop.

---

### POST /simulation/stop

Stops background simulation loop.

---

### POST /simulation/reset

Resets all bins to initial state.

---

### GET /bins

Returns all current in-memory bin states.

---

### GET /bins/{bin_id}

Returns single bin state.

---

# 4️⃣ NON-FUNCTIONAL REQUIREMENTS

* Must support at least 500 bins
* Must use async background tasks
* Must not block API responsiveness
* Must retry failed backend requests
* Must not crash on backend downtime
* Must log all failures
* Must run continuously

---

# 5️⃣ ERROR HANDLING

If backend request fails:

* Retry up to 3 times
* Use exponential backoff
* Log failure
* Continue simulation cycle

Service must not stop simulation due to API failure.

---

# 6️⃣ CONFIGURATION (Environment Variables)

```
BIN_COUNT=100
UPDATE_INTERVAL=60
BACKEND_URL=http://localhost:8000
CITY_NAME=Hyderabad
MAX_CAPACITY=100
INITIAL_FILL_MIN=0
INITIAL_FILL_MAX=30
LAT_MIN=17.30
LAT_MAX=17.45
LON_MIN=78.40
LON_MAX=78.55
LOG_LEVEL=INFO
```

---

# 7️⃣ PROJECT FILE STRUCTURE

```
iot-simulator-service/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── state.py
│   ├── simulator.py
│   ├── sender.py
│   ├── scheduler.py
│   └── utils/
│       └── geo.py
│
├── requirements.txt
├── .env
└── Dockerfile
```

---

# 8️⃣ MODULE RESPONSIBILITIES

---

## main.py

* Create FastAPI instance
* Register routes
* Start background scheduler

---

## config.py

* Load environment variables
* Validate configuration

---

## models.py

* Pydantic models for Bin schema
* API response models

---

## state.py

* In-memory storage for bins
* Global simulation state flag

---

## simulator.py

* Bin initialization
* Fill update logic
* Time delta calculations

---

## sender.py

* Async HTTP client
* Retry mechanism
* Backend communication

---

## scheduler.py

* Async simulation loop
* Start/Stop control

---

## utils/geo.py

* Random coordinate generator
* Bounding box validation

---

# 9️⃣ CONCURRENCY DESIGN

* Use asyncio
* One background task loop
* Non-blocking HTTP requests
* Avoid time.sleep()
* Use await asyncio.sleep()

Simulation must not block API endpoints.

---

# 🔟 MVP DEFINITION

Minimum viable simulator must:

* Generate 100 bins
* Update every 60 seconds
* Send updates to backend
* Support start/stop API
* Log events

No peak-hour logic required.

No zone-based rates required.

No MQTT required.

---

# 1️⃣1️⃣ SUCCESS CRITERIA

Service is successful if:

* Bins update continuously
* Backend receives updates
* Service survives backend downtime
* Restarting service does not break backend state
* Simulation control APIs work correctly

---

# 1️⃣2️⃣ ARCHITECTURAL PRINCIPLES

* Stateless design
* Replaceable by real hardware
* Backend is source of truth
* Loose coupling
* Clean modular separation

---

# 1️⃣3️⃣ FUTURE EXTENSIONS (NOT REQUIRED FOR MVP)

* MQTT publishing
* WebSocket stream
* Device authentication
* Offline buffering simulation
* Peak-hour multiplier

---
