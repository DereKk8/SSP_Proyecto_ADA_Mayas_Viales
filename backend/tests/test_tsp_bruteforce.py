"""
Unit tests for TSP Brute-Force Algorithm

Tests the distance matrix computation, brute-force TSP solver,
and integration with the road network.
"""

import pytest
import networkx as nx
import numpy as np
from pathlib import Path
import time

from app.core.distance_matrix import (
    find_closest_node,
    compute_shortest_path_length,
    build_distance_matrix,
    validate_distance_matrix,
    get_shortest_path_coords
)
from app.core.tsp_bruteforce import (
    calculate_tour_length,
    solve_tsp_bruteforce,
    generate_tour_path_geojson,
    get_tour_statistics
)
from app.core.network_loader import load_osm_from_bytes
from app.core.point_snapper import load_points_from_bytes, snap_points_to_network

# Path to test data
DATA_DIR = Path(__file__).parent.parent.parent / "data"
OSM_FILE = DATA_DIR / "chapinero.osm"
POINTS_FILE = DATA_DIR / "points.tsv"


class TestDistanceMatrix:
    """Test suite for distance matrix computation."""
    
    @pytest.fixture
    def sample_graph(self):
        """Load the chapinero network for testing."""
        with open(OSM_FILE, 'rb') as f:
            osm_bytes = f.read()
        return load_osm_from_bytes(osm_bytes)
    
    @pytest.fixture
    def simple_graph(self):
        """Create a simple test graph with known distances."""
        G = nx.MultiDiGraph()
        
        # Create a simple linear graph: 0 -- 1 -- 2 -- 3
        G.add_node(0, x=-74.05, y=4.65)
        G.add_node(1, x=-74.04, y=4.65)
        G.add_node(2, x=-74.03, y=4.65)
        G.add_node(3, x=-74.02, y=4.65)
        
        # Add edges with known lengths
        G.add_edge(0, 1, key=0, length=100.0)
        G.add_edge(1, 0, key=0, length=100.0)
        G.add_edge(1, 2, key=0, length=200.0)
        G.add_edge(2, 1, key=0, length=200.0)
        G.add_edge(2, 3, key=0, length=150.0)
        G.add_edge(3, 2, key=0, length=150.0)
        
        return G
    
    def test_find_closest_node(self, simple_graph):
        """Test 1: Encontrar nodo más cercano a coordenadas dadas."""
        # Test with coordinates very close to node 1
        coords = (-74.04, 4.65)
        closest = find_closest_node(simple_graph, coords)
        assert closest == 1
        
        # Test with coordinates between nodes
        coords = (-74.045, 4.65)
        closest = find_closest_node(simple_graph, coords)
        # Should be either 0 or 1 (the two closest)
        assert closest in [0, 1]
        
        print("✓ Test passed: find_closest_node works correctly")
    
    def test_compute_shortest_path_length_simple(self, simple_graph):
        """Test 2: Calcular distancia de camino más corto."""
        # Test direct path 0 -> 1
        coords_0 = (-74.05, 4.65)
        coords_1 = (-74.04, 4.65)
        dist = compute_shortest_path_length(simple_graph, coords_0, coords_1)
        assert dist == 100.0
        
        # Test path 0 -> 3 (should be 100 + 200 + 150 = 450)
        coords_3 = (-74.02, 4.65)
        dist = compute_shortest_path_length(simple_graph, coords_0, coords_3)
        assert dist == 450.0
        
        # Test same point
        dist = compute_shortest_path_length(simple_graph, coords_0, coords_0)
        assert dist == 0.0
        
        print("✓ Test passed: shortest path computation correct")
    
    def test_build_distance_matrix_simple(self, simple_graph):
        """Test 3: Construir matriz de distancias."""
        # Create snapped points
        snapped_points = [
            {'id': 0, 'snapped_coords': [-74.05, 4.65]},
            {'id': 1, 'snapped_coords': [-74.04, 4.65]},
            {'id': 2, 'snapped_coords': [-74.02, 4.65]}
        ]
        
        matrix, point_ids = build_distance_matrix(simple_graph, snapped_points)
        
        # Verify shape
        assert matrix.shape == (3, 3)
        assert point_ids == [0, 1, 2]
        
        # Verify diagonal is zero
        assert np.allclose(np.diag(matrix), 0.0)
        
        # Verify symmetry
        assert np.allclose(matrix, matrix.T)
        
        # Verify specific distances
        # 0->1 = 100
        assert matrix[0][1] == 100.0
        # 0->2 = 100 + 200 + 150 = 450
        assert matrix[0][2] == 450.0
        # 1->2 = 200 + 150 = 350
        assert matrix[1][2] == 350.0
        
        print("✓ Test passed: distance matrix built correctly")
        print(f"  Matrix:\n{matrix}")
    
    def test_validate_distance_matrix(self, simple_graph):
        """Test 4: Validar propiedades de matriz de distancias."""
        snapped_points = [
            {'id': 0, 'snapped_coords': [-74.05, 4.65]},
            {'id': 1, 'snapped_coords': [-74.04, 4.65]},
            {'id': 2, 'snapped_coords': [-74.02, 4.65]}
        ]
        
        matrix, _ = build_distance_matrix(simple_graph, snapped_points)
        validation = validate_distance_matrix(matrix)
        
        assert validation['is_symmetric'] == True
        assert validation['diagonal_zero'] == True
        assert validation['has_negative'] == False
        assert validation['has_infinite'] == False
        assert validation['num_points'] == 3
        assert validation['min_distance'] > 0
        
        print("✓ Test passed: distance matrix validation successful")
        print(f"  Stats: {validation}")
    
    def test_distance_matrix_real_data(self, sample_graph):
        """Test 5: Matriz de distancias con datos reales (subconjunto)."""
        # Load real points
        with open(POINTS_FILE, 'rb') as f:
            points_bytes = f.read()
        
        points_df = load_points_from_bytes(points_bytes)
        
        # Use only first 5 points for speed
        points_df = points_df.head(5)
        
        # Snap to network
        snapped_points, _ = snap_points_to_network(points_df, sample_graph)
        
        # Build matrix
        start_time = time.time()
        matrix, point_ids = build_distance_matrix(sample_graph, snapped_points)
        elapsed = (time.time() - start_time) * 1000
        
        # Validate
        validation = validate_distance_matrix(matrix)
        
        assert validation['is_symmetric']
        assert validation['diagonal_zero']
        assert not validation['has_negative']
        assert matrix.shape == (5, 5)
        
        print(f"✓ Test passed: real data distance matrix")
        print(f"  Points: {len(snapped_points)}")
        print(f"  Matrix computation time: {elapsed:.2f}ms")
        print(f"  Distance range: [{validation['min_distance']:.2f}, {validation['max_distance']:.2f}] meters")


