"""
Held-Karp TSP Solver with Dynamic Programming

Implements the Held-Karp algorithm using bitmask dynamic programming
to solve the Traveling Salesman Problem optimally.

Time Complexity: O(n² × 2^n)
Space Complexity: O(n × 2^n)

This approach is practical for moderate numbers of points (n ≤ 20-23).
It's exponentially faster than brute-force O(n!) but still exponential.

Reference: Held, M., & Karp, R. M. (1962). A dynamic programming approach 
to sequencing problems.
"""

import numpy as np
import networkx as nx
from typing import List, Tuple, Dict, Any
from app.core.distance_matrix import get_shortest_path_coords


def solve_tsp_heldkarp(
    distance_matrix: np.ndarray,
    point_ids: List[int]
) -> Tuple[List[int], float, int]:
    """
    Solve TSP using Held-Karp dynamic programming algorithm.
    
    Algorithm:
    - Uses bitmask to represent subsets of visited cities
    - DP state: dp[mask][i] = minimum cost to visit cities in 'mask' ending at city i
    - Builds solution bottom-up from smaller subsets to larger ones
    
    Args:
        distance_matrix: n×n matrix of shortest path distances
        point_ids: List of point IDs corresponding to matrix rows/cols
        
    Returns:
        Tuple of (best_tour_point_ids, best_length, subproblems_solved)
        - best_tour_point_ids: Ordered list of point IDs for optimal tour
        - best_length: Length of optimal tour in meters
        - subproblems_solved: Number of DP subproblems computed
    """
    n = len(point_ids)
    
    # Edge cases
    if n == 0:
        raise ValueError("No points provided")
    
    if n == 1:
        return [point_ids[0]], 0.0, 1
    
    if n == 2:
        dist = distance_matrix[0][1] + distance_matrix[1][0]
        return [point_ids[0], point_ids[1]], dist, 2
    
    if n > 23:
        raise ValueError(
            f"Held-Karp is impractical for {n} points (max recommended: 23). "
            f"Memory required would be {n * (2 ** n) * 8 / (1024**3):.2f} GB!"
        )
    
    # Check for infinite distances (disconnected graph)
    if np.any(np.isinf(distance_matrix)):
        raise ValueError("Graph contains disconnected points (infinite distances)")
    
    # Initialize DP table
    # dp[mask][i] = minimum distance to visit all cities in mask, ending at city i
    # mask is a bitmask where bit j is 1 if city j has been visited
    INF = float('inf')
    dp = {}
    parent = {}  # For path reconstruction
    subproblems_solved = 0
    
    # Base case: starting from city 0, only city 0 visited
    # mask with only bit 0 set = 1
    start_mask = 1 << 0  # Binary: 1
    dp[(start_mask, 0)] = 0
    parent[(start_mask, 0)] = None
    subproblems_solved += 1
    
    # Iterate over all possible subsets (masks) in increasing size order
    for mask in range(1, 1 << n):
        # Skip if starting city (city 0) is not in the mask
        if not (mask & (1 << 0)):
            continue
        
        # For each city i in the current mask
        for i in range(n):
            if not (mask & (1 << i)):
                continue
            
            # Skip the base case
            if mask == (1 << 0) and i == 0:
                continue
            
            # Try to reach city i from all cities j in mask \ {i}
            prev_mask = mask ^ (1 << i)  # Remove city i from mask
            
            min_dist = INF
            best_prev = None
            
            for j in range(n):
                # j must be in prev_mask and j != i
                if not (prev_mask & (1 << j)):
                    continue
                
                if (prev_mask, j) not in dp:
                    continue
                
                dist = dp[(prev_mask, j)] + distance_matrix[j][i]
                
                if dist < min_dist:
                    min_dist = dist
                    best_prev = j
            
            if min_dist < INF:
                dp[(mask, i)] = min_dist
                parent[(mask, i)] = best_prev
                subproblems_solved += 1
    
    # Find the minimum cost to visit all cities and return to start
    full_mask = (1 << n) - 1  # All bits set
    min_tour_length = INF
    last_city = None
    
    for i in range(1, n):  # Don't include city 0 as last (we return to it)
        if (full_mask, i) not in dp:
            continue
        
        # Cost to visit all cities ending at i, then return to 0
        tour_length = dp[(full_mask, i)] + distance_matrix[i][0]
        
        if tour_length < min_tour_length:
            min_tour_length = tour_length
            last_city = i
    
    if last_city is None:
        raise ValueError("Could not find valid tour (disconnected graph)")
    
    # Reconstruct the path
    tour = []
    mask = full_mask
    current = last_city
    
    while current is not None:
        tour.append(current)
        if (mask, current) not in parent:
            break
        prev = parent[(mask, current)]
        mask = mask ^ (1 << current)
        current = prev
    
    tour.reverse()
    
    # Convert indices to point IDs
    tour_ids = [point_ids[i] for i in tour]
    
    return tour_ids, min_tour_length, subproblems_solved


def generate_tour_path_geojson(
    G: nx.MultiDiGraph,
    tour_point_ids: List[int],
    snapped_points: List[Dict],
    algorithm_name: str = "heldkarp"
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
        GeoJSON Feature with LineString geometry
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
            'algorithm': algorithm_name
        }
    }


def get_tour_statistics(
    tour_ids: List[int],
    distance_matrix: np.ndarray,
    point_ids: List[int]
) -> Dict[str, Any]:
    """
    Calculate statistics about the tour.
    
    Args:
        tour_ids: List of point IDs in tour order
        distance_matrix: Distance matrix
        point_ids: List of all point IDs
        
    Returns:
        Dictionary with tour statistics
    """
    if len(tour_ids) == 0:
        return {'num_points': 0, 'segments': []}
    
    # Create ID to index mapping
    id_to_idx = {pid: idx for idx, pid in enumerate(point_ids)}
    
    # Calculate segment distances
    segments = []
    total_dist = 0
    
    for i in range(len(tour_ids)):
        from_id = tour_ids[i]
        to_id = tour_ids[(i + 1) % len(tour_ids)]
        
        from_idx = id_to_idx[from_id]
        to_idx = id_to_idx[to_id]
        
        dist = distance_matrix[from_idx][to_idx]
        segments.append({
            'from': from_id,
            'to': to_id,
            'distance': dist
        })
        total_dist += dist
    
    return {
        'num_points': len(tour_ids),
        'total_distance': total_dist,
        'segments': segments,
        'avg_segment_length': total_dist / len(segments) if segments else 0
    }

