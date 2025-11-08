import pandas as pd
import networkx as nx
import numpy as np
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
from typing import List, Dict, Any, Tuple
import io

def load_points_from_bytes(file_bytes: bytes, delimiter: str = '\t') -> pd.DataFrame:
    """
    Load points from TSV/CSV bytes.
    
    Args:
        file_bytes: File content as bytes
        delimiter: Column delimiter (default: tab for TSV)
        
    Returns:
        DataFrame with columns: id, X, Y
    """
    # Try to detect delimiter
    content = file_bytes.decode('utf-8')
    if ',' in content.split('\n')[0] and delimiter == '\t':
        delimiter = ','
    
    df = pd.read_csv(io.StringIO(content), delimiter=delimiter)
    
    # Ensure required columns exist
    required_cols = {'X', 'Y', 'id'}
    if not required_cols.issubset(df.columns):
        # Try lowercase
        df.columns = [c.lower() for c in df.columns]
        if not required_cols.issubset({c.lower() for c in ['X', 'Y', 'id']}):
            raise ValueError(f"File must contain columns: X, Y, id. Found: {list(df.columns)}")
    
    # Standardize column names
    df = df.rename(columns={c: c.lower() for c in df.columns})
    df = df.rename(columns={'x': 'X', 'y': 'Y'})
    
    return df[['id', 'X', 'Y']]

def find_nearest_edge(point: Point, G: nx.MultiDiGraph) -> Tuple[int, int, int, Point, float]:
    """
    Find the nearest edge in the graph to a given point.
    
    Args:
        point: Shapely Point (lon, lat)
        G: NetworkX graph
        
    Returns:
        Tuple of (u, v, key, snapped_point, distance)
    """
    min_dist = float('inf')
    nearest_edge = None
    snapped_point = None
    
    for u, v, key, data in G.edges(keys=True, data=True):
        # Get edge geometry
        if 'geometry' in data:
            edge_geom = data['geometry']
        else:
            # Create straight line between nodes
            u_data = G.nodes[u]
            v_data = G.nodes[v]
            edge_geom = LineString([
                (u_data['x'], u_data['y']),
                (v_data['x'], v_data['y'])
            ])
        
        # Find nearest point on this edge
        nearest_on_edge = nearest_points(point, edge_geom)[1]
        dist = point.distance(nearest_on_edge)
        
        if dist < min_dist:
            min_dist = dist
            nearest_edge = (u, v, key)
            snapped_point = nearest_on_edge
    
    return (*nearest_edge, snapped_point, min_dist)

def snap_points_to_network(points_df: pd.DataFrame, G: nx.MultiDiGraph) -> Tuple[List[Dict], nx.MultiDiGraph]:
    """
    Snap points to nearest edges in the network and optionally split edges.
    
    Args:
        points_df: DataFrame with columns id, X, Y
        G: NetworkX graph
        
    Returns:
        Tuple of (snapped_points_list, modified_graph)
    """
    snapped_points = []
    G_modified = G.copy()
    
    # Counter for new virtual nodes
    max_node_id = max(G.nodes()) if len(G.nodes()) > 0 else 0
    next_virtual_id = max_node_id + 1
    
    for idx, row in points_df.iterrows():
        point_id = int(row['id'])
        lon, lat = float(row['X']), float(row['Y'])
        point = Point(lon, lat)
        
        # Find nearest edge
        u, v, key, snapped_point, distance = find_nearest_edge(point, G_modified)
        
        # Store snapped point info
        snapped_info = {
            'id': point_id,
            'original_coords': [lon, lat],
            'snapped_coords': [snapped_point.x, snapped_point.y],
            'nearest_edge': [int(u), int(v)],
            'distance_to_edge': distance
        }
        snapped_points.append(snapped_info)
        
        # Optional: Split edge and add virtual node
        # (For TSP, we can use the snapped coordinates directly)
        # For now, we'll just store the snapped point without modifying the graph
        
    return snapped_points, G_modified

def snapped_points_to_geojson(snapped_points: List[Dict]) -> Dict[str, Any]:
    """
    Convert snapped points to GeoJSON FeatureCollection.
    
    Args:
        snapped_points: List of snapped point dictionaries
        
    Returns:
        GeoJSON FeatureCollection with Point features
    """
    features = []
    
    for point in snapped_points:
        # Original point
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': point['original_coords']
            },
            'properties': {
                'id': point['id'],
                'type': 'original',
                'snapped_lon': point['snapped_coords'][0],
                'snapped_lat': point['snapped_coords'][1]
            }
        })
        
        # Snapped point
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': point['snapped_coords']
            },
            'properties': {
                'id': point['id'],
                'type': 'snapped',
                'original_lon': point['original_coords'][0],
                'original_lat': point['original_coords'][1]
            }
        })
        
        # Line connecting original to snapped
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [
                    point['original_coords'],
                    point['snapped_coords']
                ]
            },
            'properties': {
                'id': point['id'],
                'type': 'snap_line'
            }
        })
    
    return {
        'type': 'FeatureCollection',
        'features': features
    }

