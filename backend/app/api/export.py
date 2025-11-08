from fastapi import APIRouter

router = APIRouter()

# Placeholders - will be implemented in Phase 8
@router.post("/geojson")
async def export_geojson():
    return {"message": "GeoJSON export endpoint - to be implemented in Phase 8"}

@router.post("/wkt")
async def export_wkt():
    return {"message": "WKT export endpoint - to be implemented in Phase 8"}

