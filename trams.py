import json
from graphs import *
import tramdata as td

def readTramNetwork(tramfile='tramnetwork.json'):
    with open(tramfile, 'r', encoding='utf-8') as file:
        data = json.load(file)

    stopdict = data['stops']
    linedict = data['lines']
    timedict = data['times']

    tram_network = TramNetwork(stopdict, linedict, timedict,start=None)
    
    return tram_network

class TramNetwork(WeightedGraph):
    def __init__(self, stopdict, linedict, timedict, start=None):
        super().__init__(start=start)
        self.stopdict = stopdict
        self.linedict = linedict
        self.timedict = timedict

        # Create nodes from stopdict
        for stop in stopdict.keys():
            self.add_vertex(stop)

        # Adding edges and weights to the edges
        for a, bx in self.timedict.items():
            for b, time in bx.items():
                self.add_edge(a, b)
                self.set_weight(a, b, time)


    def get_linedict(self):
        return self.linedict
    
    def get_stopdict(self):
        return self.stopdict
    
    def all_lines(self):
        return self.linedict

    def all_stops(self):
        return self.stopdict

    def extreme_positions(self):            
        latitud = []
        longitud = []
        for stop,data in self.stopdict.items():
            lat = float(data['lat'])
            lon = float(data['lon'])
            latitud.append(lat)
            longitud.append(lon)

        min_lat = min(latitud)
        max_lat = max(latitud)
        min_lon = min(longitud)
        max_lon = max(longitud)
        
        return (min_lat, max_lat, min_lon, max_lon)

    def geo_distance(self,stop1,stop2):
        return td.distance_between_stops(self.stopdict, stop1, stop2)

    def line_stops(self, line):
        return self.linedict.get(line)

    def stop_lines(self, stop):
        return td.lines_via_stop(stop)

    def stop_position(self, stop):
        return self.stopdict[stop]['lat'], self.stopdict[stop]['lon']

    def transition_time(self, stop1, stop2):
        return self.get_weight(stop1,stop2)
        

class TramLine:
    
    def __init__(self, num, stop, line):
        self.line = line
        self.number = num
        self.stop = stop

    def get_number(self):
        return self.line.get_linedict()

    def get_stops(self):
        for line, stoplist in self.linedict.items():
            return stoplist




class TramStop():

    def __init__(self, name, position=None, lines=None):
        self.name = name
        self.position = position
        self.lines = lines

    def add_line(self,line):
        if line not in self.lines:
            self.lines.append(line)

    def get_lines(self):
        return self.lines

    def get_name(self):
        return self.name

    def get_position(self):
        return self.position
    
    def set_position(self, lat, lon):
        self.position = {'lat': lat, 'lon': lon}

def demo():
    G = readTramNetwork()
    a, b = input('from,to ').split(',')
    view_shortest(G, a, b)

if __name__ == '__main__':
    demo()