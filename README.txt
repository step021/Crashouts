CRASHOUTS - SAFER ROUTE NAVIGATION FOR ATLANTA
================================================

DESCRIPTION
-----------
Crashouts is a safer-route navigation tool for the Atlanta metro area. Given a
start and end location, it computes two driving routes: a baseline fastest path
and a crash-penalized safer path that trades a small amount of travel time to
avoid road segments with high historical accident rates.

The backend ingests five years of Georgia crash data (2020-2024), maps each
incident to its nearest road segment using OpenStreetMap, and weights edges by
crash severity and collision type. A rain multiplier amplifies penalties when
wet-road conditions are selected. Routes are found using Dijkstra (baseline) and
A* (safer) on the weighted graph.

The frontend is a browser-based map interface. Users click two points on an
Atlanta street map, optionally toggle rain conditions, and receive both routes
drawn as colored polylines alongside a panel showing estimated travel time and
danger score for each.


INSTALLATION
------------
Prerequisites: Anaconda or Miniconda

1. Clone the repository:
   git clone https://github.com/step021/Crashouts.git
   cd Crashouts

2. Create and activate the conda environment:
   conda env create -f environment.yml
   conda activate crashoutEnv

3. Build the weighted graph cache (one-time, takes a few minutes):
   python main.py

   This downloads the Atlanta road network, maps crash records to edges, and
   writes cache/weightedGraph.graphml. Subsequent runs skip this step.

4. Install frontend dependencies:
   cd frontend
   npm install
   cd ..


EXECUTION
---------
Start the backend API (from the repo root):
   uvicorn api:app --reload

Start the frontend dev server (in a separate terminal):
   cd frontend
   npm run dev

Open http://localhost:5173 in a browser.

- Click once on the map to set a start point (blue marker)
- Click again to set an end point (second marker)
- Toggle "Raining conditions" if applicable
- Click "Calculate Routes"

The blue polyline shows the fastest baseline route; the green polyline shows the
safer route optimized to avoid high-crash segments. Travel time (minutes) and
danger score are displayed for both routes in the left panel.

A third click on the map resets to a new start point.