class TestTSPBruteForce:
    """Test suite for brute-force TSP algorithm."""
    
    def test_calculate_tour_length(self):
        """Test 1: Calcular longitud de tour dado."""
        # Simple 3-point distance matrix
        matrix = np.array([
            [0, 10, 20],
            [10, 0, 15],
            [20, 15, 0]
        ])
        
        # Tour: 0 -> 1 -> 2 -> 0
        tour = [0, 1, 2]
        length = calculate_tour_length(tour, matrix)
        # Should be 10 + 15 + 20 = 45
        assert length == 45.0
        
        # Different order: 0 -> 2 -> 1 -> 0
        tour = [0, 2, 1]
        length = calculate_tour_length(tour, matrix)
        # Should be 20 + 15 + 10 = 45 (same because symmetric)
        assert length == 45.0
        
        print("✓ Test passed: tour length calculation correct")
    
    def test_solve_tsp_3_points(self):
        """Test 2: Resolver TSP con 3 puntos."""
        # Create asymmetric matrix where optimal tour is clear
        matrix = np.array([
            [0, 10, 50],
            [10, 0, 20],
            [50, 20, 0]
        ])
        point_ids = [0, 1, 2]
        
        tour_ids, length, perms = solve_tsp_bruteforce(matrix, point_ids)
        
        # Verify solution
        assert len(tour_ids) == 3
        assert set(tour_ids) == {0, 1, 2}
        assert perms == 2  # (3-1)! = 2 permutations checked
        
        # Optimal tour should be 0->1->2->0 or 0->2->1->0
        # Both have length 10 + 20 + 50 = 80
        assert length == 80.0
        
        print(f"✓ Test passed: 3-point TSP solved")
        print(f"  Tour: {tour_ids}")
        print(f"  Length: {length}")
        print(f"  Permutations: {perms}")
    
    def test_solve_tsp_4_points(self):
        """Test 3: Resolver TSP con 4 puntos."""
        # Create a clear optimal tour
        matrix = np.array([
            [0, 1, 5, 5],
            [1, 0, 1, 5],
            [5, 1, 0, 1],
            [5, 5, 1, 0]
        ])
        point_ids = [10, 20, 30, 40]
        
        tour_ids, length, perms = solve_tsp_bruteforce(matrix, point_ids)
        
        assert len(tour_ids) == 4
        assert set(tour_ids) == {10, 20, 30, 40}
        assert perms == 6  # (4-1)! = 6
        
        # Optimal tour: 0->1->2->3->0 = 1+1+1+5 = 8
        # or reverse
        assert length == 8.0
        
        print(f"✓ Test passed: 4-point TSP solved")
        print(f"  Tour: {tour_ids}")
        print(f"  Length: {length}")
        print(f"  Permutations: {perms}")
    
    def test_single_point(self):
        """Test 4: Tour con un solo punto."""
        matrix = np.array([[0]])
        point_ids = [1]
        
        tour_ids, length, perms = solve_tsp_bruteforce(matrix, point_ids)
        
        assert tour_ids == [1]
        assert length == 0.0
        assert perms == 1
        
        print("✓ Test passed: single point handled correctly")
    
    def test_two_points(self):
        """Test 5: Tour con dos puntos."""
        matrix = np.array([
            [0, 100],
            [100, 0]
        ])
        point_ids = [1, 2]
        
        tour_ids, length, perms = solve_tsp_bruteforce(matrix, point_ids)
        
        assert len(tour_ids) == 2
        assert length == 200.0  # 100 + 100 (round trip)
        assert perms == 1  # (2-1)! = 1
        
        print("✓ Test passed: two points handled correctly")
    
    def test_too_many_points(self):
        """Test 6: Rechazar demasiados puntos."""
        # Create 13 points (exceeds limit of 12)
        n = 13
        matrix = np.random.rand(n, n)
        matrix = (matrix + matrix.T) / 2  # Make symmetric
        np.fill_diagonal(matrix, 0)
        point_ids = list(range(n))
        
        with pytest.raises(ValueError, match="impractical"):
            solve_tsp_bruteforce(matrix, point_ids)
        
        print("✓ Test passed: large input rejected appropriately")
    
    def test_disconnected_graph(self):
        """Test 7: Manejar grafo desconectado."""
        # Matrix with infinite distance
        matrix = np.array([
            [0, 10, np.inf],
            [10, 0, np.inf],
            [np.inf, np.inf, 0]
        ])
        point_ids = [1, 2, 3]
        
        with pytest.raises(ValueError, match="disconnected"):
            solve_tsp_bruteforce(matrix, point_ids)
        
        print("✓ Test passed: disconnected graph detected")
    
    def test_performance_scaling(self):
        """Test 8: Verificar escalamiento factorial."""
        results = []
        
        for n in [4, 5, 6, 7]:
            # Create random symmetric matrix
            matrix = np.random.rand(n, n) * 100
            matrix = (matrix + matrix.T) / 2
            np.fill_diagonal(matrix, 0)
            point_ids = list(range(n))
            
            start = time.time()
            tour_ids, length, perms = solve_tsp_bruteforce(matrix, point_ids)
            elapsed = (time.time() - start) * 1000
            
            results.append({
                'n': n,
                'perms': perms,
                'time_ms': elapsed,
                'time_per_perm': elapsed / perms if perms > 0 else 0
            })
        
        print("✓ Test passed: performance scaling")
        print("\nPerformance by number of points:")
        print("  n | permutations | time (ms) | μs/perm")
        print("  --|--------------|-----------|--------")
        for r in results:
            print(f"  {r['n']} | {r['perms']:12} | {r['time_ms']:9.2f} | {r['time_per_perm']*1000:7.2f}")


