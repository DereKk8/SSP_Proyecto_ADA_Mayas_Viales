"""
Brute-Force TSP Solver

Implements the brute-force approach to solve the Traveling Salesman Problem
by examining all possible permutations and selecting the optimal tour.

Time Complexity: O(n! × n)
Space Complexity: O(n²)

This approach is only practical for small numbers of points (n ≤ 12).
"""

import itertools
import numpy as np
import networkx as nx
from typing import List, Tuple, Dict, Any
from app.core.distance_matrix import get_shortest_path_coords


def calculate_tour_length(tour: List[int], distance_matrix: np.ndarray) -> float:
    """
    Calculate the total length of a tour including return to start.
    
    Args:
        tour: List of indices representing visit order
        distance_matrix: n×n matrix of pairwise distances
        
    Returns:
        Total tour length (sum of distances between consecutive points + return)
    """
    if len(tour) == 0:
        return 0.0
    
    if len(tour) == 1:
        return 0.0
    
    total_length = 0.0
    
    # Sum distances between consecutive points
    for i in range(len(tour) - 1):
        total_length += distance_matrix[tour[i]][tour[i + 1]]
    
    # Add distance to return to start
    total_length += distance_matrix[tour[-1]][tour[0]]
    
    return total_length


def solve_tsp_bruteforce(
    distance_matrix: np.ndarray,
    point_ids: List[int]
) -> Tuple[List[int], float, int]:
    """
    Solve TSP using brute-force approach by checking all permutations.
    
    Args:
        distance_matrix: n×n matrix of shortest path distances
        point_ids: List of point IDs corresponding to matrix rows/cols
        
    Returns:
        Tuple of (best_tour_point_ids, best_length, permutations_checked)
        - best_tour_point_ids: Ordered list of point IDs for optimal tour
        - best_length: Length of optimal tour in meters
        - permutations_checked: Number of permutations evaluated
    """
    n = len(point_ids)
    
    if n == 0:
        raise ValueError("No points provided")
    
    if n == 1:
        return [point_ids[0]], 0.0, 1
    
    if n > 12:
        raise ValueError(
            f"Brute-force TSP is impractical for {n} points (max recommended: 12). "
            f"Number of permutations would be {n}! = too many!"
        )
    
    # Check for infinite distances (disconnected graph)
    if np.any(np.isinf(distance_matrix)):
        raise ValueError("Graph contains disconnected points (infinite distances)")
    
    # Generate all permutations of indices (fixing first point to reduce by factor of n)
    # This is valid because TSP is a cycle - starting point doesn't matter
    indices = list(range(n))
    
    # Fix first point (index 0) and permute the rest
    # This reduces permutations from n! to (n-1)!
    best_tour = None
    best_length = float('inf')
    permutations_checked = 0
    
    # Generate permutations of remaining indices
    for perm in itertools.permutations(indices[1:]):
        # Create full tour with first index fixed
        tour = [0] + list(perm)
        
        # Calculate tour length
        length = calculate_tour_length(tour, distance_matrix)
        
        permutations_checked += 1
        
        # Update best tour if this one is better
        if length < best_length:
            best_length = length
            best_tour = tour
    
    # Convert indices back to point IDs
    best_tour_ids = [point_ids[i] for i in best_tour]
    
    return best_tour_ids, best_length, permutations_checked


def generate_tour_path_geojson(
    G: nx.MultiDiGraph,
    tour_point_ids: List[int],
    snapped_points: List[Dict],
    algorithm_name: str = "bruteforce"
) -> Dict[str, Any]:
    """
    Generate GeoJSON representation of the tour path.
    Uses actual shortest paths between consecutive points.
    
    Args:
        G: NetworkX graph with road network
        tour_point_ids: Ordered list of point IDs in tour
        snapped_points: List of snapped point dicts with 'id' and 'snapped_coords'
        algorithm_name: Name of algorithm for properties
        
    Returns:
        GeoJSON Feature with MultiLineString geometry
    """
    if len(tour_point_ids) == 0:
        return {
            'type': 'Feature',
            'geometry': {'type': 'LineString', 'coordinates': []},
            'properties': {'algorithm': algorithm_name, 'length': 0}
        }
    
    # Create lookup for point coordinates by ID
    point_coords = {p['id']: tuple(p['snapped_coords']) for p in snapped_points}
    
    # Build complete path coordinates
    all_coords = []
    
    # Add paths between consecutive points in tour
    for i in range(len(tour_point_ids)):
        current_id = tour_point_ids[i]
        next_id = tour_point_ids[(i + 1) % len(tour_point_ids)]  # Wrap around for last→first
        
        current_coords = point_coords[current_id]
        next_coords = point_coords[next_id]
        
        # Get actual path coordinates
        path_coords = get_shortest_path_coords(G, current_coords, next_coords)
        
        # Add to overall path (avoid duplicating points at joints)
        if i == 0:
            all_coords.extend(path_coords)
        else:
            # Skip first coordinate to avoid duplication
            all_coords.extend(path_coords[1:])
    
    return {
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': all_coords
        },
        'properties': {
            'algorithm': algorithm_name,
            'tour': tour_point_ids,
            'num_points': len(tour_point_ids)
        }
    }


def get_tour_statistics(
    tour_point_ids: List[int],
    distance_matrix: np.ndarray,
    point_ids: List[int]
) -> Dict[str, Any]:
    """
    Calculate statistics about a tour.
    
    Args:
        tour_point_ids: Ordered list of point IDs
        distance_matrix: Distance matrix
        point_ids: List of point IDs matching matrix indices
        
    Returns:
        Dict with tour statistics
    """
    if len(tour_point_ids) == 0:
        return {
            'num_points': 0,
            'total_length': 0.0,
            'avg_segment_length': 0.0,
            'min_segment_length': 0.0,
            'max_segment_length': 0.0
        }
    
    # Create mapping from point ID to matrix index
    id_to_idx = {pid: idx for idx, pid in enumerate(point_ids)}
    
    # Get indices for tour
    tour_indices = [id_to_idx[pid] for pid in tour_point_ids]
    
    # Calculate segment lengths
    segment_lengths = []
    for i in range(len(tour_indices)):
        current = tour_indices[i]
        next_point = tour_indices[(i + 1) % len(tour_indices)]
        segment_lengths.append(distance_matrix[current][next_point])
    
    total_length = sum(segment_lengths)
    
    return {
        'num_points': len(tour_point_ids),
        'total_length': total_length,
        'avg_segment_length': total_length / len(segment_lengths) if segment_lengths else 0.0,
        'min_segment_length': min(segment_lengths) if segment_lengths else 0.0,
        'max_segment_length': max(segment_lengths) if segment_lengths else 0.0,
        'segment_lengths': segment_lengths
    }
