from fastapi import APIRouter, HTTPException
from app.models.network import TSPResult
from app.api.points import get_cached_points, get_cached_modified_graph
from app.core.distance_matrix import build_distance_matrix, validate_distance_matrix
from app.core.tsp_bruteforce import (
    solve_tsp_bruteforce,
    generate_tour_path_geojson as generate_tour_path_geojson_bf,
    get_tour_statistics as get_tour_statistics_bf
)
from app.core.tsp_heldkarp import (
    solve_tsp_heldkarp,
    generate_tour_path_geojson as generate_tour_path_geojson_hk,
    get_tour_statistics as get_tour_statistics_hk
)
from app.core.tsp_greedy import (
    solve_tsp_greedy_with_2opt,
    generate_tour_path_geojson as generate_tour_path_geojson_greedy,
    get_tour_statistics as get_tour_statistics_greedy
)
import time

router = APIRouter()


@router.post("/bruteforce", response_model=TSPResult)
async def solve_bruteforce():
    """
    Solve TSP using brute-force algorithm.
    
    Examines all possible permutations to find the optimal tour.
    Only practical for small numbers of points (≤12).
    
    Returns:
        TSPResult with optimal tour, length, runtime, and path geometry
    """
    try:
        # Get cached graph and snapped points
        G = get_cached_modified_graph()
        snapped_points = get_cached_points()
        
        if len(snapped_points) == 0:
            raise HTTPException(
                status_code=400,
                detail="No points available. Please upload and snap points first."
            )
        
        # Auto-subset points if exceeding brute-force limit
        MAX_BRUTEFORCE_POINTS = 12
        warning_message = None
        
        if len(snapped_points) > MAX_BRUTEFORCE_POINTS:
            original_count = len(snapped_points)
            snapped_points = snapped_points[:MAX_BRUTEFORCE_POINTS]
            warning_message = (
                f"⚠️ Only the first {MAX_BRUTEFORCE_POINTS} out of {original_count} points "
                f"were used for brute-force calculation. "
                f"Points {MAX_BRUTEFORCE_POINTS + 1}-{original_count} were ignored. "
                f"For larger datasets, consider using Held-Karp or Heuristic algorithms."
            )
            print(f"⚠️ Subset applied: Using {MAX_BRUTEFORCE_POINTS}/{original_count} points")
        
        # Build distance matrix
        print(f"Building distance matrix for {len(snapped_points)} points...")
        matrix_start = time.time()
        distance_matrix, point_ids = build_distance_matrix(G, snapped_points)
        matrix_time = (time.time() - matrix_start) * 1000
        
        # Validate distance matrix
        validation = validate_distance_matrix(distance_matrix)
        print(f"Distance matrix validation: {validation}")
        
        if validation['has_infinite']:
            raise HTTPException(
                status_code=400,
                detail="Some points are not reachable from others. "
                       "The road network may be disconnected."
            )
        
        # Solve TSP using brute-force
        print(f"Solving TSP with brute-force for {len(point_ids)} points...")
        tsp_start = time.time()
        tour_ids, tour_length, perms_checked = solve_tsp_bruteforce(distance_matrix, point_ids)
        tsp_time = (time.time() - tsp_start) * 1000
        
        # Total runtime (matrix + TSP)
        total_runtime = matrix_time + tsp_time
        
        print(f"✓ Solution found!")
        print(f"  Tour: {tour_ids}")
        print(f"  Length: {tour_length:.2f} meters")
        print(f"  Permutations checked: {perms_checked}")
        print(f"  Runtime: {total_runtime:.2f}ms (matrix: {matrix_time:.2f}ms, TSP: {tsp_time:.2f}ms)")
        
        # Generate path GeoJSON
        path_geojson = generate_tour_path_geojson_bf(G, tour_ids, snapped_points, "bruteforce")
        path_geojson['properties']['length'] = tour_length
        path_geojson['properties']['runtime_ms'] = total_runtime
        path_geojson['properties']['permutations_checked'] = perms_checked
        
        # Get tour statistics
        stats = get_tour_statistics_bf(tour_ids, distance_matrix, point_ids)
        
        return TSPResult(
            tour=tour_ids,
            length=tour_length,
            runtime_ms=total_runtime,
            path_geojson=path_geojson,
            warning=warning_message
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to solve TSP: {str(e)}"
        )


