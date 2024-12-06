import json
from haversine import haversine, Unit
import sys

# Create the stopdict from json file, stop and their latitude, longitude
def build_tram_data(jsonobject):
    
    with open(jsonobject, 'r', encoding='utf-8') as file:     
        data = json.load(file)


    stops = {}

    for stop_name_list, stop_data in data.items():
        newstop_name_list = stop_name_list.lower()              #ändrat    
        latitud = stop_data['position'][0]         
        longitud = stop_data['position'][1]

        stops[newstop_name_list] = {
            'lat' : latitud,                    
            'lon' : longitud
        }

    return stops


# Create a timedict and a linedict from a txt file. The times in txt file is only counting minutes
# for example 10:63 is 11:03. Because of this we kan just look at the last two digits of the line to calculate the traveltime
def build_tram_lines(lines):
    with open(lines, 'r', encoding='utf-8') as file:
        data = file.readlines()

    linedict = {}
    timedict = {}
    current_line = None
    previous_stop = None
    previous_time = None

    for lines in data:
        line = lines.strip().lower()

        if line[:-1].isdigit() and line.endswith(':'):
            current_line = line.rstrip(':')             
            linedict[current_line] = []
            previous_time = None
            previous_stop = None
            continue

        if line:                                        # check if there is a line (some lines are empty)
            parts = line.rsplit(maxsplit=1)             # split the line in ['stop', 'time']
            stop_name = parts[0].lower()
            linedict[current_line].append(stop_name)    
            stop_time = parts[1]

        if previous_stop and previous_stop != stop_name:  
            min_now = int(stop_time[-2:])
            min_previous = int(previous_time[-2:])
            stop1, stop2 = sorted([previous_stop, stop_name])
            travel_time = abs(min_now - min_previous)

            if stop1 not in timedict:
                timedict[stop1] = {}                    # Create a new dictionary inside the dictionary
            
            if stop2 not in timedict[stop1]:             
                timedict[stop1][stop2] = travel_time


        previous_stop = stop_name.lower()
        previous_time = stop_time

        
    return linedict, timedict


# here we build the total dictionary json file combined of all of the 3 dicts we created in the functions above
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

    
    return totaldict

# Check which line(s) that are stoping at a specific stop. The result is sorted
def lines_via_stop(linedict,stop):
    result = []
    for line, stoplist in linedict.items():     
        if stop in stoplist:
            result.append(line)
    
    return sorted(result, key=int)      

# Check which line(s) that are going between two specific stops. The result is sorted
def lines_between_stops(linedict, stop1, stop2):
    result = []
    for line,stoplist in linedict.items():
        if stop1 in stoplist and stop2 in stoplist:
            result.append(line)

    return sorted(result,key=int)


# How long time it takes between two stops on a specific line. Basically we are adding all stops between
# stop1 and stop2 in a new list. Then we goes through that new list and search for all the stops in
# the timedict to calculate the traveltime
def time_between_stops(linedict, timedict, line, stop1, stop2):
    list = []
    total_time = 0
    for linenr,stoplist in linedict.items():
        if line == linenr:
            if stop1 in stoplist and stop2 in stoplist:
                start = stoplist.index(stop1)
                end = stoplist.index(stop2)

                if end < start:                         # Here we check if we are going from A->B or B->A
                    start, end = end, start             

                for i in range(start, end + 1):
                    list.append(stoplist[i])

                for i in range(0, end - start): 
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
            
# Checking the distance between stops using Haversine method
def distance_between_stops(stopdict, stop1, stop2):

    if stop1 not in stopdict or stop2 not in stopdict:
        return False

    lat1, long1 = float(stopdict[stop1]['lat']), float(stopdict[stop1]['lon'])
    lat2, long2 = float(stopdict[stop2]['lat']), float(stopdict[stop2]['lon'])

    distance = haversine((lat1, long1), (lat2, long2), unit=Unit.KILOMETERS)

    return distance

# Answer query. Part of the dialogue function where we take user input and pass it to different funtions
# depending on what kind of information the user want. We are mostly using indexing to get line and stop.
# this function also takes into account if for some reason the indexing is changing for example because of
# double words (Östra Sjukhuset)
# returning False if the for example a stop can't be found in the dictionary.
def answer_query(tramdict, query):

    stopdict = tramdict['stops']
    linedict = tramdict['lines']
    timedict = tramdict['times']

    if query.startswith('via'):
        stop = query[4:].strip().lower()                       #.title so the stop matches the stop in dict.
          # if stop in linedict:
        try:
            result = lines_via_stop(linedict, stop)
            return result
        except Exception:
            return False


    elif query.startswith('between'):
        stops = query[8:].strip().lower().split(' and ', maxsplit=1)
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
        split_userinput = query.lower().split()                    
        line = split_userinput[2]                                   

        if split_userinput[5] == 'to':
            stops = [split_userinput[4], ' '.join(split_userinput[6:])]         # Have to check the position, the first stop can be 'Östra Sjukhuset'
        
        else:
            stops = [' '.join(split_userinput[4:6]), ' '.join(split_userinput[7:])]

        try:
            result = time_between_stops(linedict, timedict, line, stops[0], stops[1])
            return result
        except Exception:
            return False        

    elif query.startswith('distance from'):
        stops = query[13:].strip().lower().split(' to ', maxsplit=1)
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

# Dialogue function
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
            
        
# mainfunction
if __name__ == '__main__':
    
    if sys.argv[1:] == ['init']:
        build_tram_network('tramlines.txt', 'tramstops.json')
    else:
        dialogue("tramnetwork.json")

