# Quick Start Guide

## 🚀 Run the Application

### Step 1: Start the Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**

### Step 2: Start the Frontend

Open a **new terminal**:

```bash
cd App/routingapp
pnpm dev
```

Frontend will be available at: **http://localhost:3000**

### Step 3: Use the Application

1. Open your browser: **http://localhost:3000**
2. Upload the OSM file: `data/chapinero.osm`
3. Upload the points file: `data/points.tsv`
4. Watch the map display the network and points!

## ✅ Test with Example Data

The `data/` directory contains example files:
- `chapinero.osm`: Chapinero neighborhood, Bogotá
- `points.tsv`: 50 test points

## 🔗 Quick Links

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## 📝 What's Implemented

✅ **Phase 1 & 2: Complete**
- ✅ Interactive Leaflet map
- ✅ File upload (OSM + TSV)
- ✅ OSM network loading & visualization
- ✅ Point snapping & visualization
- ✅ Auto-zoom to network bounds
- ✅ No hardcoded coordinates

🚧 **Coming Next: TSP Algorithms**
- ⏳ Brute-force TSP (Phase 4)
- ⏳ Held-Karp DP (Phase 5)
- ⏳ 2-Opt Heuristic (Phase 6)

## 🎨 What You'll See

1. **Gray lines**: Road network from OSM file
2. **Blue points**: Original point locations
3. **Red points**: Snapped points on roads
4. **Thin lines**: Connections between original and snapped points

## 🐛 Troubleshooting

### Backend not starting?
```bash
# Check if port 8000 is free
lsof -i :8000

# If busy, kill the process
kill -9 <PID>
```

### Frontend not starting?
```bash
# Clear Next.js cache
cd App/routingapp
rm -rf .next
pnpm dev
```

### Map not displaying?
- Check browser console (F12)
- Verify backend is running: http://localhost:8000/health
- Check CORS settings in `backend/app/main.py`

## 🎯 Next Steps

Ready to implement TSP algorithms? Just let us know which phase to build next!

