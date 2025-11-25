"""
Unit tests for Greedy TSP algorithm.
Tests the nearest neighbor heuristic and 2-Opt improvement.
"""
import pytest
import numpy as np
from pathlib import Path
from app.core.tsp_greedy import (
    solve_tsp_greedy_nearest_neighbor,
    improve_tour_with_2opt,
    solve_tsp_greedy_with_2opt,
    get_tour_statistics
)
from app.core.distance_matrix import build_distance_matrix
from app.core.network_loader import load_osm_from_bytes
from app.core.point_snapper import load_points_from_bytes, snap_points_to_network

# Path to test data
DATA_DIR = Path(__file__).parent.parent.parent / "data"
OSM_FILE = DATA_DIR / "chapinero.osm"
POINTS_FILE = DATA_DIR / "points.tsv"


class TestGreedyTSP:
    """Test suite for Greedy TSP algorithm."""
    
    def test_single_point(self):
        """Test with single point (trivial case)."""
        distance_matrix = np.array([[0]])
        point_ids = [0]
        
        tour, length, queries = solve_tsp_greedy_nearest_neighbor(distance_matrix, point_ids)
        
        assert tour == [0]
        assert length == 0.0
        assert queries == 0
        print("✓ Single point test passed")
    
    def test_two_points(self):
        """Test with two points."""
        distance_matrix = np.array([
            [0, 100],
            [100, 0]
        ])
        point_ids = [0, 1]
        
        tour, length, queries = solve_tsp_greedy_nearest_neighbor(distance_matrix, point_ids)
        
        assert len(tour) == 2
        assert tour[0] == 0
        assert length == 200.0
        assert queries == 2
        print("✓ Two points test passed")
    
    def test_three_points_greedy(self):
        """Test greedy with 3 points."""
        distance_matrix = np.array([
            [0, 10, 15],
            [10, 0, 20],
            [15, 20, 0]
        ])
        point_ids = [0, 1, 2]
        
        tour, length, queries = solve_tsp_greedy_nearest_neighbor(distance_matrix, point_ids)
        
        assert len(tour) == 3
        assert tour[0] == 0
        # Greedy should go: 0 -> 1 (10) -> 2 (20) -> 0 (15) = 45
        assert set(tour) == {0, 1, 2}
        assert length == 45.0  # May not be optimal, but greedy picks nearest
        print(f"✓ Three points greedy test passed: tour={tour}, length={length}")
    
    def test_four_points_greedy(self):
        """Test greedy with 4 points."""
        distance_matrix = np.array([
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ])
        point_ids = [0, 1, 2, 3]
        
        tour, length, queries = solve_tsp_greedy_nearest_neighbor(distance_matrix, point_ids)
        
        assert len(tour) == 4
        assert tour[0] == 0
        assert set(tour) == {0, 1, 2, 3}
        assert length > 0
        # Greedy is approximate, so just check it's reasonable
        assert length < 200  # Should not be terrible
        print(f"✓ Four points greedy test passed: tour={tour}, length={length}")
    
    def test_2opt_improvement(self):
        """Test that 2-Opt improves a suboptimal tour."""
        distance_matrix = np.array([
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ])
        point_ids = [0, 1, 2, 3]
        
        # Start with a known suboptimal tour: 0 -> 1 -> 2 -> 3 -> 0
        # Length: 10 + 35 + 30 + 20 = 95
        suboptimal_tour = [0, 1, 2, 3]
        
        improved_tour, improved_length, swaps = improve_tour_with_2opt(
            suboptimal_tour, distance_matrix, point_ids
        )
        
        assert len(improved_tour) == 4
        assert set(improved_tour) == {0, 1, 2, 3}
        # Should improve to optimal: 0 -> 1 -> 3 -> 2 -> 0 = 80
        assert improved_length <= 95  # Should be better
        assert swaps > 0  # Should have made at least one swap
        print(f"✓ 2-Opt improvement test passed: {95} -> {improved_length}, swaps={swaps}")
    
    def test_greedy_with_2opt_combined(self):
        """Test combined greedy + 2-Opt."""
        distance_matrix = np.array([
            [0, 10, 15, 20, 25],
            [10, 0, 35, 25, 30],
            [15, 35, 0, 30, 20],
            [20, 25, 30, 0, 15],
            [25, 30, 20, 15, 0]
        ])
        point_ids = [0, 1, 2, 3, 4]
        
        tour, length, stats = solve_tsp_greedy_with_2opt(distance_matrix, point_ids)
        
        assert len(tour) == 5
        assert set(tour) == {0, 1, 2, 3, 4}
        assert length > 0
        assert stats['improved_length'] <= stats['greedy_length']
        assert stats['improvement_percent'] >= 0
        print(f"✓ Greedy+2-Opt test passed:")
        print(f"  Greedy: {stats['greedy_length']:.2f}")
        print(f"  Improved: {stats['improved_length']:.2f}")
        print(f"  Improvement: {stats['improvement_percent']:.2f}%")
    
    def test_disconnected_graph_error(self):
        """Test that disconnected graph raises error."""
        distance_matrix = np.array([
            [0, 10, np.inf],
            [10, 0, np.inf],
            [np.inf, np.inf, 0]
        ])
        point_ids = [0, 1, 2]
        
        with pytest.raises(ValueError, match="disconnected"):
            solve_tsp_greedy_nearest_neighbor(distance_matrix, point_ids)
        
        print("✓ Disconnected graph test passed")
    
    def test_empty_points_error(self):
        """Test that empty point list raises error."""
        distance_matrix = np.array([])
        point_ids = []
        
        with pytest.raises(ValueError, match="No points"):
            solve_tsp_greedy_nearest_neighbor(distance_matrix, point_ids)
        
        print("✓ Empty points test passed")
    
    def test_performance_on_larger_set(self):
        """Test performance on larger point set."""
        n = 30
        # Create random symmetric distance matrix
        np.random.seed(42)
        distance_matrix = np.random.rand(n, n) * 100
        distance_matrix = (distance_matrix + distance_matrix.T) / 2
        np.fill_diagonal(distance_matrix, 0)
        point_ids = list(range(n))
        
        import time
        start = time.time()
        tour, length, queries = solve_tsp_greedy_nearest_neighbor(distance_matrix, point_ids)
        elapsed = (time.time() - start) * 1000
        
        assert len(tour) == n
        assert set(tour) == set(point_ids)
        assert length > 0
        assert elapsed < 100  # Should be fast (< 100ms for 30 points)
        print(f"✓ Performance test passed: {n} points in {elapsed:.2f}ms")
    
    def test_greedy_vs_optimal_approximation(self):
        """Test that greedy provides reasonable approximation."""
        # Known case: complete graph with random distances
        distance_matrix = np.array([
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ])
        point_ids = [0, 1, 2, 3]
        
        # Optimal is 80 (0->1->3->2->0: 10+25+30+15)
        optimal_length = 80
        
        tour, length, _ = solve_tsp_greedy_nearest_neighbor(distance_matrix, point_ids)
        
        # Greedy should be within 2x of optimal (typical bound)
        approximation_ratio = length / optimal_length
        assert approximation_ratio <= 2.0
        print(f"✓ Approximation test passed: ratio={approximation_ratio:.2f}x")
    
    def test_tour_statistics(self):
        """Test tour statistics calculation."""
        distance_matrix = np.array([
            [0, 10, 20],
            [10, 0, 15],
            [20, 15, 0]
        ])
        point_ids = [0, 1, 2]
        
        tour, length, _ = solve_tsp_greedy_nearest_neighbor(distance_matrix, point_ids)
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
        
        # Load and snap points (use 20 for reasonable test time)
        with open(POINTS_FILE, 'rb') as f:
            points_bytes = f.read()
        points_df = load_points_from_bytes(points_bytes)
        points_df = points_df.head(20)
        
        snapped_points, G_modified = snap_points_to_network(points_df, G)
        
        # Build distance matrix
        distance_matrix, point_ids = build_distance_matrix(G_modified, snapped_points)
        
        # Solve with Greedy + 2-Opt
        tour, length, stats = solve_tsp_greedy_with_2opt(distance_matrix, point_ids)
        
        assert len(tour) == 20
        assert tour[0] == point_ids[0]
        assert length > 0
        assert stats['improved_length'] <= stats['greedy_length']
        
        print(f"✓ Real data integration test passed")
        print(f"  Greedy: {stats['greedy_length'] / 1000:.2f} km")
        print(f"  Improved: {stats['improved_length'] / 1000:.2f} km")
        print(f"  Improvement: {stats['improvement_percent']:.2f}%")
        print(f"  2-Opt swaps: {stats['two_opt_swaps']}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])

