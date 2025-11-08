# OSM TSP Routing Application

**ADA (Algoritmos y Análisis de Algoritmos) Project**

A full-stack web application for solving the Traveling Salesman Problem (TSP) on OpenStreetMap road networks using three different algorithmic approaches: Brute-Force, Held-Karp Dynamic Programming, and 2-Opt Heuristic.

---

## 📁 Project Structure

```
Proyecto/
├── App/
│   └── routingapp/              # Next.js Frontend
│       ├── src/
│       │   ├── app/             # Next.js App Router pages
│       │   ├── components/      # React components (Map, FileUpload, ControlPanel)
│       │   ├── types/           # TypeScript type definitions
│       │   └── utils/           # API client utilities
│       ├── public/              # Static assets
│       ├── package.json         # Frontend dependencies
│       └── next.config.ts       # Next.js configuration
│
├── backend/                     # Python FastAPI Backend
│   ├── app/
│   │   ├── api/                 # API route handlers
│   │   │   ├── network.py       # OSM network loading endpoint
│   │   │   ├── points.py        # Point snapping endpoint
│   │   │   ├── tsp.py           # TSP algorithm endpoints
│   │   │   └── export.py        # GeoJSON/WKT export endpoints
│   │   ├── core/                # Core algorithms
│   │   │   ├── network_loader.py    # OSM parsing with osmnx
│   │   │   ├── point_snapper.py     # Point-to-edge snapping
│   │   │   ├── distance_matrix.py   # Shortest-path distances
│   │   │   ├── tsp_bruteforce.py    # Permutation-based TSP
│   │   │   ├── tsp_heldkarp.py      # DP with bitmask
│   │   │   └── tsp_heuristic.py     # 2-Opt + Nearest Neighbor
│   │   ├── models/              # Pydantic data models
│   │   └── utils/               # Report generation utilities
│   ├── tests/                   # pytest unit tests
│   ├── requirements.txt         # Python dependencies
│   └── README.md                # Backend API documentation
│
├── data/                        # Test data (OSM files, TSV points)
│   ├── chapinero.osm            # Example: Chapinero, Bogotá network
│   └── points.tsv               # Example: 50 test points
│
├── report/                      # LaTeX technical report
│   ├── main.tex                 # Master LaTeX document
│   ├── sections/                # Auto-generated use case sections
│   └── figures/                 # Runtime plots, maps
│
├── exports/                     # Generated exports (GeoJSON, WKT)
│
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 20+ and **pnpm** (for frontend)
- **Python** 3.11+ (for backend)
- **Git**

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Proyecto
```

### 2. Setup Frontend

```bash
cd App/routingapp
pnpm install
pnpm dev
```

Frontend runs at: **http://localhost:3000**

### 3. Setup Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend API runs at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs** (Swagger UI)

---

## 📚 Usage

### Step 1: Upload OSM Network File

1. Open the web application at `http://localhost:3000`
2. Drag & drop (or click to select) an OSM file (`.osm` or `.pbf`)
3. The network will load and display on the map
4. Map automatically centers on the network bounds

### Step 2: Upload Points File

1. Upload a TSV or CSV file with columns: `X`, `Y`, `id`
   - `X`: Longitude
   - `Y`: Latitude
   - `id`: Point identifier
2. Points are automatically snapped to the nearest road edges
3. Blue markers appear on the map

### Step 3: Run TSP Algorithm

Choose one of three algorithms:

- **Brute-Force**: Exhaustive search (optimal, n ≤ 10)
- **Held-Karp DP**: Dynamic programming with bitmask (optimal, n ≤ 20)
- **2-Opt Heuristic**: Approximate solution (scalable, any n)

Click **Run Algorithm** to compute the TSP tour.

### Step 4: View Results

- **Red Path**: Brute-Force result
- **Green Path**: Held-Karp result
- **Purple Path**: Heuristic result

Results display tour length (meters/km) and runtime (ms/s).

### Step 5: Export Results (Optional)

Download the network, points, and tour paths as:
- **GeoJSON**: For GIS software, web maps
- **WKT**: For spatial databases

---

## 🧪 Testing

### Backend Unit Tests

```bash
cd backend
pytest tests/ -v
```

Tests cover:
- Network loading (valid/invalid OSM files)
- Point snapping (edge cases, off-network points)
- Distance matrix (symmetry, triangle inequality)
- Algorithm correctness (small instances, known solutions)

### Frontend Testing

```bash
cd App/routingapp
pnpm lint
```

---

## 📊 Algorithms

### 1. Brute-Force TSP

- **Complexity**: O(n! × n²)
- **Method**: Enumerate all permutations, find minimum cost tour
- **Use Case**: Small instances (n ≤ 10), exact solution baseline

