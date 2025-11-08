# OSM TSP Routing API - Backend

FastAPI backend for solving the Traveling Salesman Problem on OpenStreetMap road networks.

## 📁 Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API route handlers
│   │   ├── network.py       # Network loading endpoints
│   │   ├── points.py        # Point snapping endpoints
│   │   ├── tsp.py           # TSP algorithm endpoints
│   │   └── export.py        # Export endpoints
│   ├── core/                # Core algorithms
│   │   ├── network_loader.py       # OSM parsing with osmnx
│   │   ├── point_snapper.py        # Point-to-edge snapping
│   │   ├── distance_matrix.py      # Shortest-path distances
│   │   ├── tsp_bruteforce.py       # Permutation-based TSP
│   │   ├── tsp_heldkarp.py         # DP with bitmask
│   │   └── tsp_heuristic.py        # 2-Opt + Nearest Neighbor
│   ├── models/              # Pydantic data models
│   │   └── network.py       # Request/response models
│   └── utils/               # Utilities
│       └── report_generator.py  # LaTeX report generation
├── tests/                   # pytest unit tests
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🚀 Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Base URL**: `http://localhost:8000`
- **API Documentation (Swagger)**: `http://localhost:8000/docs`
- **Alternative Docs (ReDoc)**: `http://localhost:8000/redoc`

## 📡 API Endpoints

### 1. Network Loading

**POST /api/network/load**

Upload an OSM file and load the road network.

**Request:**
- `osm_file`: File (multipart/form-data)

**Response:**
```json
{
  "stats": {
    "nodes": 1234,
    "edges": 2345,
    "bounds": {
      "minLat": 4.62,
      "maxLat": 4.68,
      "minLon": -74.06,
      "maxLon": -74.03
    }
  },
  "geojson": {
    "type": "FeatureCollection",
    "features": [...]
  }
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/api/network/load" \
  -F "osm_file=@data/chapinero.osm"
```

### 2. Point Snapping

**POST /api/points/snap**

Upload points file and snap them to the nearest network edges.

**Request:**
- `points_file`: File (TSV/CSV with columns: X, Y, id)
- `network_geojson`: String (GeoJSON from network load)

**Response:**
```json
{
  "snapped_points": [
    {
      "id": 0,
      "original_coords": [-74.0475, 4.6486],
      "snapped_coords": [-74.0476, 4.6487],
      "nearest_edge": [123, 456]
    },
    ...
  ],
  "geojson": {
    "type": "FeatureCollection",
    "features": [...]
  }
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/api/points/snap" \
  -F "points_file=@data/points.tsv" \
  -F "network_geojson={\"type\":\"FeatureCollection\",\"features\":[]}"
```

### 3. TSP Algorithms

#### Brute-Force TSP

**POST /api/tsp/bruteforce**

Exact solution via permutation enumeration (n ≤ 10).

#### Held-Karp TSP

**POST /api/tsp/heldkarp**

Exact solution via dynamic programming (n ≤ 20).

#### Heuristic TSP

**POST /api/tsp/heuristic**

Approximate solution via 2-Opt + Nearest Neighbor (scalable).

**Request:**
```json
{
  "point_ids": [0, 1, 2, 3, 4],
  "graph_data": {...}
}
```

**Response:**
```json
{
  "tour": [0, 2, 4, 1, 3, 0],
  "length": 5432.1,
  "runtime_ms": 12.34,
  "path_geojson": {
    "type": "Feature",
    "geometry": {
      "type": "LineString",
      "coordinates": [...]
    }
  }
}
```

### 4. Export

**POST /api/export/geojson** - Export as GeoJSON  
**POST /api/export/wkt** - Export as WKT

### 5. Health Check

**GET /health**

```json
{"status": "healthy"}
```

## 🧪 Testing

Run unit tests:

```bash
pytest tests/ -v
```

Run specific test file:

```bash
pytest tests/test_network_loader.py -v
```

Run with coverage:

```bash
pytest tests/ --cov=app --cov-report=html
```

## 🔧 Dependencies

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **NetworkX**: Graph algorithms
- **osmnx**: OSM data processing
- **Shapely**: Geometric operations
- **GeoPandas**: Geospatial data handling
- **pandas**: Data manipulation
- **pytest**: Testing framework

## 📊 Algorithms

### Network Loading
- **Input**: OSM XML file
- **Process**: Parse with osmnx, create directed graph, compute edge lengths
- **Output**: NetworkX graph + GeoJSON

### Point Snapping
- **Input**: Points (lon, lat) + Network graph
- **Process**: Find nearest edge for each point using geometric distance
- **Output**: Snapped coordinates + nearest edge IDs

### TSP Algorithms

#### 1. Brute-Force
- **Complexity**: O(n! × n²)
- **Method**: Enumerate all permutations
- **Use**: n ≤ 10, exact solution baseline

#### 2. Held-Karp DP
- **Complexity**: O(n² × 2ⁿ) time, O(n × 2ⁿ) space
- **Method**: Dynamic programming with bitmask
- **Use**: n ≤ 20, exact solution

#### 3. 2-Opt Heuristic
- **Complexity**: O(n²) + O(n² × k) refinement
- **Method**: Nearest-neighbor + 2-opt swaps
- **Use**: n > 20, approximate solution

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### CORS Issues
Update `app/main.py` to include your frontend URL in `allow_origins`.

## 📝 Development

### Adding a New Endpoint

1. Create route handler in `app/api/<module>.py`
2. Define Pydantic models in `app/models/<module>.py`
3. Implement core logic in `app/core/<module>.py`
4. Add unit tests in `tests/test_<module>.py`
5. Register router in `app/main.py`

### Code Style

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Type checking
mypy app/
```

## 🤝 Contributing

This is an academic project. For questions, contact the project maintainers.

---

**Authors**: Derek Sarmiento Loeber, Tomas Pinilla, Sebastian Sanchez  
**Course**: Algoritmos y Análisis de Algoritmos (ADA)  
**Institution**: Universidad Javeriana de Colombia

