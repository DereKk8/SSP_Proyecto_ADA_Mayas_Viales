# 🚀 Brute-Force TSP Algorithm - Beginner's Guide

**Welcome!** This document explains the brute-force TSP (Traveling Salesman Problem) implementation in simple terms, even if you're new to the project.

---

## 📚 Table of Contents
1. [What is TSP?](#what-is-tsp)
2. [What is Brute-Force?](#what-is-brute-force)
3. [How Our Implementation Works](#how-our-implementation-works)
4. [Project Structure](#project-structure)
5. [Step-by-Step Code Walkthrough](#step-by-step-code-walkthrough)
6. [How to Run Tests](#how-to-run-tests)
7. [How to Use the API](#how-to-use-the-api)
8. [Common Questions](#common-questions)

---

## 🎯 What is TSP?

### The Problem
Imagine you're a delivery driver who needs to visit 10 houses and return home. **What's the shortest route that visits all houses exactly once?**

That's the **Traveling Salesman Problem (TSP)**.

### Our Specific Challenge
- We have a **road network** (like Google Maps data)
- We have **points** (addresses/locations) on that network
- We need to find the **shortest route** that visits all points
- **Important:** We use **real road distances**, not straight-line distances!

---

## 🔨 What is Brute-Force?

### The Idea
Brute-force means "try every possible solution and pick the best one."

### Example with 4 Points (A, B, C, D)
```
Possible routes:
A → B → C → D → A  (calculate total distance)
A → B → D → C → A  (calculate total distance)
A → C → B → D → A  (calculate total distance)
A → C → D → B → A  (calculate total distance)
A → D → B → C → A  (calculate total distance)
A → D → C → B → A  (calculate total distance)

Pick the shortest one! ✓
```

### The Catch
- 4 points = 6 possible routes (manageable)
- 10 points = 362,880 possible routes (still ok)
- 12 points = 39,916,800 routes (limit!)
- **50 points = More than atoms in the universe!** (impossible)

**This is why brute-force only works for small problems (≤12 points).**

---

## 🏗️ How Our Implementation Works

### Big Picture Flow

```
1. User uploads OSM file (road network)
   ↓
2. User uploads points file (locations to visit)
   ↓
3. Points get "snapped" to nearest roads
   ↓
4. Build Distance Matrix (calculate distances between all point pairs)
   ↓
5. Run Brute-Force TSP (try all routes, find shortest)
   ↓
6. Return optimal tour + visualize on map
```

### The Two Main Steps

#### Step 1: Distance Matrix
**Purpose:** Calculate how far apart each pair of points is (using real roads).

**Why?** 
- Point A to B: 1.2 km via roads
- Point A to C: 3.5 km via roads
- Point B to C: 2.8 km via roads
- etc.

We store these in a table (matrix) so we can quickly look them up.

#### Step 2: TSP Algorithm
**Purpose:** Try all possible visiting orders and pick the shortest total distance.

**Example:**
```
Route 1: A→B→C→D→A = 1.2 + 2.8 + 1.5 + 3.0 = 8.5 km
Route 2: A→C→B→D→A = 3.5 + 2.8 + 0.8 + 3.0 = 10.1 km
Route 3: A→D→B→C→A = 3.0 + 0.8 + 2.8 + 3.5 = 10.1 km
...

Best route: Route 1 (8.5 km) ✓
```

---

## 📁 Project Structure

Here's where everything lives in the project:

```
SSP_Proyecto_ADA_Mayas_Viales/
│
├── backend/                              ← Python/FastAPI backend
│   ├── app/
│   │   ├── core/                         ← Core algorithms (our code!)
│   │   │   ├── distance_matrix.py        ← STEP 1: Calculate distances
│   │   │   ├── tsp_bruteforce.py         ← STEP 2: Find optimal tour
│   │   │   ├── network_loader.py         ← (Already existed) Load roads
│   │   │   └── point_snapper.py          ← (Already existed) Snap points
│   │   │
│   │   ├── api/                          ← API endpoints
│   │   │   └── tsp.py                    ← API: POST /api/tsp/bruteforce
│   │   │
│   │   └── models/                       ← Data structures
│   │       └── network.py                ← Request/response formats
│   │
│   ├── tests/                            ← Unit tests
│   │   ├── test_tsp_bruteforce.py        ← Tests for our implementation
│   │   ├── test_network_loader.py        ← (Already existed)
│   │   └── test_point_snapper.py         ← (Already existed)
│   │
│   ├── manual_test_tsp.py                ← Script to test manually
│   └── requirements.txt                  ← Python packages needed
│
├── data/                                 ← Test data
│   ├── chapinero.osm                     ← Road network (Bogotá)
│   └── points.tsv                        ← 50 test points
│
├── exports/                              ← Generated output files
│   ├── tsp_bruteforce_5pts.geojson       ← Results for 5 points
│   ├── tsp_bruteforce_7pts.geojson       ← Results for 7 points
│   └── tsp_bruteforce_9pts.geojson       ← Results for 9 points
│
└── App/routingapp/                       ← Next.js frontend (not today's focus)
```

---

## 🔍 Step-by-Step Code Walkthrough

### File 1: `distance_matrix.py` (Step 1: Calculate Distances)

**Location:** `backend/app/core/distance_matrix.py`

**What it does:** Calculates the shortest path distance between every pair of points.

#### Key Functions:

```python
# Function 1: Find closest road node to a GPS coordinate
def find_closest_node(G, coords):
    """
    Input: GPS coordinates (longitude, latitude)
    Output: ID of nearest node in the road network
    
    Why? Points might be slightly off the road, we need to 
    find the actual road node closest to them.
    """
```

```python
# Function 2: Calculate shortest path distance between two points
def compute_shortest_path_length(G, source_coords, target_coords):
    """
    Input: Two GPS coordinates
    Output: Distance in meters following roads
    
    How? Uses Dijkstra's algorithm (like Google Maps pathfinding)
    """
```

```python
# Function 3: Build the full distance matrix
def build_distance_matrix(G, snapped_points):
    """
    Input: Road network + list of points
    Output: Table of distances between all point pairs
    
    Example output for 3 points:
         Point0  Point1  Point2
    Point0   0     1200    3500
    Point1  1200    0      2800
    Point2  3500   2800     0
    
    Note: Diagonal is always 0 (distance from point to itself)
          Matrix is symmetric (A→B = B→A for our roads)
    """
```

**Real Example:**
```python
# You have 5 points
# This builds a 5×5 matrix with 25 distance values
# But we only need to calculate 10 unique distances
# (because it's symmetric and diagonal is 0)

Distance Matrix for 5 points:
  [   0,  620, 2500, 3200, 4266]
  [ 620,    0, 1800, 2600, 3646]
  [2500, 1800,    0,  800, 1846]
  [3200, 2600,  800,    0, 1046]
  [4266, 3646, 1846, 1046,    0]
```

---

### File 2: `tsp_bruteforce.py` (Step 2: Find Optimal Tour)

**Location:** `backend/app/core/tsp_bruteforce.py`

**What it does:** Tries all possible routes and picks the shortest one.

#### Key Functions:

```python
# Function 1: Calculate total length of one route
def calculate_tour_length(tour, distance_matrix):
    """
    Input: 
      - tour = [0, 2, 1, 3] (order to visit points)
      - distance_matrix = the table from Step 1
    
    Output: Total distance in meters
    
    Example:
      tour = [0, 2, 1, 3]
      
      Distances:
      0→2: 2500m
      2→1: 1800m
      1→3: 2600m
      3→0: 3200m (back to start)
      
      Total: 10,100 meters (10.1 km)
    """
```

```python
# Function 2: Try all possible tours and find best
def solve_tsp_bruteforce(distance_matrix, point_ids):
    """
    Input: Distance matrix + list of point IDs
    Output: Best tour, its length, how many we checked
    
    How it works:
    1. Fix first point (point 0)
    2. Try all permutations of remaining points
    3. For each permutation, calculate tour length
    4. Remember the shortest one
    5. Return the winner!
    
    Example with 4 points:
    Fixed: 0
    Try: [1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]
    That's 6 permutations = (4-1)! = 3! = 6
    """
```

```python
# Function 3: Generate map visualization
def generate_tour_path_geojson(G, tour_ids, snapped_points):
    """
    Input: Road network + winning tour + point locations
    Output: GeoJSON file (for displaying on map)
    
    What it does:
    - Takes the optimal tour
    - Gets the actual road paths between points
    - Creates a file that can be displayed on a map
    - Like drawing a line on Google Maps!
    """
```

**Algorithm Visualization:**

```
Starting with 5 points: [0, 1, 2, 3, 4]

Fix point 0, permute the rest:
✓ [0, 1, 2, 3, 4] → 10,094m
✓ [0, 1, 2, 4, 3] → 12,345m
✓ [0, 1, 3, 2, 4] → 11,234m
✓ [0, 1, 3, 4, 2] → 13,456m
✓ [0, 1, 4, 2, 3] → 14,567m
✓ [0, 1, 4, 3, 2] → 12,678m
... (24 total permutations for 5 points)
✓ [0, 4, 3, 2, 1] → 9,876m ← WINNER! 🏆

Best tour: [0, 4, 3, 2, 1] with length 9,876 meters
```

---

### File 3: `tsp.py` (API Endpoint)

**Location:** `backend/app/api/tsp.py`

**What it does:** Creates a web API endpoint that other programs can call.

```python
@router.post("/bruteforce")
async def solve_bruteforce():
    """
    API Endpoint: POST /api/tsp/bruteforce
    
    What it does step by step:
    
    1. Get the cached road network and points
       (from when user uploaded files earlier)
    
    2. Check if there are too many points (>12)
       If yes → return error (would take forever!)
    
    3. Build distance matrix
       Start timer, calculate all distances, stop timer
    
    4. Solve TSP with brute-force
       Start timer, find optimal tour, stop timer
    
    5. Generate visualization (GeoJSON)
       Create file showing the path on a map
    
    6. Return results
       {
         "tour": [0, 4, 3, 2, 1],
         "length": 9876.5,
         "runtime_ms": 850.3,
         "path_geojson": {...}
       }
    """
```

**API Flow:**
```
Frontend                    Backend API                  Our Code
   |                           |                            |
   |-- POST /api/tsp/bruteforce                            |
   |                           |                            |
   |                           |-- get cached data          |
   |                           |-- validate (≤12 points?)   |
   |                           |                            |
   |                           |-- build_distance_matrix() -->
   |                           |<-- matrix                  |
   |                           |                            |
   |                           |-- solve_tsp_bruteforce() -->
   |                           |<-- best tour               |
   |                           |                            |
   |<-- results (JSON)         |                            |
   |                           |                            |
Display on map
```

---

## 🧪 How to Run Tests

### Location of Tests
**File:** `backend/tests/test_tsp_bruteforce.py`

This file contains **15 different tests** that verify our code works correctly.

### What the Tests Check

```python
# Distance Matrix Tests (5 tests)
1. ✓ Can we find the closest road node to a GPS coordinate?
2. ✓ Can we calculate shortest path between two points?
3. ✓ Can we build a complete distance matrix?
4. ✓ Is the matrix valid? (symmetric, diagonal zero, no negatives)
5. ✓ Does it work with real Chapinero data?

# TSP Algorithm Tests (8 tests)
6. ✓ Can we calculate tour length correctly?
7. ✓ Can we solve TSP for 3 points?
8. ✓ Can we solve TSP for 4 points?
9. ✓ What happens with just 1 point? (should return 0 distance)
10. ✓ What happens with 2 points? (should go there and back)
11. ✓ Do we reject too many points (>12)?
12. ✓ Do we detect disconnected roads?
13. ✓ Does performance scale as expected (factorial growth)?

# Integration Tests (2 tests)
14. ✓ Does the complete pipeline work end-to-end?
15. ✓ Can we generate valid GeoJSON for visualization?
```

### Running the Tests

#### Option 1: Run All Tests (Recommended First Time)

```bash
# 1. Open PowerShell/Terminal

# 2. Navigate to backend folder
cd C:\Users\tomas\Downloads\6to_semestre\analisis\proyecto\SSP_Proyecto_ADA_Mayas_Viales\backend

# 3. Activate virtual environment
& C:/Users/tomas/Downloads/6to_semestre/analisis/proyecto/.venv/Scripts/Activate.ps1

# 4. Run tests
python -m pytest tests/test_tsp_bruteforce.py -v
```

**Expected Output:**
```
test_find_closest_node ✓ PASSED
test_compute_shortest_path_length_simple ✓ PASSED
test_build_distance_matrix_simple ✓ PASSED
test_validate_distance_matrix ✓ PASSED
test_distance_matrix_real_data ✓ PASSED
test_calculate_tour_length ✓ PASSED
test_solve_tsp_3_points ✓ PASSED
test_solve_tsp_4_points ✓ PASSED
test_single_point ✓ PASSED
test_two_points ✓ PASSED
test_too_many_points ✓ PASSED
test_disconnected_graph ✓ PASSED
test_performance_scaling ✓ PASSED
test_end_to_end_tsp ✓ PASSED
test_geojson_generation ✓ PASSED

==================== 15 passed in 30.56s ====================
```

#### Option 2: Run Tests with Output (See More Details)

```bash
python -m pytest tests/test_tsp_bruteforce.py -v -s
```

The `-s` flag shows print statements, so you'll see:
```
✓ Test passed: 3-point TSP solved
  Tour: [0, 1, 2]
  Length: 80.0
  Permutations: 2
```

#### Option 3: Run Just One Test

```bash
# Run only the 3-point test
python -m pytest tests/test_tsp_bruteforce.py::TestTSPBruteForce::test_solve_tsp_3_points -v -s
```

#### Option 4: Run Integration Test Script

```bash
# This runs a complete end-to-end test with real data
python manual_test_tsp.py
```

**What it does:**
- Loads Chapinero road network
- Tests with 5, 7, and 9 points
- Shows performance for each
- Generates GeoJSON files you can visualize

**Expected Output:**
```
======================================================================
TSP BRUTE-FORCE ALGORITHM - MANUAL TEST
======================================================================

[1/5] Loading OSM network...
✓ Loaded network: 2706 nodes, 7396 edges

TESTING WITH 5 POINTS
✓ Distance matrix built: (5, 5)
  Time: 798.05ms
✓ Optimal tour found!
  Tour: [0, 4, 3, 2, 1]
  Length: 10094.26 meters (10.09 km)
  Permutations checked: 24
  
... (continues for 7 and 9 points)
```

---

## 🚀 How to Use the API

### Step 1: Start the Backend

```bash
# Option A: Use the startup script
cd C:\Users\tomas\Downloads\6to_semestre\analisis\proyecto\SSP_Proyecto_ADA_Mayas_Viales
.\start-backend.ps1

# Option B: Manual start
cd backend
& C:/Users/tomas/Downloads/6to_semestre/analisis/proyecto/.venv/Scripts/Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 2: Upload Road Network

**API Call:** `POST /api/network/load`

You can test this using:
- The frontend application (easiest)
- Postman
- curl
- Python requests

**Example with curl:**
```bash
curl -X POST http://localhost:8000/api/network/load \
  -F "osm_file=@data/chapinero.osm"
```

### Step 3: Upload and Snap Points

**API Call:** `POST /api/points/snap`

```bash
curl -X POST http://localhost:8000/api/points/snap \
  -F "points_file=@data/points.tsv"
```

⚠️ **Important:** The `points.tsv` file has 50 points, but brute-force can only handle ≤12 points!

**To test, create a smaller file:**
```bash
# Create a file with just first 7 points
head -8 data/points.tsv > data/points_small.tsv
```

Then upload `points_small.tsv` instead.

### Step 4: Solve TSP

**API Call:** `POST /api/tsp/bruteforce`

```bash
curl -X POST http://localhost:8000/api/tsp/bruteforce
```

**Response:**
```json
{
  "tour": [0, 4, 3, 1, 2, 5, 6],
  "length": 16623.51,
  "runtime_ms": 1764.79,
  "path_geojson": {
    "type": "Feature",
    "geometry": {
      "type": "LineString",
      "coordinates": [[lon, lat], [lon, lat], ...]
    },
    "properties": {
      "algorithm": "bruteforce",
      "length": 16623.51,
      "runtime_ms": 1764.79,
      "permutations_checked": 720
    }
  }
}
```

### Step 5: View Results

The frontend displays:
- The optimal route on the map (colored line)
- Total distance (in km)
- Runtime (in milliseconds)
- Which points to visit in which order

---

## ❓ Common Questions

### Q1: Why only 12 points maximum?

**A:** Factorial growth! Look at this:

```
Points | Permutations | Time
-------|--------------|----------
   5   |         24   | < 1 second
  10   |    362,880   | ~30 seconds
  12   | 39,916,800   | ~45 minutes
  15   | 1.3 billion  | ~20 days
  20   | 2.4 quintillion | thousands of years
  50   | 3.0 × 10^64  | heat death of universe
```

**Solution:** Use Held-Karp (15-20 points) or Heuristic (50+ points) algorithms.

---

### Q2: What's the difference between Euclidean and network distance?

**Euclidean (straight line):**
```
Point A to Point B = 1.5 km "as the crow flies"
```

**Network (following roads):**
```
Point A to Point B = 2.8 km following actual roads
```

We use **network distance** because that's how people actually travel!

---

### Q3: What does "snapping" points mean?

**Problem:** GPS coordinates might be slightly off the road.

```
Your point: (-74.0475, 4.6486)
Nearest road: (-74.0476, 4.6487)
```

**Snapping** moves your point to the nearest location on the road network.

**Why?** We need to calculate paths along roads, not through buildings!

---

### Q4: What is a distance matrix and why do we need it?

**Without distance matrix:**
Every time we check a route, we calculate paths:
```
Check route [0,1,2,3]:
  Calculate 0→1 path (slow)
  Calculate 1→2 path (slow)
  Calculate 2→3 path (slow)
  Calculate 3→0 path (slow)
```

**With distance matrix (built once):**
```
Build matrix once: (takes ~2 seconds for 10 points)
  0→1: 1200m
  0→2: 2500m
  0→3: 3200m
  ... (all pairs)

Then for each route:
  Look up 0→1: 1200m (instant!)
  Look up 1→2: 1800m (instant!)
  Look up 2→3:  800m (instant!)
```

**Result:** Testing 362,880 routes for 10 points takes seconds, not hours!

---

### Q5: How do I know if my test passed?

**Look for:**
- ✓ Green checkmarks
- "PASSED" next to test names
- Summary at bottom: "15 passed in XX.XXs"

**If something failed:**
- ✗ Red X marks
- "FAILED" next to test name
- Error message explaining what went wrong

---

### Q6: What if I get an error about missing packages?

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

This installs all required Python packages:
- fastapi (web framework)
- networkx (graph algorithms)
- osmnx (OpenStreetMap tools)
- pandas (data handling)
- numpy (math operations)
- pytest (testing)

---

### Q7: Where can I see the visual results?

**Three places:**

1. **Frontend Application** (recommended)
   - Start frontend: `cd App/routingapp && pnpm dev`
   - Open: http://localhost:3000
   - See the route drawn on an interactive map

2. **GeoJSON Files** (`exports/` folder)
   - Open in: geojson.io, QGIS, or any GIS software
   - Files like: `tsp_bruteforce_5pts.geojson`

3. **API Response** (for debugging)
   - The `path_geojson` field contains coordinates
   - Can copy/paste into online viewers

---

### Q8: Can I test with my own points?

**Yes!** Create a TSV file:

```tsv
X	Y	id
-74.055	4.665	1
-74.056	4.666	2
-74.057	4.667	3
```

**Format:**
- Tab-separated (or comma-separated)
- Columns: X (longitude), Y (latitude), id
- Keep it ≤ 10 points for brute-force

---

### Q9: What's the difference between the tests and manual_test_tsp.py?

**Unit Tests (`test_tsp_bruteforce.py`):**
- Fast, automated checks
- Test individual functions
- Run during development
- Example: "Does calculate_tour_length() work?"

**Manual Test (`manual_test_tsp.py`):**
- Complete end-to-end demonstration
- Uses real data (Chapinero network)
- Shows visual progress
- Generates files you can open
- Example: "Does the whole system work together?"

**Both are important!**

---

### Q10: How do I know the algorithm found the BEST solution?

**Brute-force is guaranteed optimal** because it checks EVERY possible route!

Example with 4 points:
```
✓ Checked route [0,1,2,3]: 10.5 km
✓ Checked route [0,1,3,2]: 9.8 km  ← Better!
✓ Checked route [0,2,1,3]: 11.2 km
✓ Checked route [0,2,3,1]: 10.1 km
✓ Checked route [0,3,1,2]: 12.3 km
✓ Checked route [0,3,2,1]: 9.8 km  ← Also best!

Result: 9.8 km is PROVEN to be the shortest possible!
```

**Other algorithms (Held-Karp, Heuristic) might find approximate solutions, but brute-force is 100% optimal.**

---

## 🎓 Key Concepts Summary

### 1. **Distance Matrix**
- **What:** A table of distances between all point pairs
- **Why:** So we don't recalculate paths millions of times
- **Where:** `distance_matrix.py`

### 2. **Permutations**
- **What:** All possible orderings of points
- **Example:** [1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]
- **Count:** For n points = (n-1)! permutations

### 3. **Brute-Force**
- **What:** Try every permutation, pick the best
- **Pro:** Guaranteed optimal solution
- **Con:** Slow for large n (factorial time)

### 4. **Network Distance**
- **What:** Distance following actual roads
- **How:** Using Dijkstra's shortest path algorithm
- **Why:** Real-world routing (not straight lines)

### 5. **GeoJSON**
- **What:** A file format for geographic data
- **Use:** Display routes on maps
- **Example:** Shows the line from point to point following roads

---

## 📖 Further Learning

### Understanding the Code

1. **Start with tests** - They show how functions should work
2. **Read docstrings** - Every function explains what it does
3. **Try small examples** - Use 3-4 points to understand logic
4. **Add print statements** - See what's happening step by step

### Example: Add Debug Prints

```python
# In tsp_bruteforce.py, add prints to see what's happening:

for perm in itertools.permutations(indices[1:]):
    tour = [0] + list(perm)
    length = calculate_tour_length(tour, distance_matrix)
    
    print(f"Checking tour {tour}: {length:.2f}m")  # ← Add this
    
    if length < best_length:
        print(f"  → New best! Previous: {best_length:.2f}m")  # ← Add this
        best_length = length
        best_tour = tour
```

### Complexity Analysis

**Time Complexity:** O(n! × n)
- n! permutations to check
- Each takes O(n) time to calculate length

**Space Complexity:** O(n²)
- Distance matrix stores n² values

### Algorithm Improvements (Future)

1. **Branch and Bound** - Skip routes that are already worse
2. **Dynamic Programming (Held-Karp)** - O(n² × 2ⁿ) instead of O(n!)
3. **Heuristics (2-Opt)** - O(n²) but approximate

---

## ✅ Checklist: Did You Understand?

- [ ] I can explain what TSP is
- [ ] I know why brute-force is limited to 12 points
- [ ] I understand the two main steps (distance matrix + TSP)
- [ ] I can find the code files in the project
- [ ] I can run the unit tests
- [ ] I can run the manual test
- [ ] I know how to use the API
- [ ] I understand what "network distance" means
- [ ] I can explain why we need a distance matrix

---

## 🆘 Need Help?

### Common Issues

**"Module not found" error:**
```bash
# Install dependencies
cd backend
pip install -r requirements.txt
```

**"No network loaded" error:**
```bash
# Upload network first via API or frontend
```

**"Port already in use" error:**
```bash
# Kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

**Tests failing:**
```bash
# Make sure you're in the right directory
cd backend

# Make sure virtual environment is activated
& C:/Users/tomas/Downloads/6to_semestre/analisis/proyecto/.venv/Scripts/Activate.ps1

# Run tests
python -m pytest tests/test_tsp_bruteforce.py -v
```

---

## 🎉 Congratulations!

You now understand:
- ✅ What the brute-force TSP algorithm does
- ✅ How it's implemented in our project
- ✅ Where to find all the files
- ✅ How to run and understand the tests
- ✅ How to use the API

**Next steps:**
- Run the tests yourself
- Try modifying the code (add prints, change limits)
- Implement the other algorithms (Held-Karp, Heuristic)

Happy coding! 🚀
