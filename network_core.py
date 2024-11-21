import random
from collections import defaultdict
import heapq
import math

class Router:
    def __init__(self, id, x=0, y=0):
        self.id = id
        self.congestion = 1.0
        self.connections = {}
        self.x = x
        self.y = y

class NetworkCore:
    def __init__(self, num_routers):
        self.routers = {}
        self.setup_network(num_routers)
        self.algorithm = "dijkstra" 
        
    def setup_network(self, num_routers):
        positions = [(0,0), (1,0), (1,1), (2,1), (2,2), (3,2)]
        for i in range(num_routers):
            x, y = positions[i]
            self.routers[i] = Router(i, x, y)
            
        connections = [
            (0, 1, 1.0), (0, 2, 2.0),
            (1, 2, 1.0), (1, 3, 3.0),
            (2, 3, 2.0), (2, 4, 2.0),
            (3, 4, 1.0), (3, 5, 2.0),
            (4, 5, 1.0)
        ]
        
        for src, dst, weight in connections:
            self.add_connection(src, dst, weight)
    
    def set_algorithm(self, algo):
        self.algorithm = algo

    def add_connection(self, router1_id, router2_id, base_weight):
        if router1_id in self.routers and router2_id in self.routers:
            self.routers[router1_id].connections[router2_id] = base_weight
            self.routers[router2_id].connections[router1_id] = base_weight
    
    def update_network_conditions(self):
        for router in self.routers.values():
            router.congestion = random.uniform(0.5, 2.0)
    
    def get_effective_weight(self, src_id, dst_id):
        if src_id not in self.routers or dst_id not in self.routers:
            return float('inf')
            
        src_router = self.routers[src_id]
        dst_router = self.routers[dst_id]
        
        if dst_id not in src_router.connections:
            return float('inf')
            
        base_weight = src_router.connections[dst_id]
        return base_weight * src_router.congestion * dst_router.congestion

    def heuristic(self, current, goal):
        current_router = self.routers[current]
        goal_router = self.routers[goal]
        return abs(current_router.x - goal_router.x) + abs(current_router.y - goal_router.y)
    
    def find_path_astar(self, start, end):
        if start not in self.routers or end not in self.routers:
            return None
            
        g_score = {router_id: float('inf') for router_id in self.routers}
        g_score[start] = 0
        f_score = {router_id: float('inf') for router_id in self.routers}
        f_score[start] = self.heuristic(start, end)
        
        previous = {router_id: None for router_id in self.routers}
        open_set = [(f_score[start], start)]
        closed_set = set()
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == end:
                break
                
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            for neighbor in self.routers[current].connections:
                if neighbor in closed_set:
                    continue
                    
                weight = self.get_effective_weight(current, neighbor)
                tentative_g = g_score[current] + weight
                
                if tentative_g < g_score[neighbor]:
                    previous[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        if g_score[end] == float('inf'):
            return None
            
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return path

    def find_shortest_path(self, start, end):
        if start not in self.routers or end not in self.routers:
            return None
            
        distances = {router_id: float('inf') for router_id in self.routers}
        distances[start] = 0
        previous = {router_id: None for router_id in self.routers}
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_distance, current = heapq.heappop(pq)
            
            if current in visited:
                continue
                
            if current == end:
                break
                
            visited.add(current)
            
            for neighbor in self.routers[current].connections:
                if neighbor in visited:
                    continue
                    
                weight = self.get_effective_weight(current, neighbor)
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
        
        if distances[end] == float('inf'):
            return None
            
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return path

    def find_path(self, start, end):
        import time
        start_time = time.time()
        if self.algorithm == "astar":
            path = self.find_path_astar(start, end)
        else:
            path = self.find_shortest_path(start, end)
        comp_time = (time.time() - start_time) * 1000  
        return path, comp_time
    
    def get_network_state(self):
        state = {
            'routers': {},
            'connections': [],
            'algorithm': self.algorithm
        }
        
        for router_id, router in self.routers.items():
            state['routers'][router_id] = {
                'congestion': router.congestion,
                'x': router.x,
                'y': router.y
            }
        
        for src_id, router in self.routers.items():
            for dst_id, base_weight in router.connections.items():
                if (dst_id, src_id) not in state['connections']:
                    effective_weight = self.get_effective_weight(src_id, dst_id)
                    state['connections'].append((src_id, dst_id, base_weight, effective_weight))
        
        return state

def run_simulation_step(network, start, end):
    network.update_network_conditions()
    path = network.find_path(start, end)
    state = network.get_network_state()
    return path, state

if __name__ == "__main__":
    network = NetworkCore(6)
    print("Running with Dijkstra's algorithm:")
    path, _ = run_simulation_step(network, 0, 5)
    print(f"Dijkstra path: {path}")
    
    network.set_algorithm("astar")
    path, _ = run_simulation_step(network, 0, 5)
    print(f"A* path: {path}")