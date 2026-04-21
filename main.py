import roadMapping
import cachingLogic
import os

def main():
    graph = roadMapping.loadGraph()
    
    if os.path.exists("cache/mappedCrashes.pkl"):
        df = cachingLogic.loadMappedCrashes("cache/mappedCrashes.pkl")
    else:
        df = roadMapping.loadData()
        df = roadMapping.addCrashesToEdges(df, graph)
        cachingLogic.saveMappedCrashes(df, "cache/mappedCrashes.pkl")

    #Can delete this later, used to test if the pipeline is working.
    print(roadMapping.countCrashesPerEdge(df))

    print("Finished")


if __name__ == "__main__":
    main()