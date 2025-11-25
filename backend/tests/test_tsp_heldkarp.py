"""
Unit tests for Held-Karp TSP algorithm.
Tests the dynamic programming implementation with bitmask.
"""
import pytest
import numpy as np
import networkx as nx
from pathlib import Path
from app.core.tsp_heldkarp import (
    solve_tsp_heldkarp,
    generate_tour_path_geojson,
    get_tour_statistics
)
from app.core.distance_matrix import build_distance_matrix
from app.core.network_loader import load_osm_from_bytes
from app.core.point_snapper import load_points_from_bytes, snap_points_to_network

# Path to test data
DATA_DIR = Path(__file__).parent.parent.parent / "data"
OSM_FILE = DATA_DIR / "chapinero.osm"
POINTS_FILE = DATA_DIR / "points.tsv"


class TestHeldKarpAlgorithm:
    """Test suite for Held-Karp TSP algorithm."""
    
    def test_single_point(self):
        """Test with single point (trivial case)."""
        distance_matrix = np.array([[0]])
        point_ids = [0]
        
        tour, length, subproblems = solve_tsp_heldkarp(distance_matrix, point_ids)
        
        assert tour == [0]
        assert length == 0.0
        assert subproblems == 1
        print("✓ Single point test passed")
    
    def test_two_points(self):
        """Test with two points."""
        distance_matrix = np.array([
            [0, 100],
            [100, 0]
        ])
        point_ids = [0, 1]
        
        tour, length, subproblems = solve_tsp_heldkarp(distance_matrix, point_ids)
        
        assert len(tour) == 2
        assert tour[0] == 0  # Should start at first point
        assert length == 200.0  # Go and return
        assert subproblems == 2
        print("✓ Two points test passed")
    
    def test_three_points_triangle(self):
        """Test with 3 points forming a triangle."""
        distance_matrix = np.array([
            [0, 10, 15],
            [10, 0, 20],
            [15, 20, 0]
        ])
        point_ids = [0, 1, 2]
        
        tour, length, subproblems = solve_tsp_heldkarp(distance_matrix, point_ids)
        
        assert len(tour) == 3
        assert tour[0] == 0
        assert set(tour) == {0, 1, 2}
        # Optimal tour: 0 -> 1 -> 2 -> 0 = 10 + 20 + 15 = 45
        assert length == 45.0
        print(f"✓ Three points test passed: tour={tour}, length={length}")
    
    def test_four_points_optimal(self):
        """Test with 4 points - verify optimal solution."""
        distance_matrix = np.array([
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ])
        point_ids = [0, 1, 2, 3]
        
        tour, length, subproblems = solve_tsp_heldkarp(distance_matrix, point_ids)
        
        assert len(tour) == 4
        assert tour[0] == 0
        assert set(tour) == {0, 1, 2, 3}
        # Optimal: 0->1->3->2->0 = 10+25+30+15 = 80
        assert length == 80.0
        assert subproblems > 0
        print(f"✓ Four points test passed: tour={tour}, length={length}, subproblems={subproblems}")
    
    def test_five_points(self):
        """Test with 5 points."""
        distance_matrix = np.array([
            [0, 10, 15, 20, 25],
            [10, 0, 35, 25, 30],
            [15, 35, 0, 30, 20],
            [20, 25, 30, 0, 15],
            [25, 30, 20, 15, 0]
        ])
        point_ids = [0, 1, 2, 3, 4]
        
        tour, length, subproblems = solve_tsp_heldkarp(distance_matrix, point_ids)
        
        assert len(tour) == 5
        assert tour[0] == 0
        assert set(tour) == {0, 1, 2, 3, 4}
        assert length > 0
        # Held-Karp should explore O(n × 2^n) subproblems
        assert subproblems > 0
        assert subproblems < 200  # Upper bound check
        print(f"✓ Five points test passed: length={length:.2f}, subproblems={subproblems}")
    
    def test_disconnected_graph_error(self):
        """Test that disconnected graph raises error."""
        distance_matrix = np.array([
            [0, 10, np.inf],
            [10, 0, np.inf],
            [np.inf, np.inf, 0]
        ])
        point_ids = [0, 1, 2]
        
        with pytest.raises(ValueError, match="disconnected"):
            solve_tsp_heldkarp(distance_matrix, point_ids)
        
        print("✓ Disconnected graph test passed")
    
    def test_too_many_points_error(self):
        """Test that too many points raises error."""
        n = 24  # More than recommended limit of 23
        distance_matrix = np.random.rand(n, n) * 100
        np.fill_diagonal(distance_matrix, 0)
        point_ids = list(range(n))
        
        with pytest.raises(ValueError, match="impractical"):
            solve_tsp_heldkarp(distance_matrix, point_ids)
        
        print("✓ Too many points test passed")
    
    def test_empty_points_error(self):
        """Test that empty point list raises error."""
        distance_matrix = np.array([])
        point_ids = []
        
        with pytest.raises(ValueError, match="No points"):
            solve_tsp_heldkarp(distance_matrix, point_ids)
        
        print("✓ Empty points test passed")
    
    def test_symmetric_matrix(self):
        """Test with symmetric distance matrix."""
        distance_matrix = np.array([
            [0, 10, 20, 30],
            [10, 0, 15, 25],
            [20, 15, 0, 10],
            [30, 25, 10, 0]
        ])
        point_ids = [10, 20, 30, 40]
        
        tour, length, subproblems = solve_tsp_heldkarp(distance_matrix, point_ids)
        
        assert len(tour) == 4
        assert tour[0] == 10  # First point ID
        assert set(tour) == {10, 20, 30, 40}
        assert length > 0
        print(f"✓ Symmetric matrix test passed: tour={tour}")
    
    def test_tour_statistics(self):
        """Test tour statistics calculation."""
        distance_matrix = np.array([
            [0, 10, 20],
            [10, 0, 15],
            [20, 15, 0]
        ])
        point_ids = [0, 1, 2]
        
        tour, length, _ = solve_tsp_heldkarp(distance_matrix, point_ids)
        stats = get_tour_statistics(tour, distance_matrix, point_ids)
        
        assert stats['num_points'] == 3
        assert stats['total_distance'] == length
        assert len(stats['segments']) == 3
        assert stats['avg_segment_length'] > 0
        print(f"✓ Tour statistics test passed: {stats}")
    
    @pytest.mark.slow
    def test_real_data_integration(self):
        """Integration test with real OSM data."""
        # Load network
        with open(OSM_FILE, 'rb') as f:
            osm_bytes = f.read()
        G = load_osm_from_bytes(osm_bytes)
        
        # Load and snap points (use first 8 for reasonable test time)
        with open(POINTS_FILE, 'rb') as f:
            points_bytes = f.read()
        points_df = load_points_from_bytes(points_bytes)
        points_df = points_df.head(8)
        
        snapped_points, G_modified = snap_points_to_network(points_df, G)
        
        # Build distance matrix
        distance_matrix, point_ids = build_distance_matrix(G_modified, snapped_points)
        
        # Solve with Held-Karp
        tour, length, subproblems = solve_tsp_heldkarp(distance_matrix, point_ids)
        
        assert len(tour) == 8
        assert tour[0] == point_ids[0]
        assert length > 0
        assert subproblems > 100  # Should solve many subproblems
        
        print(f"✓ Real data integration test passed")
        print(f"  Tour: {tour}")
        print(f"  Length: {length:.2f} meters ({length/1000:.2f} km)")
        print(f"  Subproblems: {subproblems}")
    
    def test_performance_scaling(self):
        """Test that performance scales as O(n² × 2^n)."""
        import time
        
        times = []
        sizes = [5, 7, 9, 11]
        
        for n in sizes:
            distance_matrix = np.random.rand(n, n) * 100
            np.fill_diagonal(distance_matrix, 0)
            # Make symmetric
            distance_matrix = (distance_matrix + distance_matrix.T) / 2
            point_ids = list(range(n))
            
            start = time.time()
            tour, length, subproblems = solve_tsp_heldkarp(distance_matrix, point_ids)
            elapsed = (time.time() - start) * 1000
            
            times.append(elapsed)
            print(f"  n={n}: {elapsed:.2f}ms, subproblems={subproblems}")
        
        # Verify exponential growth (each step should take more than previous)
        for i in range(len(times) - 1):
            assert times[i+1] > times[i]
        
        print("✓ Performance scaling test passed")
    
    def test_geojson_generation(self):
        """Test GeoJSON path generation."""
        # Load network
        with open(OSM_FILE, 'rb') as f:
            osm_bytes = f.read()
        G = load_osm_from_bytes(osm_bytes)
        
        # Load and snap points
        with open(POINTS_FILE, 'rb') as f:
            points_bytes = f.read()
        points_df = load_points_from_bytes(points_bytes)
        points_df = points_df.head(5)
        
        snapped_points, G_modified = snap_points_to_network(points_df, G)
        distance_matrix, point_ids = build_distance_matrix(G_modified, snapped_points)
        
        tour, length, _ = solve_tsp_heldkarp(distance_matrix, point_ids)
        
        # Generate GeoJSON
        geojson = generate_tour_path_geojson(G_modified, tour, snapped_points, "heldkarp")
        
        assert geojson['type'] == 'Feature'
        assert geojson['geometry']['type'] == 'LineString'
        assert len(geojson['geometry']['coordinates']) > 0
        assert geojson['properties']['algorithm'] == 'heldkarp'
        
        print(f"✓ GeoJSON generation test passed")
        print(f"  Path has {len(geojson['geometry']['coordinates'])} coordinates")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])

