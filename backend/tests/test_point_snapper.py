"""
Unit tests for point_snapper module.
Tests the snapping of points to the road network.
"""
import pytest
import networkx as nx
import pandas as pd
from pathlib import Path
from shapely.geometry import Point, LineString
from app.core.point_snapper import (
    load_points_from_bytes,
    find_nearest_edge,
    snap_points_to_network,
    snapped_points_to_geojson
)
from app.core.network_loader import load_osm_from_bytes

# Path to test data
DATA_DIR = Path(__file__).parent.parent.parent / "data"
OSM_FILE = DATA_DIR / "chapinero.osm"
POINTS_FILE = DATA_DIR / "points.tsv"


class TestPointSnapper:
    """Test suite for point snapping functionality."""
    
    @pytest.fixture
    def sample_graph(self):
        """Load the chapinero network for testing."""
        with open(OSM_FILE, 'rb') as f:
            osm_bytes = f.read()
        return load_osm_from_bytes(osm_bytes)
    
    @pytest.fixture
    def points_file_bytes(self):
        """Load the points TSV file as bytes."""
        with open(POINTS_FILE, 'rb') as f:
            return f.read()
    
    @pytest.fixture
    def sample_points_df(self, points_file_bytes):
        """Load sample points dataframe."""
        return load_points_from_bytes(points_file_bytes)
    
    def test_load_points_from_bytes(self, points_file_bytes):
        """Test 1: Carga correcta de archivo TSV."""
        df = load_points_from_bytes(points_file_bytes)
        
        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        
        # Verify required columns
        assert 'id' in df.columns
        assert 'X' in df.columns
        assert 'Y' in df.columns
        
        # Verify data types
        assert df['X'].dtype in [float, 'float64']
        assert df['Y'].dtype in [float, 'float64']
        
        # Verify no NaN values
        assert not df['X'].isna().any()
        assert not df['Y'].isna().any()
        assert not df['id'].isna().any()
        
        # Verify coordinates are in reasonable range for Bogotá
        assert df['X'].between(-75.0, -73.0).all(), "Longitude out of range"
        assert df['Y'].between(4.0, 5.0).all(), "Latitude out of range"
        
        print(f"✓ Test passed: Loaded {len(df)} points from TSV")
        print(f"  First point: id={df.iloc[0]['id']}, X={df.iloc[0]['X']}, Y={df.iloc[0]['Y']}")
    
    def test_snap_single_point(self, sample_graph):
        """Test 2: Snapping de un punto individual."""
        # Create a test point in the middle of the network
        # Using a point near the center of Chapinero
        test_point = Point(-74.055, 4.665)
        
        # Find nearest edge
        u, v, key, snapped_point, distance = find_nearest_edge(test_point, sample_graph)
        
        # Verify results
        assert isinstance(u, (int, np.int64))
        assert isinstance(v, (int, np.int64))
        assert isinstance(key, (int, np.int64))
        assert isinstance(snapped_point, Point)
        assert isinstance(distance, float)
        assert distance >= 0
        
        # Verify edge exists in graph
        assert sample_graph.has_edge(u, v, key)
        
        # Distance should be reasonable (less than 1km in degrees ~0.01)
        assert distance < 0.01
        
        print(f"✓ Test passed: Point snapped successfully")
        print(f"  Original: ({test_point.x:.6f}, {test_point.y:.6f})")
        print(f"  Snapped: ({snapped_point.x:.6f}, {snapped_point.y:.6f})")
        print(f"  Distance: {distance:.6f} degrees (~{distance * 111000:.2f} meters)")
        print(f"  Edge: ({u}, {v}, {key})")
    
    def test_snap_multiple_points(self, sample_graph, sample_points_df):
        """Test 3: Procesamiento de múltiples puntos."""
        # Use first 10 points for faster testing
        test_df = sample_points_df.head(10)
        
        snapped_points, G_modified = snap_points_to_network(test_df, sample_graph)
        
        # Verify results
        assert len(snapped_points) == len(test_df)
        assert isinstance(G_modified, nx.MultiDiGraph)
        
        # Verify each snapped point
        for i, point_info in enumerate(snapped_points):
            assert 'id' in point_info
            assert 'original_coords' in point_info
            assert 'snapped_coords' in point_info
            assert 'nearest_edge' in point_info
            assert 'distance_to_edge' in point_info
            
            # Verify coordinate format
            assert len(point_info['original_coords']) == 2
            assert len(point_info['snapped_coords']) == 2
            assert len(point_info['nearest_edge']) == 2
            
            # Verify distance is reasonable
            assert point_info['distance_to_edge'] >= 0
            assert point_info['distance_to_edge'] < 0.01  # Less than ~1km
        
        # Calculate statistics
        distances = [p['distance_to_edge'] for p in snapped_points]
        avg_dist = sum(distances) / len(distances)
        max_dist = max(distances)
        min_dist = min(distances)
        
        print(f"✓ Test passed: Snapped {len(snapped_points)} points")
        print(f"  Average distance: {avg_dist * 111000:.2f} meters")
        print(f"  Min distance: {min_dist * 111000:.2f} meters")
        print(f"  Max distance: {max_dist * 111000:.2f} meters")
    
    def test_point_on_edge(self, sample_graph):
        """Test 4: Punto ya ubicado sobre una arista."""
        # Get a point exactly on an edge
        first_edge = list(sample_graph.edges(keys=True, data=True))[0]
        u, v, key, data = first_edge
        
        # Get the midpoint of the edge
        u_data = sample_graph.nodes[u]
        v_data = sample_graph.nodes[v]
        
        mid_x = (u_data['x'] + v_data['x']) / 2
        mid_y = (u_data['y'] + v_data['y']) / 2
        point_on_edge = Point(mid_x, mid_y)
        
        # Snap the point
        u_snap, v_snap, key_snap, snapped_point, distance = find_nearest_edge(point_on_edge, sample_graph)
        
        # Distance should be very small (near zero)
        assert distance < 0.0001  # Very close to the edge
        
        print(f"✓ Test passed: Point on edge snapped correctly")
        print(f"  Distance to edge: {distance * 111000:.4f} meters (should be ~0)")
    
    def test_point_far_from_network(self, sample_graph):
        """Test 5: Punto muy alejado de la red."""
        # Create a point far from the network (but still in Bogotá)
        far_point = Point(-74.10, 4.70)  # Far west of Chapinero
        
        # Should still find a nearest edge
        u, v, key, snapped_point, distance = find_nearest_edge(far_point, sample_graph)
        
        # Verify it found an edge
        assert u is not None
        assert v is not None
        assert snapped_point is not None
        
        # Distance should be larger
        assert distance > 0.001  # More than ~100 meters
        
        print(f"✓ Test passed: Far point handled correctly")
        print(f"  Distance to nearest edge: {distance * 111000:.2f} meters")
    
    def test_snapped_points_to_geojson(self, sample_graph, sample_points_df):
        """Additional test: Verifica conversión a GeoJSON."""
        # Snap a few points
        test_df = sample_points_df.head(5)
        snapped_points, _ = snap_points_to_network(test_df, sample_graph)
        
        # Convert to GeoJSON
        geojson = snapped_points_to_geojson(snapped_points)
        
        # Verify structure
        assert geojson['type'] == 'FeatureCollection'
        assert 'features' in geojson
        
        # Should have 3 features per point (original, snapped, line)
        expected_features = len(snapped_points) * 3
        assert len(geojson['features']) == expected_features
        
        # Verify feature types
        feature_types = [f['properties']['type'] for f in geojson['features']]
        assert feature_types.count('original') == len(snapped_points)
        assert feature_types.count('snapped') == len(snapped_points)
        assert feature_types.count('snap_line') == len(snapped_points)
        
        print(f"✓ Test passed: Generated GeoJSON with {len(geojson['features'])} features")
    
    def test_csv_format_support(self):
        """Additional test: Verifica soporte para formato CSV."""
        # Create CSV content
        csv_content = "id,X,Y\n1,-74.055,4.665\n2,-74.056,4.666"
        csv_bytes = csv_content.encode('utf-8')
        
        # Load with automatic delimiter detection
        df = load_points_from_bytes(csv_bytes)
        
        # Verify it loaded correctly
        assert len(df) == 2
        assert 'X' in df.columns
        assert 'Y' in df.columns
        
        print(f"✓ Test passed: CSV format detected and loaded correctly")


# Import numpy for type checking
import numpy as np


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])

