import unittest
import json
from graphs import *
from trams import TramNetwork

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


    # Testing connectedness with depth first search
    def test_connectedness(self):
        visited = set()

        def dfs(node):
            if node not in visited:
                visited.add(node)
                for neighbour in self.G.neighbors(node):
                    dfs(neighbour)
        
        start_node = next(iter(self.G.vertices()))
        dfs(start_node)
        print(visited)

        self.assertEqual(len(visited), len(self.G.vertices()), "Graph is not connected")



    # Testing the method transitiontime. 
    # Last test tests the transitiontime between stops thats not in the dict = None
    def test_time(self):
        
        tram_network = TramNetwork({}, {}, {
            "östra sjukhuset": {"tingvallsvägen": 1},
            "tingvallsvägen": {"kaggeledstorget": 2},
            "kaggeledstorget": {"ättehögsgatan": 3},
        })

        self.assertEqual(tram_network.transition_time("östra sjukhuset", "tingvallsvägen"), 1)
        self.assertEqual(tram_network.transition_time("tingvallsvägen", "kaggeledstorget"), 2)
        self.assertEqual(tram_network.transition_time("kaggeledstorget", "ättehögsgatan"), 3)

        self.assertIsNone(tram_network.transition_time("chalmers", "korsvägen"))


# Tried to generate a linedict and stopdict. It doesnt work properly and 
# I was running out of time so I left it as this...
class TestGraphsHypothesis(unittest.TestCase):


    line_name = st.text(min_size=1),
    stop_names = st.text(min_size=1)
    stops = st.lists(stop_names, min_size=2, unique=True)
    coordinates = st.tuples(
    st.floats(min_value=57.0, max_value=58.0), 
    st.floats(min_value=11.0, max_value=12.0))
    
    generate_linedict = st.dictionaries(keys=line_name, values=stops, min_size=2)
    generate_stopdict = st.dictionaries(keys=stop_names, values=coordinates, min_size=2)

# Testing so the nodes in stopdict and linedict are the same. 
    @given(stopdict=generate_stopdict)
    def test_extreme_positions(self,stopdict):

        network = TramNetwork(stopdict, {}, {})
        (min_lat, max_lat, min_lon, max_lon) = network.extreme_positions()

        latitudes = [coord[0] for coord in stopdict.values()]
        longitudes = [coord[1] for coord in stopdict.values()]

        assert min_lat == min(latitudes)
        assert max_lat == max(latitudes)
        assert min_lon == min(longitudes)
        assert max_lon == max(longitudes)






if __name__ == '__main__':
    unittest.main()

    