import networkx as nx
import graphviz as gv

class Graph(nx.Graph):

    def __init__(self, start=None):
        super().__init__(start)
#        if not start:
#            self.add_edges_from(start)

    def neighbors(self, vertex):
        return list(super().neighbors(vertex))

    def vertices(self):
        return list(self.nodes())

    def edges(self):
        return list(super().edges())

    def __len__(self): 
        return len(self.vertices())

    def add_vertex(self, vertex):
        super().add_node(vertex)

    def add_edge(self, vertex1, vertex2):
        super().add_edge(vertex1, vertex2)

    def remove_vertex(self, vertex): 
        if vertex in self.vertices():
            self.remove_node(vertex)

    def remove_edge(self, vertex1, vertex2):
        if vertex1 in self.vertices() and vertex2 in self.vertices():
            super().remove_edge(vertex1, vertex2)

    def get_vertex_value(self, vertex):
        return self.nodes[vertex]

    # Denna fungerar inte som den ska
    def set_vertex_value(self, vertex, value):
        self.nodes[vertex].update(value)
        #nodes[vertex] = value
        



class WeightedGraph(Graph):

    def __init__(self,start):
        super().__init__(start)
        #self.weight = {}

    def get_weight(self, vertex1 ,vertex2):
        if self.has_edge(vertex1, vertex2):
            return self[vertex1][vertex2].get('weight')   


    def set_weight(self, vertex1, vertex2, weight):
        if self.has_edge(vertex1, vertex2):
            self[vertex1][vertex2]['weight'] = weight



def costs2attributes(G, cost, attr='weight'):
    for a, b in G.edges():
        Weight = G.get_weight(a,b)
        if Weight != None:
            G[a][b][attr] = Weight
        else:
            G[a][b][attr] = cost(a,b)
        

    
def dijkstra(graph, source, cost=lambda u, v: 1):
    costs2attributes(graph, cost)
    paths = nx.shortest_path(graph, source, weight= 'weight', method='dijkstra')
    return paths

def view_shortest(G, source, target, cost=lambda u,v: 1):
    path = dijkstra(G, source, cost)[target]
    print(path)
    colormap = {str(v): 'orange' for v in path}
    print(colormap)
    visualize(G, nodecolors=colormap)

def visualize(graph, nodecolors=None):
    dot = gv.Digraph(format='pdf')
    for node in graph.nodes():
        if nodecolors and str(node) in nodecolors:
            dot.node(str(node), color=nodecolors[str(node)], style='filled')
        else:
            dot.node(str(node))
    
    for edge in graph.edges():
        dot.edge(str(edge[0]), str(edge[1]))

    dot.render('graph_output', view=True,)

def demo():
    G = Graph([(1,2),(1,3),(1,4),(3,4),(3,5),(3,6), (3,7), (6,7), (4,5), (5,6)])
    wegr = WeightedGraph(G)
    wegr.set_weight(1,2,weight=5)
    wegr.set_weight(1,3,weight=10)
    wegr.set_weight(3,6,weight=5)
    wegr.set_weight(1,4,weight=1)
    wegr.set_weight(4,5,weight=100)
    wegr.set_weight(5,6,weight=1)
    wegr.set_weight(3,7,weight=100)
    wegr.set_weight(6,7,weight=1)
    wegr.set_weight(3,5,weight=100)
    wegr.set_weight(1,4,weight=100)
    wegr.get_weight(1,2)
    wegr.get_weight(1,3)
    wegr.get_weight(1,4)
    wegr.get_weight(4,5)
    wegr.get_weight(5,6)
    wegr.get_weight(3,7)

    view_shortest(wegr, 4, 7)

if __name__ == '__main__':
    demo()

#edges = [(1, 2), (2, 3), (3, 1), (3, 4), (4, 3)]

#g = Graph(edges)
#wg = WeightedGraph(edges)

#wg.add_vertex(5)
#wg.add_edge(5,1)
#wg.set_weight(1,5,1)
#wg.set_weight(1,2,5)
#wg.set_weight(2,3,5)
#wg.set_weight(3,4,3)
#wg.set_weight(1,3,2)

#g.add_node(5)
#g.add_edge(1,5)
#print(g.edges())
#g.remove_vertex(1)
#print(g.edges())
#g.remove_edge(2,3)
#print(g.edges())
#print(g.vertices())

#print(g.get_vertex_value)
#gv.visualize(g, view='dot', name='mygraph', nodecolors=None)

#print(wg.get_weight(1,2))
#vikt = wg[1][2]['weight']
#print(vikt)
#wg.set_vertex_value(1, {"color": "blue"})
#verval = wg.get_vertex_value(1)
#print(verval)
