import json

from math import cos, sin, atan2, sqrt, radians, degrees, asin, modf
import datetime
import time
from confluent_kafka import Producer, KafkaError
from threading import Thread
from multiprocessing import Process
import ccloud_lib

vehicle_details = [
    {
        "reg_num": "KA1234",
        "lat_start": 14.241637,
        "lat_end": 14.24555,
        "lon_start": 74.38445,
        "lon_end": 74.35555,
        "orientation": 45
    }
    # ,
    # {
    #     "reg_num": "KA47A1111",
    #     "lat_start": 14.241637,
    #     "lat_end": 14.25555,
    #     "lon_start": 74.448445,
    #     "lon_end": 74.25555,
    #     "orientation": 90
    # },
    # {
    #     "reg_num": "KA47W2222",
    #     "lat_start": 14.241637,
    #     "lat_end": 14.255555,
    #     "lon_start": 74.448445,
    #     "lon_end": 74.255555,
    #     "orientation": 100
    # }
]


def get_path_length(lat1, lng1, lat2, lng2):
    ''' calculates the distance between two lat, long coordinate pairs '''
    r = 6371000  # radius of earth in m
    lat1rads = radians(lat1)
    lat2rads = radians(lat2)
    deltaLat = radians((lat2 - lat1))
    deltaLng = radians((lng2 - lng1))
    a = sin(deltaLat / 2) * sin(deltaLat / 2) + cos(lat1rads) * cos(lat2rads) * sin(deltaLng / 2) * sin(deltaLng / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = r * c
    return d


def get_destination_lat_lon(lat, lng, orientation, distance):
    ''' returns the lat an long of destination point
    given the start lat, long, aziuth, and distance '''
    R = 6378.1  # Radius of the Earth in km
    brng = radians(orientation)  # Bearing is degrees converted to radians.
    d = distance / 100  # Distance m converted to km

    lat1 = radians(lat)  # Current dd lat point converted to radians
    lon1 = radians(lng)  # Current dd long point converted to radians

    lat2 = asin(sin(lat1) * cos(d / R) + cos(lat1) * sin(d / R) * cos(brng))

    lon2 = lon1 + atan2(sin(brng) * sin(d / R) * cos(lat1),
                        cos(d / R) - sin(lat1) * sin(lat2))

    # convert back to degrees
    lat2 = degrees(lat2)
    lon2 = degrees(lon2)

    return [lat2, lon2]


def produce_data(data):
    topic = "iiot_tracking"
    record_value = json.dumps(data)
    print("Producing record: {}\t{}".format("timeseries data", record_value))
    time.sleep(2)
    producer.produce(topic, key="timeseries data", value=record_value, on_delivery=ack)
    # p.poll() serves delivery reports (on_delivery)
    # from previous produce() calls.
    producer.poll(0)
    producer.flush()
    print("{} messages were produced to topic {}!".format(delivered_records, topic))


def get_coordinates(interval, orientation, lat1, lng1, lat2, lng2, reg_num):
    '''returns every coordinate pair inbetween two coordinate 
    pairs given the desired interval '''
    coordinates = []
    d = get_path_length(lat1, lng1, lat2, lng2)
    remainder, dist = modf((d / interval))
    counter = 1.0
    coordinates.append([lat1, lng1])
    for distance in range(1, int(dist)):
        time.sleep(1)
        c = get_destination_lat_lon(lat1, lng1, orientation, counter)
        counter += 1.0
        real_time_data_json = {"reg_num": reg_num, "Timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                               "lat": c[0], "lon": c[1]}
        print(real_time_data_json)
        produce_data(real_time_data_json)
        coordinates_final.append(real_time_data_json)
    counter += 1
    return coordinates


def generate_data():
    # point interval in meters
    interval = 1

    for vehicle in vehicle_details:
        print("thread finished...exiting")
        coordinates = []
        # direction of line in degrees
        orientation = vehicle["orientation"]
        # start point
        lat1 = vehicle["lat_start"]
        lng1 = vehicle["lon_start"]
        # end point
        lat2 = vehicle["lat_end"]
        lng2 = vehicle["lon_end"]
        get_coordinates(interval, orientation, lat1, lng1, lat2, lng2, vehicle["reg_num"])
        # thread = Thread(target=, args=())
        # thread.start()
        # thread.join()
        # coordinates = get_coordinates(interval, orientation, lat1, lng1, lat2, lng2, vehicle["reg_num"])


if __name__ == '__main__':

    args = ccloud_lib.parse_args()
    config_file = args.config_file
    conf = ccloud_lib.read_ccloud_config(config_file)
    producer_conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
    producer = Producer(producer_conf)

    coordinates_final = []

    delivered_records = 0


    def ack(err, msg):
        global delivered_records
        """
        Message Delivered Successfully @!!!!!!
        """
        if err is not None:
            print("Failed to deliver message: {}".format(err))
        else:
            delivered_records += 1
            print("Produced record to topic {} partition [{}] @ offset {}"
                  .format(msg.topic(), msg.partition(), msg.offset()))


    generate_data()
