# ATTENTION INTREPID CS 395 STUDENTS
# Hi, glad you're curious about the AOT API :)
# This code is dedicated to my roommates and parents, 
# since they'll have to pay my rent when this code gets out into the public.

# Just kidding! The code is slightly suboptimal though, in the sense that it 
# makes a separate API request to get measurements (observations) from each node in the list getAOTNodes returns.
# This could/should instead be bundled together so that it happens in 1 request but even teachers get lazy sometimes.
# The code is also not especially well-optimized (it takes about a second to run)

import requests
from pprint import PrettyPrinter
import geojson
import json
from datetime import datetime, timedelta
from .AOTNode import AOTNode, Measurement

# get a list of AOT Nodes and return it as a list
def getAOTNodes(project : str = None, size : int = 200):
    if project != None:
        req_str = 'https://api.arrayofthings.org/api/nodes?size=' + str(size) + "&project=" + project
    else:
        req_str = 'https://api.arrayofthings.org/api/nodes?size=' + str(size)

    response = requests.get(req_str)
    
    nodes = response.json()['data']
    node_list = list()

    for node in nodes:
        vsn = node['vsn']
        location = geojson.loads(json.dumps(node['location']))
        description = node['description']
        address = node['address']

        node_obj = AOTNode(vsn=vsn, location=location, address=address, description=description)

        node_list.append(node_obj)

    return node_list

def updateMeasurements(nodes : list, size : int):
    
    # TODO this could be more efficient in terms of calls to the api. We could instead construct the list of nodes and match them to the right data later
    for node in nodes:
        req_str = 'https://api.arrayofthings.org/api/observations?node[]=' + str(node.vsn) +'&size=' + str(size)
        response = requests.get(req_str)
        
        observations = response.json()['data']
        if len(observations) == 0:
            continue

        for observation in observations:
            
            uom = observation['uom']

            ts = observation['timestamp']
            date, time = ts.split('T')
            year, month, day = date.split('-')
            hour, minute, second = time.split(':')

            timestamp = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

            value = observation['value']

            sensorpath = observation['sensor_path']

            measurement = Measurement(uom, timestamp, sensorpath, value)

            node.updateMeasurement(sensorpath, measurement)

# returns a list of nodes without empty measurements
def stripEmptyNodes(nodes : list):
    ret_list = list()
    for node in nodes:
        if len(node.getMeasurements()) == 0:
            continue
        ret_list.append(node)

    return ret_list

# jank caching variables.
ns = None
ts = None

def getData(project_slug : str = "chicago", verbose : bool = False):
    global ns
    global ts
    if ns == None or ts == None or datetime.now() - ts >= timedelta(minutes=5):
        expired = ns != None
        if expired:
            print("Data is expired, getting new data...")

        ns = getAOTNodes(project=project_slug, size=500)
        ts = datetime.now()

        updateMeasurements(ns, 500)

        ns = stripEmptyNodes(ns)

        if expired:
            print("Data retrieved!")

    if verbose == True:
        print("There are " + str(len(ns)) + " nodes reporting:\n")
        for n in ns:
            measurements = n.getMeasurements()
            for measurement in measurements:
                print(str(measurements[measurement]))
    
    return ns