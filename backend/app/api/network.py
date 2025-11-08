from fastapi import APIRouter, File, UploadFile, HTTPException
from app.models.network import NetworkResponse, NetworkStats, NetworkBounds
from app.core.network_loader import process_network

router = APIRouter()

# In-memory storage for the current network graph
# In production, use Redis or database
_network_cache = {}

@router.post("/load", response_model=NetworkResponse)
async def load_network(osm_file: UploadFile = File(...)):
    """
    Load OSM network file and return network statistics and GeoJSON.
    
    Args:
        osm_file: OSM file (.osm or .pbf format)
        
    Returns:
        NetworkResponse with stats and GeoJSON
    """
    try:
        # Read file content
        file_content = await osm_file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Process network
        graph, geojson, stats, bounds = process_network(file_content)
        
        # Cache the graph for later use (point snapping, TSP)
        _network_cache['graph'] = graph
        _network_cache['geojson'] = geojson
        
        # Build response
        response = NetworkResponse(
            stats=NetworkStats(
                nodes=stats['nodes'],
                edges=stats['edges'],
                bounds=NetworkBounds(
                    minLat=bounds['minLat'],
                    maxLat=bounds['maxLat'],
                    minLon=bounds['minLon'],
                    maxLon=bounds['maxLon']
                )
            ),
            geojson=geojson
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load network: {str(e)}"
        )

@router.get("/cache/status")
async def get_cache_status():
    """Check if network is cached"""
    return {
        "cached": 'graph' in _network_cache,
        "nodes": _network_cache['graph'].number_of_nodes() if 'graph' in _network_cache else 0,
        "edges": _network_cache['graph'].number_of_edges() if 'graph' in _network_cache else 0
    }

def get_cached_graph():
    """Helper function to retrieve cached graph"""
    if 'graph' not in _network_cache:
        raise HTTPException(status_code=400, detail="No network loaded. Please upload OSM file first.")
    return _network_cache['graph']

