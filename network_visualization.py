import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from network_core import NetworkCore, run_simulation_step

class NetworkVisualizer:
    def __init__(self, network):
        self.network = network
        self.fig = plt.figure(figsize=(14, 8))
        self.ax = self.fig.add_subplot(111)
        self.pos = None
        self.setup_graph()
        
    def setup_graph(self):
        self.G = nx.Graph()
        
        for router_id in self.network.routers:
            self.G.add_node(router_id)
            
        for src_id, router in self.network.routers.items():
            for dst_id, base_weight in router.connections.items():
                self.G.add_edge(src_id, dst_id, base_weight=base_weight)
        
        self.pos = nx.spring_layout(self.G, seed=42)
    
    def update_visualization(self, frame, start, end):
        self.ax.clear()
        
        path, state = run_simulation_step(self.network, start, end)
        
        path_edges = []
        if path:
            path_edges = list(zip(path[:-1], path[1:]))
        
        nx.draw_networkx_edges(self.G, self.pos, alpha=0.2, ax=self.ax)
        
        if path_edges:
            nx.draw_networkx_edges(self.G, self.pos, edgelist=path_edges,
                                 edge_color='r', width=2, ax=self.ax)
        
        node_colors = [state['routers'][node]['congestion'] for node in self.G.nodes()]
        nodes = nx.draw_networkx_nodes(self.G, self.pos, node_color=node_colors,
                                     node_size=700, ax=self.ax,
                                     cmap=plt.cm.RdYlGn_r,
                                     vmin=0.5, vmax=2.0)
        
        labels = {node: f'Router {node}\nCongestion: {state["routers"][node]["congestion"]:.2f}'
                 for node in self.G.nodes()}
        nx.draw_networkx_labels(self.G, self.pos, labels, ax=self.ax, font_size=8)
        
        edge_labels = {}
        for src, dst, base, effective in state['connections']:
            edge_labels[(src, dst)] = f'Base: {base:.1f}\nEffective: {effective:.2f}'
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels, ax=self.ax, font_size=7)
        
        plt.colorbar(nodes, ax=self.ax, label='Congestion Level')
        
        if path:
            total_weight = 0
            for i in range(len(path)-1):
                src, dst = path[i], path[i+1]
                for s, d, _, eff in state['connections']:
                    if (s == src and d == dst) or (s == dst and d == src):
                        total_weight += eff
                        break
            self.ax.text(0.02, 0.98, 
                        f'Total path weight: {total_weight:.2f}\n' +
                        f'Path: {" → ".join(map(str, path))}',
                        transform=self.ax.transAxes,
                        verticalalignment='top',
                        bbox=dict(facecolor='white', alpha=0.7))
        
        self.ax.set_title('Network Packet Routing Simulation\n' +
                         f'Step {frame}: Routing from Router {start} to Router {end}\n' +
                         'Red path shows optimal route based on congestion levels\n' +
                         'Effective weight = Base weight × Source congestion × Destination congestion')
        
        self.ax.axis('off')
        plt.tight_layout()
        
        return self.ax.get_children()
    
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
        print("\nVisualization Guide:")
        print("1. Router Labels:")
        print("   - Shows router ID and current congestion level")
        print("   - Color indicates congestion (red = high, green = low)")
        print("\n2. Connection Labels:")
        print("   - Base weight: Original connection cost")
        print("   - Effective weight: Actual cost considering congestion")
        print("\n3. Red Path:")
        print("   - Shows current optimal route from start to end")
        print("   - Chosen to minimize total effective weight")
        
        visualizer.create_animation(0, 5, num_steps=10, interval=1000)
        
        print("\nVisualization complete! Check network_simulation.gif")
        
    except Exception as e:
        print(f"Error in visualization: {e}")

if __name__ == "__main__":
    run_visualization()