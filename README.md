# 🚗 Fuel Route Optimization API

A Django-based API that generates optimized driving routes within the United States and determines cost-efficient fuel stops along the route based on vehicle range and fuel pricing.

---

## 📌 Overview

This service:

- Accepts **start and end city/state inputs**
- Generates a driving route using OpenRouteService
- Simulates vehicle fuel consumption along the route
- Identifies cost-efficient refueling stops
- Calculates total estimated fuel cost using precision-safe financial math

The system is designed with clean architecture, performance awareness, and scalability in mind.

---

## 🏗 Architecture

The project follows a service-oriented architecture with clear separation of concerns:

```
routes/
├── views.py                # API endpoints
├── services/
│   ├── routing.py          # Route + geocoding logic
│   ├── fuel_optimizer.py   # Fuel optimization engine
│   └── geocoding.py        # Location conversion
├── utils/
│   └── polyline.py         # Route decoding
├── models.py               # FuelStation model
```

### Core Components

**RoutingService**
- Converts city/state into coordinates
- Calls OpenRouteService API
- Decodes route polyline
- Returns structured route data

**FuelOptimizer**
- Simulates vehicle movement along the route
- Selects cheapest fuel stations within range
- Calculates total fuel cost using Decimal-safe math

**FuelStation Model**
- Stores station name, coordinates, and retail price
- Optimized for bounding-box filtering

---

## ⚙️ How It Works

### 1️⃣ Route Generation

- City/state inputs are geocoded into coordinates.
- OpenRouteService generates a driving route.
- Encoded polyline is decoded into coordinate points.
- Distance is converted into miles.

---

### 2️⃣ Fuel Optimization Strategy

The optimizer:

1. Computes a bounding box around the route to avoid full table scans.
2. Simulates vehicle progression using geodesic distance calculations.
3. Uses:
   - 500-mile maximum range  
   - 10 MPG fuel efficiency  
4. When max range is exceeded:
   - Identifies stations within 10 miles of the current route point
   - Selects the cheapest station
   - Records a fuel stop
   - Resets fuel range counter

This implements a spatially-aware greedy optimization strategy.

---

### 3️⃣ Financial Accuracy

Fuel prices are stored as `Decimal`.

All cost calculations use Python’s `Decimal` type to prevent floating-point precision errors.

Final fuel cost is rounded safely to two decimal places.

---

## 🐳 Docker-Based Data Seeding

Fuel station data is seeded during the **Docker build stage**, not at runtime.

This ensures:

- No long delays during API calls
- No heavy data-loading operations during container startup
- Consistent performance across environments

The container is production-ready immediately after startup.

---

## 🚀 API Endpoint

### Optimize Route

**POST** `/api/optimize-route/`

---

### Request Body

```json
{
  "start_city": "Atlanta",
  "start_state": "GA",
  "end_city": "Dallas",
  "end_state": "TX"
}
```

---

### Example Response

```json
{
  "route": [[-84.38, 33.75], ...],
  "distance_miles": 781.4,
  "fuel_stops": [
    {
      "name": "Station A",
      "price": "3.45",
      "latitude": 32.1,
      "longitude": -95.2
    }
  ],
  "total_fuel_cost": "269.83"
}
```

---

## 🛠 Installation

### Requirements

- Docker
- Docker Compose
- OpenRouteService API Key

---

### Environment Variables

Create a `.env` file:

```
ORS_API_KEY=your_openrouteservice_api_key
```

---

### Run with Docker

```bash
docker compose up --build
```

The API will be available at:

```
http://localhost:8000/api/optimize-route/
```

---

## 📊 Scalability Considerations

- Bounding-box filtering avoids full database scans.
- Business logic is separated from routing logic.
- Financial math is precision-safe.
- Architecture supports future enhancements such as:
  - PostGIS spatial indexing
  - GeoDjango distance queries
  - Advanced fuel price prediction
  - Smarter cost minimization algorithms

---

## 📄 License

MIT License
