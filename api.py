import os
import sys
from contextlib import asynccontextmanager

import osmnx as ox
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import cachingLogic
import penalty
import routing

GRAPH = None
WEIGHTED_GRAPH_PATH = "cache/weightedGraph.graphml"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global GRAPH
    if not os.path.exists(WEIGHTED_GRAPH_PATH):
        print("\nERROR: cache/weightedGraph.graphml not found.")
        print("Run 'python main.py' first to build the weighted graph.\n")
        sys.exit(1)
    print("Loading weighted graph...")
    GRAPH = cachingLogic.loadWeightedGraph(WEIGHTED_GRAPH_PATH)
    print(f"Graph loaded: {len(GRAPH.nodes)} nodes, {len(GRAPH.edges)} edges.")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "nodes": len(GRAPH.nodes), "edges": len(GRAPH.edges)}


class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    isRaining: bool = False


@app.post("/route")
def route(req: RouteRequest):
    # finalWeights mutates edge 'weight' attrs in place based on isRaining.
    # Safe for a single-threaded dev server; copy the graph if concurrency matters.
    penalty.finalWeights(GRAPH, isRaining=req.isRaining)

    start_node = ox.distance.nearest_nodes(GRAPH, req.start_lon, req.start_lat)
    end_node = ox.distance.nearest_nodes(GRAPH, req.end_lon, req.end_lat)

    baseline, safer = routing.calculate_routes(GRAPH, start_node, end_node)

    if baseline is None:
        raise HTTPException(status_code=404, detail="No route found between those points.")

    baseline_time, baseline_danger = routing.path_stats(GRAPH, baseline)
    safer_time, safer_danger = routing.path_stats(GRAPH, safer)

    def to_coords(path):
        if not path:
            return []
        return [[GRAPH.nodes[n]["y"], GRAPH.nodes[n]["x"]] for n in path]

    return {
        "baseline": {
            "coordinates": to_coords(baseline),
            "time_minutes": baseline_time,
            "danger_score": baseline_danger,
        },
        "safer": {
            "coordinates": to_coords(safer),
            "time_minutes": safer_time,
            "danger_score": safer_danger,
        },
    }
