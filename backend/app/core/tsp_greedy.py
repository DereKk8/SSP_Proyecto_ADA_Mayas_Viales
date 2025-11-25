"""
Greedy Nearest Neighbor TSP Solver

Implements a fast greedy heuristic that builds a tour by always visiting
the nearest unvisited city.

Time Complexity: O(n²)
Space Complexity: O(n)

This is an approximate algorithm that provides good solutions quickly but
does not guarantee optimality. Typical approximation ratio: 1.25-2x optimal.

Algorithm:
1. Start at city 0
2. Repeatedly go to the nearest unvisited city
3. Return to start city
"""

import numpy as np
import networkx as nx
from typing import List, Tuple, Dict, Any
from app.core.distance_matrix import get_shortest_path_coords


def solve_tsp_greedy_nearest_neighbor(
    distance_matrix: np.ndarray,
    point_ids: List[int]
) -> Tuple[List[int], float, int]:
    """
    Solve TSP using Greedy Nearest Neighbor heuristic.
    
    Greedy Strategy:
    - Start at first city
    - Always pick the nearest unvisited city
    - Continue until all cities visited
    - Return to start
    
    Args:
        distance_matrix: n×n matrix of shortest path distances
        point_ids: List of point IDs corresponding to matrix rows/cols
        
    Returns:
        Tuple of (tour_point_ids, tour_length, distance_queries)
        - tour_point_ids: Ordered list of point IDs in the tour
        - tour_length: Total length of tour in meters
        - distance_queries: Number of distance lookups performed
    """
    n = len(point_ids)
    
    # Edge cases
    if n == 0:
        raise ValueError("No points provided")
    
    if n == 1:
        return [point_ids[0]], 0.0, 0
    
    if n == 2:
        dist = distance_matrix[0][1] + distance_matrix[1][0]
        return [point_ids[0], point_ids[1]], dist, 2
    
    # Check for infinite distances (disconnected graph)
    if np.any(np.isinf(distance_matrix)):
        raise ValueError("Graph contains disconnected points (infinite distances)")
    
    # Greedy nearest neighbor algorithm
    visited = [False] * n
    tour = []
    current = 0  # Start at first city
    total_distance = 0.0
    distance_queries = 0
    
    # Mark starting city as visited
    visited[current] = True
    tour.append(current)
    
    # Visit n-1 remaining cities
    for _ in range(n - 1):
        nearest_city = None
        nearest_distance = float('inf')
        
        # Find nearest unvisited city
        for next_city in range(n):
            if not visited[next_city]:
                distance_queries += 1
                distance = distance_matrix[current][next_city]
                
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_city = next_city
        
        # Move to nearest city
        if nearest_city is None:
            raise ValueError("No unvisited cities found (should not happen)")
        
        visited[nearest_city] = True
        tour.append(nearest_city)
        total_distance += nearest_distance
        current = nearest_city
    
    # Return to start city
    distance_queries += 1
    total_distance += distance_matrix[current][0]
    
    # Convert indices to point IDs
    tour_ids = [point_ids[i] for i in tour]
    
    return tour_ids, total_distance, distance_queries


