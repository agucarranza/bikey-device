import serial
import logging
import bluetooth
import time
import os
from subprocess import Popen, PIPE

SERIAL_PORT = "/dev/serial0"
gps = serial.Serial(SERIAL_PORT, baudrate=9600, timeout=0.5)
running = True
start_time = time.time() # poner cuando se inicializa el driver

# Log
logger = logging.getLogger('example_log')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('/home/pi/debug.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


def get_position_data(my_gps):
    data = my_gps.readline()
    message = data[0:6]
    while not message == "$GPRMC":
        data = my_gps.readline()
        message = data[0:6]
        continue

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

        cadena = tiempo + "," + str(latitude) + "," + str(longitude) + "," + str(speed) + '$'
        return cadena


def bt_server():
    os.system('echo "discoverable on\\npairable on\\n" | bluetoothctl')
    print('Bluetooth Visible')

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


def send_driver(value):
    command = 'echo ' + str(value) + ' > /dev/Bikey'
    print(command)
    os.system(command)
    time.sleep(2)


def init_driver():
    Popen(["insmod", "/home/pi/proyectos/drv4/drv4.ko"], stdout=PIPE)
    print('driver installed!')
    time.sleep(3)
    os.chmod('/dev/Bikey', 0o777)
    print('permits changed')


print "Application started!"
init_driver()
socket = bt_server()


while running:
    try:
        received = socket.recv(1)
        print('Recibido: ' + str(received))
        if received == 'd': # Habilitar
            pass
        elif received == 'g': # Enviar string de info.
            print('Obteniendo datos GPS')
            info = get_position_data(gps)
            if info is None:
               pass
            else:
                socket.send(info)
        elif received == 'u': # Desbloquear.
            print('Cerrojo Desbloqueado')
            send_driver(0)
        elif received == 'b': # Bloquear.
             print('Cerrojo Bloqueado')
             send_driver(1)
             start_time = time.time()
             socket.close()
             socket = bt_server()
        else:
            print("ERROR en la orden. Recibido: " + str(received))
            break
    except KeyboardInterrupt:
        Popen(["rmmod", "drv4"], stdout=PIPE, stderr=PIPE)
        print "Application close!"
        running = False



    # finally:
    #     running = False
    #     gps.close()
    #     socket.close()
    #     Popen(["rmmod", "drv4"], stdout=PIPE, stderr=PIPE)
    #     print "Application close!"
