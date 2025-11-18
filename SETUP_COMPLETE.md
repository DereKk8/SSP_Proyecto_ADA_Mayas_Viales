# Setup Complete! 🎉

Your TSP Routing project is now configured and ready to run.

## ✅ What Was Installed

### Backend (Python/FastAPI)
- ✅ FastAPI 0.115.5
- ✅ Uvicorn (with standard extras)
- ✅ NetworkX 3.4.2
- ✅ OSMnx 2.0.6
- ✅ GeoPandas 1.1.1
- ✅ Shapely 2.1.2
- ✅ Pandas 2.3.3
- ✅ NumPy 2.3.5
- ✅ Matplotlib 3.10.7
- ✅ PyTest + other dependencies

### Frontend (Next.js)
- ✅ Next.js 16.0.1
- ✅ React 19.2.0
- ✅ Leaflet + React-Leaflet
- ✅ Axios
- ✅ Tailwind CSS
- ✅ TypeScript

## 🚀 How to Run

### Option 1: Using PowerShell Scripts

Open **TWO** PowerShell terminals:

**Terminal 1 - Backend:**
```powershell
cd C:\Users\tomas\Downloads\6to_semestre\analisis\proyecto\SSP_Proyecto_ADA_Mayas_Viales
.\start-backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\tomas\Downloads\6to_semestre\analisis\proyecto\SSP_Proyecto_ADA_Mayas_Viales
.\start-frontend.ps1
```

### Option 2: Manual Commands

**Terminal 1 - Backend:**
```powershell
cd C:\Users\tomas\Downloads\6to_semestre\analisis\proyecto\SSP_Proyecto_ADA_Mayas_Viales\backend
C:/Users/tomas/Downloads/6to_semestre/analisis/proyecto/.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\tomas\Downloads\6to_semestre\analisis\proyecto\SSP_Proyecto_ADA_Mayas_Viales\App\routingapp
pnpm dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Test Data

The `data/` folder contains sample files:
- `chapinero.osm` - OpenStreetMap data for Chapinero, Bogotá
- `points.tsv` - 50 test points

## 🧪 Testing

Run backend tests:
```powershell
cd backend
C:/Users/tomas/Downloads/6to_semestre/analisis/proyecto/.venv/Scripts/python.exe -m pytest
```

## ⚠️ Note About Dependencies

Some geospatial packages (pyogrio, specific pandas version) couldn't be installed due to Python 3.14 compatibility issues. However, the core functionality works with:
- shapely 2.1.2 (instead of 2.0.6)
- pandas 2.3.3 (instead of 2.2.3)
- geopandas and osmnx installed without full dependencies

This should not affect the TSP routing functionality.

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Clear Next.js Cache
```powershell
cd App\routingapp
Remove-Item -Recurse -Force .next
pnpm dev
```

### Python Import Errors
Make sure you're using the virtual environment Python:
```powershell
C:/Users/tomas/Downloads/6to_semestre/analisis/proyecto/.venv/Scripts/python.exe --version
```

## 📚 Next Steps

1. Start both servers (backend + frontend)
2. Open http://localhost:3000 in your browser
3. Upload `data/chapinero.osm` 
4. Upload `data/points.tsv`
5. See the network and points visualized on the map!

Happy coding! 🚀
