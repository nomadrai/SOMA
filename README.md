# SOMA — Subsurface Observation and Mission Architecture

> Detection and Characterization of Subsurface Ice in Lunar South Polar Regions Using Chandrayaan-2 Radar and Imagery Data for Landing Site and Rover Traverse Planning

---

## Overview

SOMA is a **scientifically grounded lunar mission-planning platform** that processes real Chandrayaan-2 datasets to generate actionable mission insights for the **lunar south polar region**. The platform ingests data from the Chandrayaan-2 orbiter — specifically **DFSAR** (Dual Frequency Synthetic Aperture Radar) and **OHRC** (Orbiter High Resolution Camera) instruments — alongside Digital Elevation Models (DEMs), to produce outputs that support landing site selection and rover traverse planning.

This is not a static dashboard or a mockup. Every major output is generated through **actual algorithms operating on real datasets**. The scientific processing engine is the primary product; the frontend exists to visualize and interact with its outputs.

---

## Key Capabilities

| Module                     | Description                                                          |
| -------------------------- | -------------------------------------------------------------------- |
| **Data Ingestion**         | Load, validate, and standardize DFSAR, OHRC, and DEM datasets       |
| **Radar Analysis**         | Compute CPR and DOP maps from polarimetric radar data                |
| **Ice Detection**          | Fuse multiple indicator layers to identify subsurface ice regions    |
| **Terrain Analysis**       | Derive slope, roughness, hazard, and mobility maps from DEMs         |
| **Landing Site Evaluation**| Score and rank candidate landing sites using multi-criteria analysis  |
| **Rover Traverse Planning**| Generate optimal rover routes using A* / Dijkstra pathfinding        |
| **Ice Volume Estimation**  | Estimate accessible water ice resources with uncertainty quantification |
| **Visualization**          | Interactive map-based exploration of all generated products          |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Frontend (Vite + JS)                │
│          Interactive Map • Layer Controls        │
│        Visualization • Mission Dashboard         │
└────────────────────────┬────────────────────────┘
                         │  REST API
                         ▼
┌─────────────────────────────────────────────────┐
│              Backend API (FastAPI)               │
│        Routes • Validation • Orchestration       │
│        TiTiler Tile Server (COG serving)         │
└────────────────────────┬────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────┐
│         Scientific Processing Layer              │
│  Radar • Terrain • Ice Detection • Landing Sites │
│  Rover Traverse • Volume Estimation              │
└────────────────────────┬────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────┐
│              Data Layer                          │
│      DFSAR  •  OHRC  •  DEM  •  Products        │
└─────────────────────────────────────────────────┘
```

---

## Tech Stack

### Backend
- **Python 3.11** — Core language
- **FastAPI** — REST API framework
- **Uvicorn** — ASGI server
- **TiTiler / rio-tiler** — Dynamic map tile server for Cloud-Optimized GeoTIFFs
- **Pydantic** — Data validation and serialization

### Scientific Computing & Geospatial
- **NumPy, SciPy, Pandas** — Numerical computation and data analysis
- **Scikit-learn** — Machine learning for classification and clustering
- **Rasterio / GDAL** — Raster data I/O and geospatial processing
- **GeoPandas, Shapely, PyProj** — Vector operations and coordinate transformations
- **NetworkX** — Graph-based pathfinding (A*, Dijkstra)

### Frontend
- **Vite** — Build tooling and dev server
- **Plotly** — Interactive charts and plots

### Visualization (Planned)
- **Leaflet / CesiumJS** — Interactive 2D/3D mapping
- **Matplotlib** — Scientific figure generation

### Infrastructure
- **Docker & Docker Compose** — Containerized development environment

---

## Prerequisites

Before you begin, make sure you have the following installed:

1. **Docker Desktop** (includes Docker Engine and Docker Compose)
   - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Ensure it is **running** before starting the project

2. **Git**
   - [Download Git](https://git-scm.com/downloads)

### Optional (for local IDE support)

3. **Python 3.11+** — Only needed if you want IDE autocomplete and linting to work locally
4. **Node.js 20+** — Only needed if you want to run frontend tooling outside Docker

---

## Quickstart

### 1. Clone the Repository

```bash
git clone https://github.com/nomadrai/SOMA.git
cd SOMA
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

The default `.env` values work out of the box for local development. Customize if needed:

| Variable             | Default                    | Description                       |
| -------------------- | -------------------------- | --------------------------------- |
| `ENV`                | `development`              | Environment mode                  |
| `DATA_RAW_DIR`       | `/app/data/raw`            | Raw dataset directory (in container) |
| `DATA_PROCESSED_DIR` | `/app/data/processed`      | Processed output directory        |
| `DATA_EXPORTS_DIR`   | `/app/data/exports`        | Export directory                   |
| `API_HOST`           | `0.0.0.0`                 | API bind host                      |
| `API_PORT`           | `8000`                     | API bind port                      |
| `CORS_ORIGINS`       | `http://localhost:5173`    | Allowed CORS origins               |

