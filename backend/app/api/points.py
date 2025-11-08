from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from app.models.network import PointsResponse, SnappedPoint
from app.core.point_snapper import load_points_from_bytes, snap_points_to_network, snapped_points_to_geojson
from app.api.network import get_cached_graph
import json

router = APIRouter()

# Cache for snapped points
_points_cache = {}

@router.post("/snap", response_model=PointsResponse)
async def snap_points(
    points_file: UploadFile = File(...),
    network_geojson: str = Form(...)
):
    """
    Load points from TSV/CSV file, snap them to the nearest network edges.
    
    Args:
        points_file: TSV or CSV file with columns: X, Y, id
        network_geojson: GeoJSON of the network (for reference, actual graph from cache)
        
    Returns:
        PointsResponse with snapped points and GeoJSON
    """
    try:
        # Get cached graph
        G = get_cached_graph()
        
        # Read points file
        file_content = await points_file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Load points
        points_df = load_points_from_bytes(file_content)
        
        # Snap points to network
        snapped_points_list, G_modified = snap_points_to_network(points_df, G)
        
        # Convert to GeoJSON
        geojson = snapped_points_to_geojson(snapped_points_list)
        
        # Cache the snapped points
        _points_cache['points'] = snapped_points_list
        _points_cache['graph'] = G_modified
        
        # Build response
        response = PointsResponse(
            snapped_points=[
                SnappedPoint(
                    id=p['id'],
                    original_coords=p['original_coords'],
                    snapped_coords=p['snapped_coords'],
                    nearest_edge=p['nearest_edge']
                )
                for p in snapped_points_list
            ],
            geojson=geojson
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to snap points: {str(e)}"
        )

@router.get("/cache/status")
async def get_points_cache_status():
    """Check if points are cached"""
    return {
        "cached": 'points' in _points_cache,
        "count": len(_points_cache['points']) if 'points' in _points_cache else 0
    }

def get_cached_points():
    """Helper function to retrieve cached points"""
    if 'points' not in _points_cache:
        raise HTTPException(status_code=400, detail="No points loaded. Please upload points file first.")
    return _points_cache['points']

def get_cached_modified_graph():
    """Helper function to retrieve cached modified graph"""
    if 'graph' not in _points_cache:
        raise HTTPException(status_code=400, detail="No points loaded. Please upload points file first.")
    return _points_cache['graph']

