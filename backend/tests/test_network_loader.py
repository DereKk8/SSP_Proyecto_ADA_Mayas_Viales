"""
Unit tests for network_loader module.
Tests the loading and processing of OSM network files.
"""
import pytest
import networkx as nx
import os
from pathlib import Path
from app.core.network_loader import (
    load_osm_from_bytes,
    calculate_bounds,
    graph_to_geojson,
    process_network
)

# Path to test data
DATA_DIR = Path(__file__).parent.parent.parent / "data"
OSM_FILE = DATA_DIR / "chapinero.osm"


class TestNetworkLoader:
    """Test suite for network loading functionality."""
    
    @pytest.fixture
    def osm_file_bytes(self):
        """Load the chapinero OSM file as bytes for testing."""
        with open(OSM_FILE, 'rb') as f:
            return f.read()
    
    @pytest.fixture
    def sample_graph(self, osm_file_bytes):
        """Load a sample graph for testing."""
        return load_osm_from_bytes(osm_file_bytes)
    
    def test_load_osm_file(self, osm_file_bytes):
        """Test 1: Verifica carga correcta de archivo OSM válido."""
        # Load the OSM file
        G = load_osm_from_bytes(osm_file_bytes)
        
        # Verify it's a MultiDiGraph
        assert isinstance(G, nx.MultiDiGraph)
        
        # Verify it has nodes and edges
        assert G.number_of_nodes() > 0
        assert G.number_of_edges() > 0
        
        # Verify nodes have coordinates
        for node_id, data in G.nodes(data=True):
            assert 'x' in data, f"Node {node_id} missing 'x' coordinate"
            assert 'y' in data, f"Node {node_id} missing 'y' coordinate"
            assert isinstance(data['x'], (int, float))
            assert isinstance(data['y'], (int, float))
        
        # Verify edges have lengths
        for u, v, key, data in G.edges(keys=True, data=True):
            assert 'length' in data, f"Edge ({u}, {v}, {key}) missing length"
            assert data['length'] >= 0  # Some edges can have 0 length (duplicate nodes)
        
        print(f"✓ Test passed: Loaded {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    def test_calculate_bounds(self, sample_graph):
        """Test 2: Valida cálculo de límites geográficos."""
        bounds = calculate_bounds(sample_graph)
        
        # Verify all required keys exist
        required_keys = {'minLat', 'maxLat', 'minLon', 'maxLon'}
        assert required_keys.issubset(bounds.keys())
        
        # Verify bounds are valid numbers
        for key, value in bounds.items():
            assert isinstance(value, (int, float))
            assert not (value != value), f"{key} is NaN"  # Check for NaN
        
        # Verify min < max
        assert bounds['minLat'] < bounds['maxLat']
        assert bounds['minLon'] < bounds['maxLon']
        
        # Verify reasonable ranges for Bogotá coordinates
        assert 4.0 < bounds['minLat'] < 5.0
        assert 4.0 < bounds['maxLat'] < 5.0
        assert -75.0 < bounds['minLon'] < -73.0
        assert -75.0 < bounds['maxLon'] < -73.0
        
        print(f"✓ Test passed: Bounds calculated correctly")
        print(f"  Latitude: [{bounds['minLat']:.6f}, {bounds['maxLat']:.6f}]")
        print(f"  Longitude: [{bounds['minLon']:.6f}, {bounds['maxLon']:.6f}]")
    
    def test_graph_to_geojson(self, sample_graph):
        """Test 3: Comprueba conversión a formato GeoJSON."""
        geojson = graph_to_geojson(sample_graph)
        
        # Verify structure
        assert geojson['type'] == 'FeatureCollection'
        assert 'features' in geojson
        assert isinstance(geojson['features'], list)
        assert len(geojson['features']) == sample_graph.number_of_edges()
        
        # Verify each feature
        for feature in geojson['features']:
            assert feature['type'] == 'Feature'
            assert 'geometry' in feature
            assert 'properties' in feature
            
            # Check geometry
            geometry = feature['geometry']
            assert geometry['type'] == 'LineString'
            assert 'coordinates' in geometry
            assert len(geometry['coordinates']) >= 2
            
            # Verify coordinates are [lon, lat] pairs
            for coord in geometry['coordinates']:
                assert len(coord) == 2
                lon, lat = coord
                assert isinstance(lon, (int, float))
                assert isinstance(lat, (int, float))
            
            # Check properties
            props = feature['properties']
            assert 'u' in props
            assert 'v' in props
            assert 'key' in props
            assert 'length' in props
            assert props['length'] >= 0
        
        print(f"✓ Test passed: Converted {len(geojson['features'])} edges to GeoJSON")
    
    def test_empty_file(self):
        """Test 4: Manejo de archivos vacíos (excepción esperada)."""
        empty_bytes = b""
        
        # Should raise an exception when trying to parse empty file
        with pytest.raises(Exception):
            load_osm_from_bytes(empty_bytes)
        
        print("✓ Test passed: Empty file raises exception as expected")
    
    def test_process_network_complete(self, osm_file_bytes):
        """Additional test: Verifica el proceso completo de carga."""
        G, geojson, stats, bounds = process_network(osm_file_bytes)
        
        # Verify graph
        assert isinstance(G, nx.MultiDiGraph)
        assert G.number_of_nodes() > 0
        
        # Verify stats
        assert stats['nodes'] == G.number_of_nodes()
        assert stats['edges'] == G.number_of_edges()
        
        # Verify bounds
        assert 'minLat' in bounds
        assert 'maxLat' in bounds
        
        # Verify geojson
        assert geojson['type'] == 'FeatureCollection'
        assert len(geojson['features']) == G.number_of_edges()
        
        print(f"✓ Test passed: Complete network processing successful")
        print(f"  Network stats: {stats['nodes']} nodes, {stats['edges']} edges")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])

