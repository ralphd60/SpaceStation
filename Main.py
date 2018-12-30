#!/usr/bin/python3


import urllib.request, json, threading, math, time, signal, logging, sys

# import RPi.GPIO as GPIO

# currently setup for python 3, make sure to use "python3" and script
url = "https://api.wheretheiss.at/v1/satellites/25544?units=miles"
home_lat = 43.14
home_long = -74.24
# lables the pins in board as displayed on the board
if sys.platform == 'linux':
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)

logging.basicConfig(filename='SpaceStation.log', filemode='w', format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def sigint_handler(signum, frame):
    GPIO.cleanup()
    logging.info('cleanup the GPIO')
    raise SystemExit()

if sys.platform == 'linux':
    signal.signal(signal.SIGINT, sigint_handler)


def work(home_lat, home_long):
    response = urllib.request.urlopen(url)
    # use just this one in 3.6
    data = json.loads(response.read())
    # this is for version 3.4 python and is not needed in 3.6
    # str_response = response.readall().decode('utf-8')
    # data = json.loads(str_response)
    logging.info(data)
    iss_lat = data['latitude']
    iss_long = data['longitude']
    iss_altitude = data['altitude']
    iss_velocity = data['velocity']
    distance = sph_dist(home_lat, home_long, iss_lat, iss_long)
    if sys.platform == 'linux':
        if distance <500:
            GPIO.output(12, True)
        else:
            GPIO.output(12, False)

    printCoordinates(distance, home_lat, home_long, iss_lat, iss_long, iss_altitude, iss_velocity)
    # the threading is a timer of 30 seconds, placing the lambda "function" enalbes
    # the timer to work properly, but ctrl-c does not seem to stop the program
    # from running.
    threading.Timer(30.0, lambda:work(home_lat,home_long)).start()
    # threading.Timer(30.0, work(home_lat,home_long)).start()


def printCoordinates(distance, home_lat, home_long, iss_lat, iss_long, iss_altitude, iss_velocity):
    logging.info("The International Space Station's current coordinates are: ")
    logging.info("Latitude = " + str(iss_lat) + " Longitude = " + str(iss_long))
    logging.info("The International Space Altitude and Velocity (in mph) are: ")
    logging.info("Altitude = " + str(iss_altitude) + " miles " + "and Velocity = " + str(iss_velocity)+ " mph")
    logging.info("Current distance to the ISS: " + str(distance))


def sph_dist(lat1, long1, lat2, long2):
    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
    phi1 = (90.0 - lat1) * degrees_to_radians
    phi2 = (90.0 - lat2) * degrees_to_radians
    theta1 = long1 * degrees_to_radians
    theta2 = long2 * degrees_to_radians
    cos = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) +
           math.cos(phi1) * math.cos(phi2))
    arc = math.acos(cos)
    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return arc * 3960


# def main():
    #


if __name__ == "__main__":
    work(home_lat, home_long)



