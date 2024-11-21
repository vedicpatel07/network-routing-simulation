import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from network_core import NetworkCore, run_simulation_step

class NetworkVisualizer:
    def __init__(self, network):
        self.network = network
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(20, 8))
        self.pos = None
        self.setup_graph()
        
    def setup_graph(self):
        self.G = nx.Graph()
        for router_id in self.network.routers:
            self.G.add_node(router_id)
        for src_id, router in self.network.routers.items():
            for dst_id, base_weight in router.connections.items():
                self.G.add_edge(src_id, dst_id, base_weight=base_weight)
        self.pos = {rid: (r.x, r.y) for rid, r in self.network.routers.items()}

    def draw_network(self, ax, path, state, algorithm_name, computation_time):
        path_edges = []
        if path:
            path_edges = list(zip(path[:-1], path[1:]))
        
        nx.draw_networkx_edges(self.G, self.pos, alpha=0.2, ax=ax)
        
        if path_edges:
            nx.draw_networkx_edges(self.G, self.pos, edgelist=path_edges,
                                 edge_color='r', width=2, ax=ax)
        
        node_colors = [state['routers'][node]['congestion'] for node in self.G.nodes()]
        nodes = nx.draw_networkx_nodes(self.G, self.pos, node_color=node_colors,
                                     node_size=700, ax=ax,
                                     cmap=plt.cm.RdYlGn_r,
                                     vmin=0.5, vmax=2.0)
        
        labels = {node: f'Router {node}\nCongestion: {state["routers"][node]["congestion"]:.2f}'
                 for node in self.G.nodes()}
        nx.draw_networkx_labels(self.G, self.pos, labels, ax=ax, font_size=8)
        
        edge_labels = {}
        for src, dst, base, effective in state['connections']:
            edge_labels[(src, dst)] = f'Base: {base:.1f}\nEff: {effective:.2f}'
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels, ax=ax, font_size=7)
        
        if path:
            total_weight = 0
            for i in range(len(path)-1):
                src, dst = path[i], path[i+1]
                for s, d, _, eff in state['connections']:
                    if (s == src and d == dst) or (s == dst and d == src):
                        total_weight += eff
                        break
            
            ax.text(0.02, 0.98, 
                   f'Algorithm: {algorithm_name}\n' +
                   f'Computation time: {computation_time:.3f}ms\n' +
                   f'Total weight: {total_weight:.2f}\n' +
                   f'Path: {" → ".join(map(str, path))}',
                   transform=ax.transAxes,
                   verticalalignment='top',
                   bbox=dict(facecolor='white', alpha=0.7))
        return nodes

    def update_visualization(self, frame, start, end):
        self.ax1.clear()
        self.ax2.clear()
        
        self.network.update_network_conditions()
        state = self.network.get_network_state()
        
        self.network.set_algorithm("dijkstra")
        dijkstra_path, dijkstra_time = self.network.find_path(start, end)
        
        self.network.set_algorithm("astar")
        astar_path, astar_time = self.network.find_path(start, end)
        
        nodes1 = self.draw_network(self.ax1, dijkstra_path, state, "Dijkstra", dijkstra_time)
        nodes2 = self.draw_network(self.ax2, astar_path, state, "A*", astar_time)
        
        self.ax1.set_title("Dijkstra's Algorithm")
        self.ax2.set_title("A* Algorithm")
        
        for ax in [self.ax1, self.ax2]:
            ax.axis('off')
        
        plt.tight_layout()
        return self.ax1.get_children() + self.ax2.get_children()
    
    def create_animation(self, start, end, num_steps=10, interval=1000, save_path='network_simulation.gif'):
        try:
            ani = animation.FuncAnimation(self.fig, self.update_visualization,
                                        frames=num_steps, interval=interval,
                                        fargs=(start, end), blit=True)
            
            plt.tight_layout()
            ani.save(save_path, writer='pillow')
            plt.close()
            
            print(f"Animation saved as {save_path}")
            
        except Exception as e:
            print(f"Error creating animation: {e}")

def run_visualization():
    try:
        network = NetworkCore(6)
        visualizer = NetworkVisualizer(network)
        print("Starting network simulation visualization...")
        visualizer.create_animation(0, 5, num_steps=10, interval=1000)
        print("Visualization complete! Check network_simulation.gif")
        
    except Exception as e:
        print(f"Error in visualization: {e}")

if __name__ == "__main__":
    run_visualization()