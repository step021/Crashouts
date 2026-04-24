import networkx as nx
import osmnx as ox

def calculate_routes(graph, source, target):
    try:
        baseline = nx.shortest_path(graph, source=source, target=target, weight='travel_time')
    except nx.NetworkXNoPath:
        baseline = None
        print("Error: No shortest path found!")

    def heuristic(u, v):
        u_lat = graph.nodes[u].get('y', 0)
        u_lon = graph.nodes[u].get('x', 0)
        v_lat = graph.nodes[v].get('y', 0)
        v_lon = graph.nodes[v].get('x', 0)
        
        distance = ox.distance.great_circle(u_lat, u_lon, v_lat, v_lon)
        estimated_time = distance / 15.0 
        return estimated_time
    
    try:
        safer_route = nx.astar_path(
            graph, 
            source=source, 
            target=target, 
            heuristic=heuristic,
            weight='weight' 
        )
    except nx.NetworkXNoPath:
        safer_route = None
        print("No safer path found.")

    return baseline, safer_route

def path_stats(graph, path):
    """ returns the time, danger score to represent time (minutes) path takes and the danger of that path"""
    if not path:
        return 0, 0  
    total_time = 0
    total_danger = 0
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        edge_data = graph.get_edge_data(u, v)[0] 
        total_time += float(edge_data.get('travel_time', 0))
        total_danger += float(edge_data.get('crash_penalty', 0))
    return round(total_time / 60, 2), round(total_danger, 2)