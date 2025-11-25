from pydantic import BaseModel, Field
from typing import Dict, Any, List

class NetworkBounds(BaseModel):
    minLat: float = Field(..., description="Minimum latitude")
    maxLat: float = Field(..., description="Maximum latitude")
    minLon: float = Field(..., description="Minimum longitude")
    maxLon: float = Field(..., description="Maximum longitude")

class NetworkStats(BaseModel):
    nodes: int = Field(..., description="Number of nodes in the network")
    edges: int = Field(..., description="Number of edges in the network")
    bounds: NetworkBounds = Field(..., description="Geographic bounds of the network")

class NetworkResponse(BaseModel):
    stats: NetworkStats
    geojson: Dict[str, Any] = Field(..., description="GeoJSON FeatureCollection of the network")

class SnappedPoint(BaseModel):
    id: int
    original_coords: List[float] = Field(..., description="[lon, lat] original coordinates")
    snapped_coords: List[float] = Field(..., description="[lon, lat] snapped coordinates")
    nearest_edge: List[int] = Field(..., description="[u, v] node IDs of nearest edge")

class PointsResponse(BaseModel):
    snapped_points: List[SnappedPoint]
    geojson: Dict[str, Any] = Field(..., description="GeoJSON FeatureCollection of snapped points")

class TSPRequest(BaseModel):
    point_ids: List[int] = Field(..., description="List of point IDs to visit")
    graph_data: Dict[str, Any] = Field(..., description="Graph data from network")

class TSPResult(BaseModel):
    tour: List[int] = Field(..., description="Ordered list of node IDs in the tour")
    length: float = Field(..., description="Total length of the tour in meters")
    runtime_ms: float = Field(..., description="Runtime in milliseconds")
    path_geojson: Dict[str, Any] = Field(..., description="GeoJSON LineString of the path")
    warning: str | None = Field(None, description="Warning message if any limitations were applied")