def improve_tour_with_2opt(
    tour: List[int],
    distance_matrix: np.ndarray,
    point_ids: List[int],
    max_iterations: int = 1000
) -> Tuple[List[int], float, int]:
    """
    Improve a tour using 2-Opt local search.
    
    2-Opt Strategy:
    - Try swapping every pair of edges
    - If swap improves tour, accept it
    - Repeat until no improvement found
    
    Args:
        tour: Initial tour (list of point IDs)
        distance_matrix: Distance matrix
        point_ids: List of all point IDs
        max_iterations: Maximum number of improvement iterations
        
    Returns:
        Tuple of (improved_tour, improved_length, swaps_made)
    """
    # Create ID to index mapping
    id_to_idx = {pid: idx for idx, pid in enumerate(point_ids)}
    
    # Convert tour IDs to indices
    tour_indices = [id_to_idx[pid] for pid in tour]
    n = len(tour_indices)
    
    def calculate_tour_length(tour_idx):
        """Calculate total tour length."""
        length = 0.0
        for i in range(n):
            length += distance_matrix[tour_idx[i]][tour_idx[(i + 1) % n]]
        return length
    
    current_tour = tour_indices[:]
    current_length = calculate_tour_length(current_tour)
    swaps_made = 0
    iterations = 0
    
    improved = True
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        
        # Try all possible 2-opt swaps
        for i in range(n - 1):
            for j in range(i + 2, n):
                # Calculate change in tour length if we swap edges
                # Current edges: (i, i+1) and (j, j+1)
                # New edges: (i, j) and (i+1, j+1)
                
                current_edges_cost = (
                    distance_matrix[current_tour[i]][current_tour[i + 1]] +
                    distance_matrix[current_tour[j]][current_tour[(j + 1) % n]]
                )
                
                new_edges_cost = (
                    distance_matrix[current_tour[i]][current_tour[j]] +
                    distance_matrix[current_tour[i + 1]][current_tour[(j + 1) % n]]
                )
                
                # If swap improves tour, apply it
                if new_edges_cost < current_edges_cost:
                    # Reverse the segment between i+1 and j
                    current_tour[i + 1:j + 1] = reversed(current_tour[i + 1:j + 1])
                    current_length = calculate_tour_length(current_tour)
                    swaps_made += 1
                    improved = True
                    break
            
            if improved:
                break
    
    # Convert indices back to IDs
    improved_tour_ids = [point_ids[idx] for idx in current_tour]
    
    return improved_tour_ids, current_length, swaps_made


def solve_tsp_greedy_with_2opt(
    distance_matrix: np.ndarray,
    point_ids: List[int],
    max_iterations: int = 1000
) -> Tuple[List[int], float, Dict[str, Any]]:
    """
    Solve TSP using Greedy + 2-Opt improvement.
    
    Two-phase approach:
    1. Build initial tour with greedy nearest neighbor
    2. Improve tour with 2-Opt local search
    
    Args:
        distance_matrix: n×n matrix of shortest path distances
        point_ids: List of point IDs
        max_iterations: Max 2-Opt iterations
        
    Returns:
        Tuple of (tour_ids, length, stats)
    """
    # Phase 1: Greedy construction
    greedy_tour, greedy_length, distance_queries = solve_tsp_greedy_nearest_neighbor(
        distance_matrix, point_ids
    )
    
    # Phase 2: 2-Opt improvement
    improved_tour, improved_length, swaps = improve_tour_with_2opt(
        greedy_tour, distance_matrix, point_ids, max_iterations
    )
    
    # Calculate improvement
    improvement_percent = ((greedy_length - improved_length) / greedy_length) * 100
    
    stats = {
        'greedy_length': greedy_length,
        'improved_length': improved_length,
        'improvement_percent': improvement_percent,
        'distance_queries': distance_queries,
        'two_opt_swaps': swaps
    }
    
    return improved_tour, improved_length, stats


def generate_tour_path_geojson(
    G: nx.MultiDiGraph,
    tour_point_ids: List[int],
    snapped_points: List[Dict],
    algorithm_name: str = "greedy"
) -> Dict[str, Any]:
    """
    Generate GeoJSON representation of the tour path.
    Uses actual shortest paths between consecutive points.
    
    Args:
        G: NetworkX graph with road network
        tour_point_ids: Ordered list of point IDs in tour
        snapped_points: List of snapped point dicts
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
        next_id = tour_point_ids[(i + 1) % len(tour_point_ids)]
        
        current_coords = point_coords[current_id]
        next_coords = point_coords[next_id]
        
        # Get actual path coordinates
        path_coords = get_shortest_path_coords(G, current_coords, next_coords)
        
        # Add to overall path
        if i == 0:
            all_coords.extend(path_coords)
        else:
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