### 3. Start the Application

```bash
docker compose up --build
```

> **First run will take several minutes** as Docker downloads base images and installs all Python/Node dependencies. Subsequent runs will be much faster due to layer caching.

### 4. Access the Application

| Service            | URL                                      |
| ------------------ | ---------------------------------------- |
| **Frontend**       | [http://localhost:5173](http://localhost:5173) |
| **Backend API**    | [http://localhost:8000](http://localhost:8000) |
| **API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Health Check**   | [http://localhost:8000/api/health](http://localhost:8000/api/health) |

### 5. Stop the Application

```bash
# Press Ctrl+C in the terminal where docker compose is running, then:
docker compose down
```

---

## Development Workflow

### Starting and Stopping

```bash
# Start containers (use --build if Dockerfiles or dependencies changed)
docker compose up --build

# Start containers (no rebuild needed, faster)
docker compose up

# Stop and remove containers
docker compose down
```

### Live Reload

Both the backend and frontend support **hot-reloading** during development:

- **Backend:** Uses Uvicorn's `--reload` flag. Any changes to Python files in `backend/` are automatically detected and the server restarts.
- **Frontend:** Uses Vite's HMR (Hot Module Replacement). Any changes to frontend files are reflected instantly in the browser.

This works because Docker volumes mount your local source code into the containers. You edit files on your machine; the containers see the changes immediately.

### IDE Setup (Optional)

To get proper autocomplete and linting in your code editor, you can set up a local Python virtual environment. **This is purely for IDE support — the app always runs inside Docker.**

```bash
# From the SOMA root directory
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then select `./venv/bin/python` as your Python interpreter in your editor.

---

## Project Structure

```
SOMA/
├── README.md                    # This file
├── CONTEXT.md                   # Project context, specs, and scientific methodology
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Container orchestration
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
│
├── backend/
│   ├── Dockerfile               # Backend container definition
│   ├── app/
│   │   ├── main.py              # FastAPI entry point + TiTiler integration
│   │   ├── api/routes/          # API endpoint definitions
│   │   ├── core/                # Config and scientific constants
│   │   ├── services/            # Scientific processing modules
│   │   │   ├── ingestion/       # Data loading and validation
│   │   │   ├── radar/           # CPR, DOP, speckle filtering
│   │   │   ├── terrain/         # Slope, roughness, hazards
│   │   │   ├── ice_detection/   # Ice probability and classification
│   │   │   ├── landing_sites/   # Site scoring and ranking
│   │   │   ├── path_planning/   # A* / Dijkstra traverse planning
│   │   │   └── volume_estimation/ # Ice resource estimation
│   │   ├── models/              # Domain models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   └── utils/               # Shared utilities
│   └── tests/                   # Backend test suite
│       └── data/golden/         # Small real datasets for testing
│
├── frontend/
│   ├── Dockerfile               # Frontend container definition
│   ├── package.json             # Node.js dependencies
│   └── src/                     # Frontend source code
│
├── data/
│   ├── raw/                     # Original unmodified datasets (gitignored)
│   │   ├── dfsar/               # DFSAR radar products
│   │   ├── ohrc/                # OHRC imagery
│   │   └── dem/                 # Digital Elevation Models
│   ├── processed/               # Algorithm-generated products (gitignored)
│   └── exports/                 # User-exported products (gitignored)
│
├── notebooks/                   # Jupyter notebooks for exploration
├── scripts/                     # CLI scripts for standalone processing
├── docs/                        # Project documentation
└── outputs/                     # Generated maps, reports, routes (gitignored)
```

---

## Data Preparation

> **Important:** All input datasets must be pre-processed into **Cloud-Optimized GeoTIFFs (COGs)** before ingestion. The pipeline does not parse raw PDS4 archives.

Use QGIS, MIDAS, or GDAL CLI to convert raw data, then place them in:

```
data/raw/dfsar/    # DFSAR radar products
data/raw/ohrc/     # OHRC imagery
data/raw/dem/      # Digital Elevation Models
```

These directories are volume-mounted into the Docker containers and are gitignored to keep the repository lightweight.

---

## API Reference

Once the backend is running, the full interactive API documentation is available at:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Current Endpoints

| Method | Endpoint         | Description                    |
| ------ | ---------------- | ------------------------------ |
| `GET`  | `/api/health`    | Health check                   |
| `GET`  | `/api/tiles/...` | Dynamic COG tile serving (TiTiler) |

> More endpoints will be added as processing modules are implemented.

---

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Test locally with `docker compose up --build`
4. Commit and push
5. Open a Pull Request

---

## License

This project is developed for a lunar exploration hackathon. License TBD.

---

## Acknowledgments

- **ISRO / Chandrayaan-2** — DFSAR and OHRC instrument data
- **NASA LRO** — LOLA/Diviner PSR data products
- **TiTiler** — Dynamic tile serving for Cloud-Optimized GeoTIFFs