### 2. Held-Karp Dynamic Programming

- **Complexity**: O(n² × 2ⁿ) time, O(n × 2ⁿ) space
- **Method**: DP with bitmask to represent visited subsets
- **Use Case**: Medium instances (n ≤ 20), exact solution

### 3. 2-Opt + Nearest Neighbor Heuristic

- **Complexity**: O(n²) construction + O(n² × k) refinement
- **Method**: Greedy nearest-neighbor tour, local search with 2-opt swaps
- **Use Case**: Large instances (n > 20), approximate solution

---

## 📖 Technical Report

The LaTeX report is auto-generated after running each use case. It includes:

- **Problem Description**: Use case goals, input data summary
- **Algorithm Design**: Pseudocode, data structures
- **Complexity Analysis**: Asymptotic time/space (Big-O)
- **Implementation**: Key code snippets, libraries used
- **Testing**: Unit test descriptions, edge cases
- **Empirical Analysis**: Runtime tables, plots (time vs n)
- **Conclusions**: Scalability observations, approximation quality

Compile the report:

```bash
cd report
pdflatex main.tex
```

---

## 🛠️ Technologies

### Frontend
- **Next.js 16**: React framework with App Router
- **React 19**: UI library
- **Leaflet**: Interactive map library
- **react-leaflet**: React bindings for Leaflet
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework

### Backend
- **FastAPI**: Modern Python web framework
- **NetworkX**: Graph algorithms library
- **osmnx**: OSM data processing
- **Shapely**: Geometric operations
- **GeoPandas**: Geospatial data handling
- **pytest**: Testing framework

### Data Formats
- **OSM XML**: OpenStreetMap data
- **TSV/CSV**: Point coordinates
- **GeoJSON**: Geographic feature export
- **WKT**: Well-Known Text geometry

---

## 🎯 Key Features

✅ **Modular Design**: Upload any OSM file and point set (no hardcoded data)  
✅ **Interactive Visualization**: Pan, zoom, toggle layers  
✅ **Multiple Algorithms**: Compare exact vs. approximate solutions  
✅ **Real-time Metrics**: Tour length, runtime, approximation ratio  
✅ **Export Capabilities**: GeoJSON and WKT formats  
✅ **Comprehensive Testing**: Unit tests for all backend components  
✅ **Auto-generated Report**: LaTeX document with complexity analysis  

---

## 📝 Development Notes

### Disabling React Strict Mode

React Strict Mode is **disabled** in `next.config.ts` to prevent Leaflet map double-initialization errors. This is a known issue with React 19 + Leaflet.

### API CORS Configuration

The backend allows CORS from `http://localhost:3000` for local development. Update `app/main.py` for production deployments.

### Data Files

The `data/` directory contains example files for testing:
- `chapinero.osm`: Chapinero neighborhood, Bogotá, Colombia
- `points.tsv`: 50 random points within the network bounds

These files are **not** hardcoded in the application. Users can upload any OSM file and point set via the web UI.

---

## 🤝 Contributing

This is an academic project for ADA course evaluation. For questions or issues, contact the project maintainer.

---

## 📄 License

Academic project - Universidad Javeriana de Colombia.

---

## 👨‍🏫 Evaluation Notes for Teacher

### Project Completeness

- ✅ **Frontend**: Full-featured web UI with interactive map
- ✅ **Backend**: REST API with three TSP algorithms
- ✅ **Algorithms**: Brute-force, Held-Karp, 2-Opt implemented
- ✅ **Testing**: Comprehensive unit tests for backend
- ✅ **Report**: LaTeX document structure prepared
- ✅ **Documentation**: README with setup instructions

### Running the Application

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd App/routingapp && pnpm dev`
3. Open browser: `http://localhost:3000`
4. Upload `data/chapinero.osm` and `data/points.tsv`
5. Run each algorithm and observe results

### API Endpoints

- `POST /api/network/load`: Upload OSM file
- `POST /api/points/snap`: Upload and snap points
- `POST /api/tsp/bruteforce`: Run brute-force TSP
- `POST /api/tsp/heldkarp`: Run Held-Karp TSP
- `POST /api/tsp/heuristic`: Run 2-Opt heuristic
- `POST /api/export/geojson`: Export as GeoJSON
- `POST /api/export/wkt`: Export as WKT

Full API documentation: `http://localhost:8000/docs`

---

**Authors**: Derek Sarmiento Loeber, Tomas Pinilla, Sebastian Sanchez 
**Course**: Algoritmos y Análisis de Algoritmos (ADA)  
**Date**: November 2025

