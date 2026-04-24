import os
import roadMapping
import cachingLogic
import penalty
import routing

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

    nodes = list(graph.nodes())
    start_node = nodes[0]  
    end_node = nodes[-1]
    print(f"Calculating routes from Node {start_node} to Node {end_node}")
    baseline, safer = routing.calculate_routes(graph, start_node, end_node)
    baseline_time_mins, baseline_danger = routing.path_stats(graph, baseline)
    safer_time_mins, safer_danger = routing.path_stats(graph, safer)
    print(f"Baseline Route: {baseline_time_mins} minutes | Danger Score: {baseline_danger}")
    print(f"Safer Route: {safer_time_mins} minutes | Danger Score: {safer_danger}")

    if baseline and safer:
        print(f"SUCCESS: Baseline route generated with {len(baseline)} nodes.")
        print(f"SUCCESS: Safer route generated with {len(safer)} nodes.")
        if baseline != safer:
            print("Safer path is different than the baseline")
        else:
            print("Routes are identical")

    print("Finished")

if __name__ == "__main__":
    main()