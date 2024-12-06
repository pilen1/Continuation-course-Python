import unittest
import json
from graphs import *

from hypothesis import given
import hypothesis.strategies as st

TRAM_FILE = './tramnetwork.json'

class TestGraphs(unittest.TestCase):

    def setUp(self):
        with open(TRAM_FILE) as trams:
            tramdict = json.loads(trams.read())
            self.timedict = tramdict['times']
        self.G = WeightedGraph([])
        for a, bx in self.timedict.items():
            for b, time in bx.items():
                self.G.add_edge(a, b)
                self.G.set_weight(a, b, time)
        
    
    # If a,b in .edges, both are in .vertices
    def test_edges_in_vertices(self):
        for a, b in self.G.edges():
            self.assertIn(a, self.G.vertices(), msg=f'{a} is in edges but not in vertices')
            self.assertIn(b, self.G.vertices(), msg=f'{b} is in edges but not in vertices')

    # Neighbourtest
    def test_neighbour(self):
        for a,b in self.G.edges():
            self.assertIn(a,self.G.neighbors(b))
            self.assertIn(b,self.G.neighbors(a))
    
    # Test dijkstra. Shortest path a->b = shortest path b->a. As there can be different shortest path 
    # where the weight for different paths are the same I had to add the last if to exclude this cases
    def test_dijkstra(self):
        for a in self.G.vertices():
            for b in self.G.vertices():
                if a != b:
                    shortest_ab = dijkstra(self.G, a)[b]
                    shortest_ba = dijkstra(self.G, b)[a]

                    weight_ab = sum(self.G.get_weight(shortest_ab[i], shortest_ab[i+1]) 
                                    for i in range(len(shortest_ab) - 1))
                    weight_ba = sum(self.G.get_weight(shortest_ba[i], shortest_ba[i+1]) 
                                    for i in range(len(shortest_ba) - 1))

                    if shortest_ab[::-1] != shortest_ba and weight_ab == weight_ba:
                        continue

                    self.assertEqual(shortest_ab[::-1], shortest_ba,
                                    msg=f'Shortest path is not matching: {shortest_ab} vs {shortest_ba}')

class TestGraphsHypothesis(unittest.TestCase):

    smallints = st.integers(min_value=0, max_value=10)
    twoints = st.tuples(smallints, smallints)
    st_edge_set = st.sets(twoints, min_size=1)

    # Test of the remove vertex method. Removal of the vertex also removes the edges connected to it
    @given(st_edge_set)     
    def test_removevertex(self,eds):
        G = Graph()
        for a,b in eds:
            G.add_edge(a,b)
        
        if G.vertices():
            remove_node = next(iter(G.vertices()))
            G.remove_node(remove_node)

            assert remove_node not in G.vertices(), f'{remove_node} still in graph'

            for edge in G.edges():
                assert remove_node not in edge, f'{edge} still connected to {remove_node}'

    @given(st_edge_set)
    def test_remove_edge(self,eds):
        G = Graph()
        for a,b in eds:
            G.add_edge(a,b)
            
        if G.edges():
            edge_to_remove = next(iter(G.edges()))
            node1, node2 = edge_to_remove
            G.remove_edge(node1,node2)

            assert (node1, node2) not in G.edges()  

            assert node1 in G.vertices()
            assert node2 in G.vertices()



if __name__ == '__main__':
    unittest.main()