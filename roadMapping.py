import os
import osmnx as ox
import pandas as pd
from shapely.geometry import Point

def loadData(path="data/CleanedCrashData.csv"):
    if not os.path.exists(path):
        raise FileNotFoundError("Crash csv not found")
    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise ValueError(f"Failed to read csv. Error is {e}")
    
    if df.empty:
        raise ValueError(f"Crash csv is empty")
    
    try:
        df["geometry"] = [Point(xy) for xy in zip(df["lon"], df["lat"])]
    except Exception as e:
        raise ValueError("Failed to create Point geometry")

    return df

def loadGraph(path="atlantaGraph.graphml"):
    if os.path.exists(path):
        return ox.load_graphml(path)
    else:
        print("Making new graph")
        graph = ox.graph_from_place("Atlanta, Georgia, USA", network_type='drive')
        ox.save_graphml(graph, path)
        return graph
    
def addCrashesToEdges(df, graph):
    try:
        df['nearest_edge'] = list(ox.distance.nearest_edges(graph, df['lon'].to_numpy(), df['lat'].to_numpy()))
    except Exception as e:
        raise ValueError(f"Failed to add crash to edges. Error is {e}")
    return df

def countCrashesPerEdge(df):
    edgeCounts = df.groupby("nearest_edge").size().reset_index(name="crash_count").sort_values(by="crash_count", ascending=False)
    return edgeCounts