class TestTSPIntegration:
    """Integration tests with real road network data."""
    
    @pytest.fixture
    def sample_graph(self):
        """Load the chapinero network."""
        with open(OSM_FILE, 'rb') as f:
            osm_bytes = f.read()
        return load_osm_from_bytes(osm_bytes)
    
    @pytest.fixture
    def snapped_points_subset(self, sample_graph):
        """Get a small subset of snapped points."""
        with open(POINTS_FILE, 'rb') as f:
            points_bytes = f.read()
        
        points_df = load_points_from_bytes(points_bytes)
        points_df = points_df.head(6)  # Use 6 points for integration test
        
        snapped_points, G_modified = snap_points_to_network(points_df, sample_graph)
        return snapped_points, G_modified
    
    def test_end_to_end_tsp(self, snapped_points_subset):
        """Test 1: Pipeline completo end-to-end."""
        snapped_points, G = snapped_points_subset
        
        print(f"\nRunning end-to-end TSP with {len(snapped_points)} points...")
        
        # Build distance matrix
        matrix_start = time.time()
        matrix, point_ids = build_distance_matrix(G, snapped_points)
        matrix_time = (time.time() - matrix_start) * 1000
        
        # Validate matrix
        validation = validate_distance_matrix(matrix)
        assert validation['is_symmetric']
        assert validation['diagonal_zero']
        assert not validation['has_infinite']
        
        # Solve TSP
        tsp_start = time.time()
        tour_ids, length, perms = solve_tsp_bruteforce(matrix, point_ids)
        tsp_time = (time.time() - tsp_start) * 1000
        
        # Verify results
        assert len(tour_ids) == len(snapped_points)
        assert set(tour_ids) == set(point_ids)
        assert length > 0
        assert perms > 0
        
        # Get statistics
        stats = get_tour_statistics(tour_ids, matrix, point_ids)
        
        print(f"✓ Test passed: end-to-end TSP solution")
        print(f"  Points: {len(tour_ids)}")
        print(f"  Tour: {tour_ids}")
        print(f"  Total length: {length:.2f} meters")
        print(f"  Average segment: {stats['avg_segment_length']:.2f} meters")
        print(f"  Permutations checked: {perms}")
        print(f"  Matrix time: {matrix_time:.2f}ms")
        print(f"  TSP time: {tsp_time:.2f}ms")
        print(f"  Total time: {matrix_time + tsp_time:.2f}ms")
    
    def test_geojson_generation(self, snapped_points_subset):
        """Test 2: Generación de GeoJSON."""
        snapped_points, G = snapped_points_subset
        
        # Build matrix and solve
        matrix, point_ids = build_distance_matrix(G, snapped_points)
        tour_ids, length, perms = solve_tsp_bruteforce(matrix, point_ids)
        
        # Generate GeoJSON
        geojson = generate_tour_path_geojson(G, tour_ids, snapped_points, "bruteforce")
        
        # Verify structure
        assert geojson['type'] == 'Feature'
        assert 'geometry' in geojson
        assert geojson['geometry']['type'] == 'LineString'
        assert 'coordinates' in geojson['geometry']
        assert len(geojson['geometry']['coordinates']) > 0
        
        # Verify properties
        assert geojson['properties']['algorithm'] == 'bruteforce'
        assert geojson['properties']['tour'] == tour_ids
        assert geojson['properties']['num_points'] == len(tour_ids)
        
        print("✓ Test passed: GeoJSON generated correctly")
        print(f"  Coordinates in path: {len(geojson['geometry']['coordinates'])}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
