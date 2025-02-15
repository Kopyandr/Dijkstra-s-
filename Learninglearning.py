import heapq
import osmnx as ox
import matplotlib as plt
'''G = {
    1 : {2:8, 3:4, 5:2},
    2 : {1:8, 3:5, 4:2, 7:6, 8:7},
    3 : {1:4, 2:5, 6:3, 7:4},
    4 : {2:2, 9:3},
    5 : {1:2, 6:5},
    6 : {3:3, 5:5, 7:5, 8:7, 9:10},
    7 : {2:6, 3:4, 6:5, 8:3},
    8 : {2:7, 6:7, 7:3, 9:1},
    9 : {4:3, 6:10, 8:1}
}'''
'''G = {
    1: {
        2: {"distance": 8, "speedlimit": 50},
        3: {"distance": 4, "speedlimit": 10},
        5: {"distance": 2, "speedlimit": 130}
    },
    2: {
        1: {"distance": 8, "speedlimit": 50},
        3: {"distance": 5, "speedlimit": 90},
        4: {"distance": 2, "speedlimit": 50},
        7: {"distance": 6, "speedlimit": 130},
        8: {"distance": 7, "speedlimit": 90}
    },
    3: {
        1: {"distance": 4, "speedlimit": 90},
        2: {"distance": 5, "speedlimit": 50},
        6: {"distance": 3, "speedlimit": 130},
        7: {"distance": 4, "speedlimit": 90}
    },
    4: {
        2: {"distance": 2, "speedlimit": 50},
        9: {"distance": 3, "speedlimit": 130}
    },
    5: {
        1: {"distance": 2, "speedlimit": 130},
        6: {"distance": 5, "speedlimit": 90}
    },
    6: {
        3: {"distance": 3, "speedlimit": 50},
        5: {"distance": 5, "speedlimit": 130},
        7: {"distance": 5, "speedlimit": 90},
        8: {"distance": 7, "speedlimit": 50},
        9: {"distance": 10, "speedlimit": 90}
    },
    7: {
        2: {"distance": 6, "speedlimit": 130},
        3: {"distance": 4, "speedlimit": 90},
        6: {"distance": 5, "speedlimit": 90},
        8: {"distance": 3, "speedlimit": 90}
    },
    8: {
        2: {"distance": 7, "speedlimit": 90},
        6: {"distance": 7, "speedlimit": 130},
        7: {"distance": 3, "speedlimit": 90},
        9: {"distance": 1, "speedlimit": 130}
    },
    9: {
        4: {"distance": 3, "speedlimit": 130},
        6: {"distance": 10, "speedlimit": 90},
        8: {"distance": 1, "speedlimit": 130}
    }
}'''


G = ox.graph_from_place("Karlovarský kraj, Czechia", network_type="drive")


for u, v, k, data in G.edges(keys=True, data=True):
    try:
        
        data['speed_kph'] = float(data.get('speed_kph', 50))
    except Exception as e:
        data['speed_kph'] = 50  


G_dict = {}
for u, neighbors in G.adjacency():
    G_dict[u] = {}
    for v, edge_dict in neighbors.items():
        
        lengths = [data.get('length', 1) for data in edge_dict.values()]
        speeds = [data.get('speed_kph', 50) for data in edge_dict.values()]
        
        length = int(round(min(lengths))) if lengths else 1
        speed = int(round(min(speeds))) if speeds else 50
        
        G_dict[u][v] = {"length": length, "speed_kph": speed}
        
#for i, (node, nbrs) in enumerate(G_dict.items()):
#    print(f"G Node {node}: {nbrs}")
#    if i >= 8:  
# break

gdf_nodes, _ = ox.graph_to_gdfs(G)
C = {node: [row['x'], row['y']] for node, row in gdf_nodes.iterrows()}
#for i, (node, coord) in enumerate(C.items()):
#    print(f"C Node {node}: {coord}")
#    if i >= 8:
#        break

#method= input("choose method ('travel time' or distance): ").strip().lower()
location='Cheb'  
destination='Kynšperk nad Ohří' 
method='distance'  
lat_loc, lon_loc=ox.geocode(location) 
print(lat_loc,lon_loc) 
lat_des,lon_des=ox.geocode(destination)
start=ox.distance.nearest_nodes(G, X=lon_loc, Y=lat_loc) # set the location to the nearest node 
end=ox.distance.nearest_nodes(G, X=lon_des, Y=lat_des)  # destination set to the nearest node 

def DJ (G,start,end,method='distance'):
    distances = {node: float('inf') for node in G} # Distances set to inf 
    distances[start] = 0 # The start node distance=0 
    predecessors = {node: None for node in G} # set initial perent nodes to None 
    queue = [(0, start)] # Priority queue: chosing the closest node (dist optimazation)

    while queue: 
        current_distance, current_node= heapq.heappop(queue) #returns the distance, and the node while clearing the que  
        # current_distance=0,current_node=start
        if current_node==end: 
            break
        if current_distance > distances[current_node]: # is the current distance (0) > than the distances[current_node]->skip   
            continue  
        
        for neighbor,properties in G[current_node].items(): #returns 1st (neigbor=2, weight=8)

            if method=='travel time': #chosing the weight computation method 
                new_distance=current_distance + (properties['length']/1000)/properties['speed_kph']
            
            else:
                new_distance=current_distance+properties['length'] #plain distance 
                
            if new_distance < distances[neighbor]: 
                distances[neighbor]=new_distance
                predecessors[neighbor]=current_node 
                heapq.heappush(queue,(new_distance,neighbor)) # que now = [(8,2)] 
    return(distances, predecessors) 
 


def reconstruct_path (predecessors, start,end): 
    path=[] 
    current=end 
    while current is not None: 
        path.append(current) 
        if current==start:
            break
        current=predecessors[current] # set the current to the parent of the curent if u get me 
    path.reverse() 
    
    if path[0]!= start: 
        print('incorect path')
        return[]
    
    return path

distances, predecessors = DJ(G_dict, start, end, method)
route=reconstruct_path(predecessors,start,end)

if method=='travel time':
    print ("Shortest distance from start node:", start, "to end node", end, ":", round(distances[end]*60,2), 'minits')
else:
    print("Shortest distance from start node:", start, "to end node", end, ":", (distances[end]/1000),'km')
#print(predecessors)
#print("Route:", route)


fig, ax = ox.plot_graph_route(G, route, route_linewidth=4, node_size=0, route_color='r')

         

    
            
    