import random
from collections import defaultdict
import heapq

class Router:
    def __init__(self, id):
        self.id = id
        self.congestion = 1.0
        self.connections = {}

class NetworkCore:
    def __init__(self, num_routers):
        self.routers = {}
        self.setup_network(num_routers)
        
    def setup_network(self, num_routers):
        for i in range(num_routers):
            self.routers[i] = Router(i)
            
        connections = [
            (0, 1, 1.0), (0, 2, 2.0),
            (1, 2, 1.0), (1, 3, 3.0),
            (2, 3, 2.0), (2, 4, 2.0),
            (3, 4, 1.0), (3, 5, 2.0),
            (4, 5, 1.0)
        ]
        
        for src, dst, weight in connections:
            self.add_connection(src, dst, weight)
    
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
    
    def get_network_state(self):
        state = {
            'routers': {},
            'connections': []
        }
        
        for router_id, router in self.routers.items():
            state['routers'][router_id] = {
                'congestion': router.congestion
            }
        
        for src_id, router in self.routers.items():
            for dst_id, base_weight in router.connections.items():
                if (dst_id, src_id) not in state['connections']:
                    effective_weight = self.get_effective_weight(src_id, dst_id)
                    state['connections'].append((src_id, dst_id, base_weight, effective_weight))
        
        return state

def run_simulation_step(network, start, end):
    network.update_network_conditions()
    path = network.find_shortest_path(start, end)
    state = network.get_network_state()
    return path, state

if __name__ == "__main__":
    network = NetworkCore(6)
    print("Running 3 simulation steps:")
    for step in range(3):
        path, state = run_simulation_step(network, 0, 5)
        print(f"\nStep {step + 1}:")
        print(f"Path found: {path}")
        print("Router congestion levels:")
        for router_id, data in state['routers'].items():
            print(f"Router {router_id}: {data['congestion']:.2f}")