@router.post("/heldkarp", response_model=TSPResult)
async def solve_heldkarp():
    """
    Solve TSP using Held-Karp dynamic programming algorithm.
    
    Uses bitmask DP to find optimal tour in O(n² × 2^n) time.
    Practical for moderate numbers of points (≤20).
    
    Returns:
        TSPResult with optimal tour, length, runtime, and path geometry
    """
    try:
        # Get cached graph and snapped points
        G = get_cached_modified_graph()
        snapped_points = get_cached_points()
        
        if len(snapped_points) == 0:
            raise HTTPException(
                status_code=400,
                detail="No points available. Please upload and snap points first."
            )
        
        # Auto-subset points if exceeding Held-Karp practical limit
        MAX_HELDKARP_POINTS = 20
        warning_message = None
        
        if len(snapped_points) > MAX_HELDKARP_POINTS:
            original_count = len(snapped_points)
            snapped_points = snapped_points[:MAX_HELDKARP_POINTS]
            warning_message = (
                f"⚠️ Only the first {MAX_HELDKARP_POINTS} out of {original_count} points "
                f"were used for Held-Karp calculation. "
                f"Points {MAX_HELDKARP_POINTS + 1}-{original_count} were ignored. "
                f"For larger datasets, consider using the Heuristic algorithm."
            )
            print(f"⚠️ Subset applied: Using {MAX_HELDKARP_POINTS}/{original_count} points")
        
        # Build distance matrix
        print(f"Building distance matrix for {len(snapped_points)} points...")
        matrix_start = time.time()
        distance_matrix, point_ids = build_distance_matrix(G, snapped_points)
        matrix_time = (time.time() - matrix_start) * 1000
        
        # Validate distance matrix
        validation = validate_distance_matrix(distance_matrix)
        print(f"Distance matrix validation: {validation}")
        
        if validation['has_infinite']:
            raise HTTPException(
                status_code=400,
                detail="Some points are not reachable from others. "
                       "The road network may be disconnected."
            )
        
        # Solve TSP using Held-Karp
        print(f"Solving TSP with Held-Karp for {len(point_ids)} points...")
        tsp_start = time.time()
        tour_ids, tour_length, subproblems_solved = solve_tsp_heldkarp(distance_matrix, point_ids)
        tsp_time = (time.time() - tsp_start) * 1000
        
        # Total runtime (matrix + TSP)
        total_runtime = matrix_time + tsp_time
        
        print(f"✓ Solution found!")
        print(f"  Tour: {tour_ids}")
        print(f"  Length: {tour_length:.2f} meters")
        print(f"  Subproblems solved: {subproblems_solved}")
        print(f"  Runtime: {total_runtime:.2f}ms (matrix: {matrix_time:.2f}ms, TSP: {tsp_time:.2f}ms)")
        
        # Generate path GeoJSON
        path_geojson = generate_tour_path_geojson_hk(G, tour_ids, snapped_points, "heldkarp")
        path_geojson['properties']['length'] = tour_length
        path_geojson['properties']['runtime_ms'] = total_runtime
        path_geojson['properties']['subproblems_solved'] = subproblems_solved
        
        # Get tour statistics
        stats = get_tour_statistics_hk(tour_ids, distance_matrix, point_ids)
        
        return TSPResult(
            tour=tour_ids,
            length=tour_length,
            runtime_ms=total_runtime,
            path_geojson=path_geojson,
            warning=warning_message
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to solve TSP: {str(e)}"
        )


@router.post("/heuristic", response_model=TSPResult)
async def solve_heuristic():
    """
    Solve TSP using Greedy Nearest Neighbor + 2-Opt heuristic.
    
    Fast approximate algorithm: O(n²) construction + O(n² × k) improvement.
    Can handle large numbers of points (100+).
    
    Returns:
        TSPResult with approximate tour, length, runtime, and path geometry
    """
    try:
        # Get cached graph and snapped points
        G = get_cached_modified_graph()
        snapped_points = get_cached_points()
        
        if len(snapped_points) == 0:
            raise HTTPException(
                status_code=400,
                detail="No points available. Please upload and snap points first."
            )
        
        # No auto-subset for greedy - it can handle many points
        # But warn if extremely large
        if len(snapped_points) > 200:
            print(f"⚠️ Large dataset: {len(snapped_points)} points. This may take a while...")
        
        # Build distance matrix
        print(f"Building distance matrix for {len(snapped_points)} points...")
        matrix_start = time.time()
        distance_matrix, point_ids = build_distance_matrix(G, snapped_points)
        matrix_time = (time.time() - matrix_start) * 1000
        
        # Validate distance matrix
        validation = validate_distance_matrix(distance_matrix)
        print(f"Distance matrix validation: {validation}")
        
        if validation['has_infinite']:
            raise HTTPException(
                status_code=400,
                detail="Some points are not reachable from others. "
                       "The road network may be disconnected."
            )
        
        # Solve TSP using Greedy + 2-Opt
        print(f"Solving TSP with Greedy+2-Opt for {len(point_ids)} points...")
        tsp_start = time.time()
        tour_ids, tour_length, stats = solve_tsp_greedy_with_2opt(
            distance_matrix, point_ids, max_iterations=1000
        )
        tsp_time = (time.time() - tsp_start) * 1000
        
        # Total runtime (matrix + TSP)
        total_runtime = matrix_time + tsp_time
        
        print(f"✓ Solution found!")
        print(f"  Tour: {tour_ids}")
        print(f"  Initial (greedy) length: {stats['greedy_length']:.2f} meters")
        print(f"  Improved length: {tour_length:.2f} meters")
        print(f"  Improvement: {stats['improvement_percent']:.2f}%")
        print(f"  2-Opt swaps: {stats['two_opt_swaps']}")
        print(f"  Runtime: {total_runtime:.2f}ms (matrix: {matrix_time:.2f}ms, TSP: {tsp_time:.2f}ms)")
        
        # Generate path GeoJSON
        path_geojson = generate_tour_path_geojson_greedy(G, tour_ids, snapped_points, "greedy+2opt")
        path_geojson['properties']['length'] = tour_length
        path_geojson['properties']['runtime_ms'] = total_runtime
        path_geojson['properties']['greedy_length'] = stats['greedy_length']
        path_geojson['properties']['improvement_percent'] = stats['improvement_percent']
        path_geojson['properties']['two_opt_swaps'] = stats['two_opt_swaps']
        
        # Get tour statistics
        tour_stats = get_tour_statistics_greedy(tour_ids, distance_matrix, point_ids)
        
        return TSPResult(
            tour=tour_ids,
            length=tour_length,
            runtime_ms=total_runtime,
            path_geojson=path_geojson,
            warning=None
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to solve TSP: {str(e)}"
        )

