"""
Distance Matrix Module

Computes shortest path distances between points on a road network.
Uses NetworkX's shortest path algorithms to build a distance matrix
for TSP computations.
"""

import networkx as nx
import numpy as np
from typing import List, Dict, Tuple, Optional
from shapely.geometry import Point


def find_closest_node(G: nx.MultiDiGraph, coords: Tuple[float, float]) -> int:
    """
    Find the closest actual node in the graph to given coordinates.
    
    Args:
        G: NetworkX MultiDiGraph with node coordinates
        coords: Tuple of (longitude, latitude)
        
    Returns:
        Node ID of the closest node
    """
    lon, lat = coords
    point = Point(lon, lat)
    
    min_dist = float('inf')
    closest_node = None
    
    for node_id, data in G.nodes(data=True):
        node_point = Point(data['x'], data['y'])
        dist = point.distance(node_point)
        
        if dist < min_dist:
            min_dist = dist
            closest_node = node_id
    
    if closest_node is None:
        raise ValueError("No nodes found in graph")
    
    return closest_node


def compute_shortest_path_length(
    G: nx.MultiDiGraph, 
    source_coords: Tuple[float, float],
    target_coords: Tuple[float, float],
    weight: str = 'length'
) -> float:
    """
    Compute shortest path length between two coordinate pairs.
    
    Args:
        G: NetworkX MultiDiGraph
        source_coords: (lon, lat) of source point
        target_coords: (lon, lat) of target point
        weight: Edge attribute to use for path length (default: 'length')
        
    Returns:
        Length of shortest path in meters
    """
    # Find closest nodes to the coordinates
    source_node = find_closest_node(G, source_coords)
    target_node = find_closest_node(G, target_coords)
    
    # Handle case where source and target are the same
    if source_node == target_node:
        return 0.0
    
    try:
        # Compute shortest path length
        path_length = nx.shortest_path_length(
            G, 
            source=source_node, 
            target=target_node, 
            weight=weight
        )
        return path_length
    except nx.NetworkXNoPath:
        # Nodes are not connected - return infinity
        return float('inf')
    except Exception as e:
        raise ValueError(f"Error computing path from {source_node} to {target_node}: {str(e)}")


def build_distance_matrix(
    G: nx.MultiDiGraph, 
    snapped_points: List[Dict],
    weight: str = 'length'
) -> Tuple[np.ndarray, List[int]]:
    """
    Build a distance matrix for all pairs of snapped points using shortest paths.
    
    Args:
        G: NetworkX MultiDiGraph with edge lengths
        snapped_points: List of dicts with 'id' and 'snapped_coords' keys
        weight: Edge attribute to use for distances (default: 'length')
        
    Returns:
        Tuple of (distance_matrix, point_ids)
        - distance_matrix: n×n numpy array of shortest path distances
        - point_ids: List of point IDs in the same order as matrix rows/cols
    """
    n = len(snapped_points)
    
    if n == 0:
        raise ValueError("No points provided")
    
    # Initialize distance matrix
    distance_matrix = np.zeros((n, n), dtype=float)
    
    # Extract point IDs and coordinates
    point_ids = [p['id'] for p in snapped_points]
    coords = [tuple(p['snapped_coords']) for p in snapped_points]
    
    # Compute pairwise distances
    for i in range(n):
        for j in range(n):
            if i == j:
                distance_matrix[i][j] = 0.0
            elif i < j:
                # Compute distance for upper triangle
                dist = compute_shortest_path_length(G, coords[i], coords[j], weight)
                distance_matrix[i][j] = dist
                distance_matrix[j][i] = dist  # Matrix is symmetric
    
    return distance_matrix, point_ids


def validate_distance_matrix(distance_matrix: np.ndarray) -> Dict[str, any]:
    """
    Validate distance matrix and return statistics.
    
    Args:
        distance_matrix: n×n distance matrix
        
    Returns:
        Dict with validation results and statistics
    """
    n = distance_matrix.shape[0]
    
    # Check symmetry
    is_symmetric = np.allclose(distance_matrix, distance_matrix.T)
    
    # Check diagonal is zero
    diagonal_zero = np.allclose(np.diag(distance_matrix), 0.0)
    
    # Check for negative values
    has_negative = np.any(distance_matrix < 0)
    
    # Check for infinite values
    has_infinite = np.any(np.isinf(distance_matrix))
    
    # Calculate statistics (excluding diagonal and infinities)
    mask = ~np.eye(n, dtype=bool) & ~np.isinf(distance_matrix)
    if np.any(mask):
        min_dist = np.min(distance_matrix[mask])
        max_dist = np.max(distance_matrix[mask])
        avg_dist = np.mean(distance_matrix[mask])
    else:
        min_dist = max_dist = avg_dist = 0.0
    
    return {
        'is_symmetric': is_symmetric,
        'diagonal_zero': diagonal_zero,
        'has_negative': has_negative,
        'has_infinite': has_infinite,
        'num_points': n,
        'min_distance': min_dist,
        'max_distance': max_dist,
        'avg_distance': avg_dist,
        'total_pairs': n * (n - 1) // 2
    }


def get_shortest_path_coords(
    G: nx.MultiDiGraph,
    source_coords: Tuple[float, float],
    target_coords: Tuple[float, float],
    weight: str = 'length'
) -> List[Tuple[float, float]]:
    """
    Get the actual coordinate sequence of the shortest path between two points.
    Useful for generating path geometry.
    
    Args:
        G: NetworkX MultiDiGraph
        source_coords: (lon, lat) of source
        target_coords: (lon, lat) of target
        weight: Edge attribute for pathfinding
        
    Returns:
        List of (lon, lat) coordinates along the path
    """
    source_node = find_closest_node(G, source_coords)
    target_node = find_closest_node(G, target_coords)
    
    if source_node == target_node:
        return [source_coords]
    
    try:
        # Get the shortest path as a list of nodes
        path = nx.shortest_path(G, source=source_node, target=target_node, weight=weight)
        
        # Convert node sequence to coordinate sequence
        coords = []
        for node in path:
            node_data = G.nodes[node]
            coords.append((node_data['x'], node_data['y']))
        
        return coords
    except nx.NetworkXNoPath:
        # Return straight line if no path exists
        return [source_coords, target_coords]
