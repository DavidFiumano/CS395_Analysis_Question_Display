from datetime import datetime, timedelta # allows me to cache data
import geojson
from pprint import pformat

class Measurement:

    def __init__(self, uom : str, timestamp : datetime, path : str, value):
        self.uom = uom
        self.timestamp = timestamp
        self.value = value
        self.path = path

    def __str__(self):
        ret_str = "Measurement: " + self.path + "\n"
        ret_str += "  Units: " + str(self.uom) +'\n'
        ret_str += "  Timestamp: " + str(self.timestamp) + '\n'
        if self.uom != None:
            ret_str += "  Value: " + str(self.value) + " " + str(self.uom)
        else:
            ret_str += "  Value: " + str(self.value)

        return ret_str

class AOTNode:

    def __init__(self, vsn : str, location : geojson.Point, address : str, description : str):
        self.vsn = vsn
        
        self.latitude = location['geometry']['coordinates'][1]
        self.longitude = location['geometry']['coordinates'][0]

        self.address = address

        self.description = description

        self.measurements = dict()

    def updateMeasurement(self, sensorpath : str, measurement : Measurement):
        if sensorpath not in self.measurements:
            self.measurements[sensorpath] = measurement
        else: # only update the measurement if the argument is actually newer.
            if self.measurements[sensorpath].timestamp < measurement.timestamp:
                self.measurements[sensorpath] = measurement

    def getMeasurements(self):
        return self.measurements

    def getMeasurement(self, sensorpath : str):
        return self.measurements[sensorpath]

    def __str__(self):
        ret_str = 'Node: '
        ret_str += self.vsn + '\n'

        ret_str += '  Location: (' + str(self.latitude) + ',' + str(self.longitude) + ')\n'
        ret_str += '  Address: ' + self.address + '\n'
        ret_str += '  Description: ' + self.description + '\n'
        ret_str += '  With ' + str(len(self.measurements)) + ' sensors reporting over the lifetime of this process.'
        
        return ret_str

    def __eq__(self, other):
        return self.vsn == other.vsn

    def __lt__(self, other):
        return self.vsn < other.vsn
