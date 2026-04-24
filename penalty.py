R_TABLE = {True: 1.55, False: 1}

CT_TABLE = {'Rear End': .572, 'Sideswipe-Same Direction': .303, 'Angle': 1.23, 'Head On': 3.875, 'Sideswipe-Opposite Direction': .612, 'Not A Collision with Motor Vehicle': 10.645, 'O': 1}

CR_TABLE = {'K': 15, 'A': 5, 'B': 1, 'C': 1, 'O': .2}

def computeEdgePenalties(df, graph, l=1, b=1):
    penalties = {}
    edgeDf = df.groupby('nearest_edge')
    for e, crashes in edgeDf:
        u, v, k = e
        crashPenalty = 0
        for _, crash in crashes.iterrows():
            cr = str(crash.get('crashSeverity', 'O'))
            ct = str(crash.get('mannerOfCollision', 'O'))
            crashPenalty += l * b * CT_TABLE[ct] * CR_TABLE[cr]
        penalties[e] = crashPenalty / graph.edges[u, v, k].get("length", 1.0)
    return penalties

def addPenaltiesToGraph(graph, penalties):
    for e, penalty in penalties.items():
        u, v, k = e
        if (u, v, k) in graph.edges:
            graph.edges[u, v, k]['crash_penalty'] = penalty
    return graph
    
def finalWeights(graph, isRaining=False):
    for u, v, k, data in graph.edges(keys=True, data=True):
        travelTime = float(data.get("travel_time", 0))
        penalty = float(data.get("crash_penalty", 0))
        penalty *= R_TABLE[isRaining]
        data['weight'] = travelTime + penalty
    return graph