import unittest
from tramdata import *
from haversine import haversine, Unit

TRAM_FILE = './tramnetwork.json'
TXT_FILE = './tramlines.txt'

class TestTramData(unittest.TestCase):

    def setUp(self):
        with open(TRAM_FILE, encoding='utf-8') as trams:
            tramdict = json.loads(trams.read())
            
            self.stopdict = tramdict['stops']
            self.linedict = tramdict['lines']
            self.timedict = tramdict['times']

            self.full_tramdict = {
            "stops": self.stopdict,
            "lines": self.linedict,
            "times": self.timedict
            }

        with open(TXT_FILE, 'r', encoding='utf-8') as file:
            self.lines_txtfile = file.readlines()

    def test_stops_exist(self):
        stopset = {stop for line in self.linedict for stop in self.linedict[line]}
        for stop in stopset:
            self.assertIn(stop, self.stopdict, msg = stop + ' not in stopdict')

    def test_lines(self):

        lines = [
            line.strip().rstrip(':')
            for line in self.lines_txtfile
            if line.isdigit and line.endswith(':')
        ]

        for line in lines:
            self.assertIn(line, self.linedict, msg= f'Line {line} is missing in linedict')

    def test_linestop(self):

        lines = []
        for line in self.lines_txtfile:
            parts = line.strip().rsplit(maxsplit=1)
            if len(parts) > 0:
                lines.append(parts[0])
        
#        print("TXTFIL:", lines)              #test, ta bort
#        print("LINEDICT", self.linedict)


        for line,stops in self.linedict.items():
            for stop in stops:
                self.assertIn(stop, lines, msg= f'Stop {stop} is missing in linedict')

    # This test going through the stopdictionary
    # Getting the lat and long and tests if there is more than 1km between two stops

    def test_distance(self):
        stops = list(self.stopdict.items())
        for i in range(len(stops) - 1):  
            stop1, coord1 = stops[i]
            stop2, coord2 = stops[i + 1]

        # Extrahera latitud och longitud för båda hållplatserna
            lat1, lon1 = float(coord1["lat"]), float(coord1["lon"])
            lat2, lon2 = float(coord2["lat"]), float(coord2["lon"])

        
            distance = haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)

            self.assertLessEqual(distance,20, 
            msg=f"Stop {stop1} and {stop2} are farther than 20km apart: {distance:.2f} km"
        )


    def test_time(self):
        for stop1, times in self.timedict.items():
            for stop2, time_1to2 in times.items():
                if stop2 in self.timedict and stop1 in self.timedict[stop2]:
                    time_2to1 = self.timedict[stop2][stop1]

                    self.assertEqual(time_1to2, time_2to1, msg= f'Time from {stop1} to {stop2} is {time_1to2},'
                                     f'but time from {stop2} to {stop1} is {time_2to1}')

    # Test 'via' function
    def test_answer_query_via(self):
        query = 'via Mariaplan'
        result = answer_query(self.full_tramdict, query)
        expected = ['3', '11', '13']
        self.assertEqual(result, expected, msg= f'Expected result is {expected}, but the result is {result}')
    
    # Test lines between two stops
    def test_answer_query_between(self):
        query = "between chalmers and centralstationen"
        result = answer_query(self.full_tramdict, query)
        expected = ['7', '10', '13']
        self.assertEqual(result, expected, msg= f'Expected result is {expected}, but the result is {result}')
    
    # Test time between two stops from a->b and b->a
    def test_answer_query_time(self):
        query = 'time with 6 from aprilgatan to varmfrontsgatan'
        result = answer_query(self.full_tramdict, query)
        expected = 63
        self.assertEqual(result, expected, msg= f'Expected result is {expected}, but the result is {result}')
    
    # Test distance between two stops
    def test_answer_query_distance(self):
        query = 'distance from Saltholmen to centralstationen'
        result = answer_query(self.full_tramdict, query)
        expected = 9.237564482005418
        self.assertEqual(result, expected, msg= f'Expected result is {expected}, but the result is {result}')

    # Test if one of the stops is not in the dict
    def test_answer_query_errormsg(self):
        query = 'between Chalmers and Landvetter'
        result = answer_query(self.full_tramdict, query)
        self.assertFalse(result, msg= f'Expected result is False, but the result is {result}')


if __name__ == '__main__':
    unittest.main()