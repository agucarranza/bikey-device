import serial
import logging
# from datetime import datetime, timedelta
import bluetooth
import time

SERIAL_PORT = "/dev/serial0"
gps = serial.Serial(SERIAL_PORT, baudrate=9600, timeout=0.5)
running = True
start_time = time.time()


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

            elapsed_time = time.time() - start_time
            tiempo = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

            info = tiempo + "," + str(latitude) + "," + str(longitude) + "," + str(speed) + '$'
            # print(info)
            return info
    else:
        pass


def bt_server():
    logger.debug("init bt")
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]

    uuid = "00001101-0000-1000-8000-00805F9B34FB"

    bluetooth.advertise_service(server_sock, "SampleServer", service_id=uuid,
                                service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE],
                                )
    print("Waiting for connection on RFCOMM channel", port)

    client_sock, client_info = server_sock.accept()
    print("Accepted connection from", client_info)
    return client_sock


print "Application started!"

# Log
logger = logging.getLogger('example_log')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('/home/pi/debug.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

socket = bt_server()

while running:
    try:
        information = get_position_data(gps)

        if not information:
            continue
        information = information.replace('.', ',')
        information = information.replace('$', '.')

        print(information)
        # dato = socket.recv(1024)
        # if not dato:
        #     break
        # print("Received", dato)
        socket.send(information)

    except KeyboardInterrupt:
        running = False
        gps.close()
        print "Application closed!"
    except OSError:
        pass
    except bluetooth.btcommon.BluetoothError:
        socket.close()
        running = False
        gps.close()
        print('ended connection!')
