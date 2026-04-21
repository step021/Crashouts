import os
import roadMapping
import cachingLogic
import penalty

WEIGHTED_GRAPH_PATH = "cache/weightedGraph.graphml"
MAPPED_CRASHES_PATH = "cache/mappedCrashes.pkl"

def main():
    if os.path.exists(WEIGHTED_GRAPH_PATH):
        graph = cachingLogic.loadWeightedGraph(WEIGHTED_GRAPH_PATH)
    else:
        graph = roadMapping.loadGraph()
        graph = roadMapping.addTravelTimes(graph)

        if os.path.exists(MAPPED_CRASHES_PATH):
            df = cachingLogic.loadMappedCrashes(MAPPED_CRASHES_PATH)
        else:
            df = roadMapping.loadData()
            df = roadMapping.addCrashesToEdges(df, graph)
            cachingLogic.saveMappedCrashes(df, MAPPED_CRASHES_PATH)

        penalties = penalty.computeEdgePenalties(df, graph)
        graph = penalty.addPenaltiesToGraph(graph, penalties)

        cachingLogic.saveWeightedGraph(graph, WEIGHTED_GRAPH_PATH)

    #This needs to eventually become an API call
    isRaining = True
    graph = penalty.finalWeights(graph, isRaining=isRaining)

    print("Finished")

if __name__ == "__main__":
    main()