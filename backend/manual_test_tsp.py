"""
Manual testing script for TSP Brute-Force implementation.

Tests the complete pipeline from loading network to solving TSP.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.network_loader import load_osm_from_bytes
from app.core.point_snapper import load_points_from_bytes, snap_points_to_network
from app.core.distance_matrix import build_distance_matrix, validate_distance_matrix
from app.core.tsp_bruteforce import (
    solve_tsp_bruteforce,
    generate_tour_path_geojson,
    get_tour_statistics
)
import time
import json


def main():
    """Run manual test of TSP brute-force implementation."""
    
    print("=" * 70)
    print("TSP BRUTE-FORCE ALGORITHM - MANUAL TEST")
    print("=" * 70)
    
    # Paths to data
    data_dir = Path(__file__).parent.parent / "data"
    osm_file = data_dir / "chapinero.osm"
    points_file = data_dir / "points.tsv"
    
    # 1. Load network
    print("\n[1/5] Loading OSM network...")
    with open(osm_file, 'rb') as f:
        osm_bytes = f.read()
    
    G = load_osm_from_bytes(osm_bytes)
    print(f"✓ Loaded network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # 2. Load and snap points
    print("\n[2/5] Loading and snapping points...")
    with open(points_file, 'rb') as f:
        points_bytes = f.read()
    
    points_df = load_points_from_bytes(points_bytes)
    
    # Test with different sizes
    test_sizes = [5, 7, 9]
    
    for n_points in test_sizes:
        print(f"\n{'='*70}")
        print(f"TESTING WITH {n_points} POINTS")
        print(f"{'='*70}")
        
        # Use subset
        subset_df = points_df.head(n_points)
        snapped_points, G_modified = snap_points_to_network(subset_df, G)
        print(f"✓ Snapped {len(snapped_points)} points to network")
        
        # 3. Build distance matrix
        print(f"\n[3/5] Building distance matrix...")
        matrix_start = time.time()
        distance_matrix, point_ids = build_distance_matrix(G_modified, snapped_points)
        matrix_time = (time.time() - matrix_start) * 1000
        
        # Validate matrix
        validation = validate_distance_matrix(distance_matrix)
        print(f"✓ Distance matrix built: {distance_matrix.shape}")
        print(f"  Time: {matrix_time:.2f}ms")
        print(f"  Symmetric: {validation['is_symmetric']}")
        print(f"  Min distance: {validation['min_distance']:.2f}m")
        print(f"  Max distance: {validation['max_distance']:.2f}m")
        print(f"  Avg distance: {validation['avg_distance']:.2f}m")
        
        # 4. Solve TSP
        print(f"\n[4/5] Solving TSP with brute-force...")
        tsp_start = time.time()
        tour_ids, tour_length, perms_checked = solve_tsp_bruteforce(distance_matrix, point_ids)
        tsp_time = (time.time() - tsp_start) * 1000
        
        print(f"✓ Optimal tour found!")
        print(f"  Tour: {tour_ids}")
        print(f"  Length: {tour_length:.2f} meters ({tour_length/1000:.2f} km)")
        print(f"  Permutations checked: {perms_checked:,}")
        print(f"  Time: {tsp_time:.2f}ms")
        print(f"  Total time: {matrix_time + tsp_time:.2f}ms")
        
        # 5. Generate GeoJSON
        print(f"\n[5/5] Generating path visualization...")
        geojson = generate_tour_path_geojson(G_modified, tour_ids, snapped_points, "bruteforce")
        geojson['properties']['length'] = tour_length
        geojson['properties']['runtime_ms'] = matrix_time + tsp_time
        geojson['properties']['permutations_checked'] = perms_checked
        
        print(f"✓ GeoJSON generated")
        print(f"  Path coordinates: {len(geojson['geometry']['coordinates'])}")
        
        # Get statistics
        stats = get_tour_statistics(tour_ids, distance_matrix, point_ids)
        print(f"\nTour Statistics:")
        print(f"  Points visited: {stats['num_points']}")
        print(f"  Total length: {stats['total_length']:.2f}m")
        print(f"  Avg segment: {stats['avg_segment_length']:.2f}m")
        print(f"  Min segment: {stats['min_segment_length']:.2f}m")
        print(f"  Max segment: {stats['max_segment_length']:.2f}m")
        
        # Save GeoJSON for visualization
        output_file = Path(__file__).parent.parent / "exports" / f"tsp_bruteforce_{n_points}pts.geojson"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        print(f"\n✓ Saved to: {output_file}")
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
    print("=" * 70)
    
    # Performance summary
    print("\nPERFORMANCE SUMMARY:")
    print("Points | Expected Perms | Complexity")
    print("-------|----------------|------------")
    for n in [5, 7, 9, 10, 11, 12]:
        import math
        perms = math.factorial(n-1)
        print(f"  {n:2}   | {perms:14,} | {n-1}! = {perms:,}")
    
    print("\nNote: Brute-force is practical only for n ≤ 12 points")
    print("For larger datasets, use Held-Karp or heuristic algorithms.")


if __name__ == "__main__":
    main()
