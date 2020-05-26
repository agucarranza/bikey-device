import serial
import logging

SERIAL_PORT = "/dev/serial0"
running = True


def get_position_data(my_gps):
    data = my_gps.readline()
    message = data[0:6]
    if message == "$GPRMC":
        # GPRMC = Recommended minimum specific GPS/Transit data
        # Reading the GPS fix data is an alternative approach that also works
        parts = data.split(",")
        if parts[2] == 'V':
            # V = Warning, most likely, there are no satellites in view...
            print "GPS receiver warning"
            logger.info("error")
        else:
            dd = int(float(parts[3]) / 100)
            mm = float(parts[3]) - dd * 100
            latitude = dd + mm / 60
            if parts[4] == 'S':
                latitude = latitude * -1
            dd = int(float(parts[5]) / 100)  # degrees
            mm = float(parts[5]) - dd * 100  # minutes
            longitude = dd + mm / 60
            if parts[6] == 'W':
                longitude = longitude * -1
            speed = float(parts[7]) * 1.852  # km/h
            print "Your position: " + str(latitude) + ", " + str(longitude) + ", v = " + str(speed)
            logger.info(str(latitude) + ", " + str(longitude) + ", " + str(speed))
    else:
        pass


print "Application started!"
gps = serial.Serial(SERIAL_PORT, baudrate=9600, timeout=0.5)

# Log
logger = logging.getLogger('example_log')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('/home/pi/debug.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

while running:
    try:
        get_position_data(gps)
    except KeyboardInterrupt:
        running = False
        gps.close()
        print "Application closed!"
