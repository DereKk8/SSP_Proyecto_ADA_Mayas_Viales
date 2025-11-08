from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import network, points, tsp, export as export_api

app = FastAPI(
    title="OSM TSP Routing API",
    description="Backend API for TSP routing on OSM road networks",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(network.router, prefix="/api/network", tags=["network"])
app.include_router(points.router, prefix="/api/points", tags=["points"])
app.include_router(tsp.router, prefix="/api/tsp", tags=["tsp"])
app.include_router(export_api.router, prefix="/api/export", tags=["export"])

@app.get("/")
async def root():
    return {
        "message": "OSM TSP Routing API",
        "version": "1.0.0",
        "endpoints": {
            "network": "/api/network/load",
            "points": "/api/points/snap",
            "tsp": {
                "bruteforce": "/api/tsp/bruteforce",
                "heldkarp": "/api/tsp/heldkarp",
                "heuristic": "/api/tsp/heuristic"
            },
            "export": {
                "geojson": "/api/export/geojson",
                "wkt": "/api/export/wkt"
            }
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

