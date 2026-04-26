# Running the app

## Prerequisites

The weighted graph cache must exist before starting the API. If it doesn't:

```bash
conda activate crashoutEnv
python main.py
```

This builds `cache/weightedGraph.graphml` (takes a few minutes on first run).

---

## Backend

```bash
conda activate crashoutEnv
uvicorn api:app --reload
```

The API will be available at http://localhost:8000.  
Check http://localhost:8000/health to confirm the graph loaded.

---

## Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The app will be available at http://localhost:5173.

---

## Usage

1. Open http://localhost:5173
2. Click a start point on the Atlanta map
3. Click an end point
4. Toggle "Raining conditions" if needed
5. Click **Calculate Routes**
6. The blue polyline is the fastest baseline route; the green polyline is the safer (lower crash-penalty) route
