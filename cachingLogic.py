import os
import pandas as pd
import roadMapping

def saveMappedCrashes(df, path="cache/mappedCrashes.pkl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_pickle(path)

def loadMappedCrashes(path="cache/mappedCrashes.pkl"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Cannot find {path}")
    return pd.read_pickle(path)

def getMappedCrashes(df, graph, path="cache/mappedCrashes.pkl"):
    if os.path.exists(path):
        return loadMappedCrashes(path)
    df = roadMapping.addCrashesToEdges(df, graph)
    saveMappedCrashes(df, path)
    return df