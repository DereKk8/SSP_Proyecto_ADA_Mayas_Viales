import io
import tempfile
import os
import osmnx as ox
import networkx as nx
from shapely.geometry import LineString
from typing import Dict, Any, Tuple

def load_osm_from_bytes(file_bytes: bytes) -> nx.MultiDiGraph:
    """
    Load an OSM file from bytes and convert to NetworkX graph.
    
    Args:
        file_bytes: OSM file content as bytes
        
    Returns:
        NetworkX MultiDiGraph representing the road network
    """
    # Write bytes to temporary file (osmnx requires file path)
    with tempfile.NamedTemporaryFile(suffix='.osm', delete=False) as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name
    
    try:
        # Load graph from OSM file
        # simplify=True merges intersection nodes
        G = ox.graph_from_xml(tmp_path, simplify=True, retain_all=False)
        
        # Ensure the graph is a MultiDiGraph
        if not isinstance(G, nx.MultiDiGraph):
            G = nx.MultiDiGraph(G)
        
        # Add edge lengths if not present
        G = ox.distance.add_edge_lengths(G)
        
        return G
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def calculate_bounds(G: nx.MultiDiGraph) -> Dict[str, float]:
    """
    Calculate geographic bounds of the network.
    
    Args:
        G: NetworkX graph with node coordinates
        
    Returns:
        Dict with minLat, maxLat, minLon, maxLon
    """
    lats = [data['y'] for _, data in G.nodes(data=True)]
    lons = [data['x'] for _, data in G.nodes(data=True)]
    
    return {
        'minLat': min(lats),
        'maxLat': max(lats),
        'minLon': min(lons),
        'maxLon': max(lons)
    }

def graph_to_geojson(G: nx.MultiDiGraph) -> Dict[str, Any]:
    """
    Convert NetworkX graph to GeoJSON FeatureCollection.
    
    Args:
        G: NetworkX graph
        
    Returns:
        GeoJSON FeatureCollection with edges as LineStrings
    """
    features = []
    
    for u, v, key, data in G.edges(keys=True, data=True):
        # Get node coordinates
        u_data = G.nodes[u]
        v_data = G.nodes[v]
        
        # Create LineString geometry
        # Use edge geometry if available, otherwise straight line
        if 'geometry' in data:
            geom = data['geometry']
            coords = list(geom.coords)
        else:
            coords = [
                (u_data['x'], u_data['y']),
                (v_data['x'], v_data['y'])
            ]
        
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': coords
            },
            'properties': {
                'u': int(u),
                'v': int(v),
                'key': int(key),
                'length': data.get('length', 0)
            }
        }
        features.append(feature)
    
    return {
        'type': 'FeatureCollection',
        'features': features
    }

def process_network(file_bytes: bytes) -> Tuple[nx.MultiDiGraph, Dict[str, Any], Dict[str, int], Dict[str, float]]:
    """
    Process OSM file and extract network information.
    
    Args:
        file_bytes: OSM file content as bytes
        
    Returns:
        Tuple of (graph, geojson, stats, bounds)
    """
    # Load graph
    G = load_osm_from_bytes(file_bytes)
    
    # Calculate stats
    stats = {
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges()
    }
    
    # Calculate bounds
    bounds = calculate_bounds(G)
    
    # Convert to GeoJSON
    geojson = graph_to_geojson(G)
    
    return G, geojson, stats, bounds

