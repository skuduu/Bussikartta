from fastapi import FastAPI

# Import routers from all route modules
from api.routes import (
    agency,
    alerts,
    calendar,
    emissions,
    fare_attributes,
    fare_rules,
    feed_info,
    routes,
    stops,
    transfers,
    trips,
    vehicle_positions,
    vehicles,
)

app = FastAPI(
    title="HSL Bus API",
    description="API for Helsinki Regional Transport data",
    version="0.1.0",
)

# Include all routers
app.include_router(agency.router)
app.include_router(alerts.router)
app.include_router(calendar.router)
app.include_router(emissions.router)
app.include_router(fare_attributes.router)
app.include_router(fare_rules.router)
app.include_router(feed_info.router)
app.include_router(routes.router)
app.include_router(stops.router)
app.include_router(transfers.router)
app.include_router(trips.router)
app.include_router(vehicle_positions.router)
app.include_router(vehicles.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)