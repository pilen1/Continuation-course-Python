import json
from haversine import haversine, Unit
import sys

def build_tram_data(jsonobject):
    
    with open(jsonobject, 'r', encoding='utf-8') as file:      #read the json file
        data = json.load(file)


    stops = {}

    for stop_name_list, stop_data in data.items():          
        latitud = stop_data['position'][0]         #taking the first and second element in 'position' to get latitude and longitude
        longitud = stop_data['position'][1]

        stops[stop_name_list] = {
            'lat' : latitud,                    #add in the dicitonary
            'lon' : longitud
        }
    
    #print(json.dumps(stops, ensure_ascii=False, indent=1))      # Test ta bort

    return stops


def build_tram_lines(lines):
    with open(lines, 'r', encoding='utf-8') as file:
        data = file.readlines()

    stopdict = {}
    timedict = {}
    current_line = None
    previous_stop = None
    previous_time = None

    for lines in data:
        line = lines.strip()

        if line[:-1].isdigit() and line.endswith(':'):
            current_line = line.rstrip(':')  # Check if the line is a line nr and if so, save it under current line
            stopdict[current_line] = []
            previous_time = None
            previous_stop = None
            continue

        if line:  # Se så att det finns text på raden
            parts = line.rsplit(maxsplit=1)  # Dela raden i ['hållplats', 'tid']
            stop_name = parts[0]
            stopdict[current_line].append(stop_name)  # Lägg in hållplatsen i listan kopplad till linjenummret
            stop_time = parts[1]

        if previous_stop and previous_stop != stop_name:  
            min_now = int(stop_time[-2:])
            min_previous = int(previous_time[-2:])
            stop1, stop2 = sorted([previous_stop, stop_name])
            travel_time = abs(min_now - min_previous)

            if stop1 not in timedict:
                timedict[stop1] = {}  # Skapa en ny inre dictionary
                # Kontrollera om stop2 redan finns
            if stop2 not in timedict[stop1]:
                timedict[stop1][stop2] = travel_time


        previous_stop = stop_name
        previous_time = stop_time

        
    return stopdict, timedict



def build_tram_network(linefile, stopfile):

    tramdata = build_tram_data(stopfile)
    stopdict, timedict = build_tram_lines(linefile)

    totaldict = {
        'stops' : tramdata,
        'lines' : stopdict,
        'times' : timedict, 
    }

    with open('tramnetwork.json', 'w', encoding='utf-8') as file:
        json.dump(totaldict,file, indent=4, ensure_ascii=False)
    #print(json.dumps(totaldict, indent=4, ensure_ascii=False))     #Ta bort

    return totaldict

# Något som skulle kunna tas med här är att kolla allt med små bokstäver. Blir fel om det i linedict står "Centralstationen"
# och i stop "centralstationen"
def lines_via_stop(linedict,stop):
    result = []
    for line, stoplist in linedict.items():     
        if stop in stoplist:
            result.append(line)
    
#    print(result)
    return sorted(result, key=int)      

def lines_between_stops(linedict, stop1, stop2):
    result = []
    for line,stoplist in linedict.items():
        if stop1 in stoplist and stop2 in stoplist:
            result.append(line)

    return sorted(result,key=int)



def time_between_stops(linedict, timedict, line, stop1, stop2):
    list = []
    total_time = 0
    for linenr,stoplist in linedict.items():
        if line == linenr:
            if stop1 in stoplist and stop2 in stoplist:
                start = stoplist.index(stop1)
                end = stoplist.index(stop2)

                if end < start:
                    start, end = end, start

                for i in range(start, end + 1):
                    list.append(stoplist[i])



                for i in range(0, end - start): ## Detta index (i) måste gå från 0 till längden av listan
                    next = i +1
                    stat1, stat2 = sorted([list[i],list[next]]) 
                   
                    for stop,dict in timedict.items():
                        if stat1 == stop:
                            if stat2 in dict.keys():
                                time = dict.get(stat2)
                                total_time += time
                                break

                return total_time
    return False
            

def distance_between_stops(stopdict, stop1, stop2):

    if stop1 not in stopdict or stop2 not in stopdict:
        return False

    lat1, long1 = float(stopdict[stop1]['lat']), float(stopdict[stop1]['lon'])
    lat2, long2 = float(stopdict[stop2]['lat']), float(stopdict[stop2]['lon'])

    distance = haversine((lat1, long1), (lat2, long2), unit=Unit.KILOMETERS)

    return distance


def answer_query(tramdict, query):

    stopdict = tramdict['stops']
    linedict = tramdict['lines']
    timedict = tramdict['times']

    if query.startswith('via'):
        stop = query[4:].strip().title()                       #.title so the stop matches the stop in dict.
          # if stop in linedict:
        try:
            result = lines_via_stop(linedict, stop)
            return result
        except Exception:
            return False


    elif query.startswith('between'):
        stops = query[8:].strip().title().split(' And ', maxsplit=1)
        stop1 = stops[0]
        stop2 = stops[1]
                #if stop1 in linedict and stop2 in linedict:
        try:
            result = lines_between_stops(linedict, stop1, stop2)
            if result:
                return result
            else:
                return False
        except Exception:
            return False

    elif query.startswith('time with'):
        split_userinput = query.title().split()
        line = split_userinput[2]

        if split_userinput[5] == 'To':
            stops = [split_userinput[4], ' '.join(split_userinput[6:])]
        
        else:
            stops = [' '.join(split_userinput[4:6]), ' '.join(split_userinput[7:])]

        try:
            result = time_between_stops(linedict, timedict, line, stops[0], stops[1])
            return result
        except Exception:
            return False
        

    elif query.startswith('distance from'):
        stops = query[13:].strip().title().split(' To ', maxsplit=1)
        if len(stops) == 2:
            stop1, stop2 = stops
            if stop1 in stopdict and stop2 in stopdict:
                try:
                    result = distance_between_stops(stopdict, stop1, stop2)
                    return result
                except Exception:
                    return False
        else:
            return False
    
    else:
        return False

def dialogue(tramfile):

    with open(tramfile, 'r', encoding='utf-8') as file:      
        data = json.load(file)

    while True:
        query = input().strip().lower()
        
        if query == 'quit':
            print('bye')
            break
        
        else:
            result = answer_query(data, query)
            if result == False:
                print('unknown arguments')
            else:
                print(result)
            
        

if __name__ == '__main__':
    
    if sys.argv[1:] == ['init']:
        build_tram_network('tramlines.txt', 'tramstops.json')
    else:
        dialogue("tramnetwork.json")

