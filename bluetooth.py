# import serial
#
# blue = serial.Serial("/dev/serial1", baudrate=9600, timeout=0.5)
#
# while True:
#     data = blue.readline()
#     print('data: ' + data)

from bluedot import BlueDot
bd = BlueDot()
bd.wait_for_press()
print("Hello World")

# from bluedot.btcomm import BluetoothServer
# from signal import pause
#
# def data_received(data):
#     print(data)
#     s.send(data)
#
# s = BluetoothServer(data_received)
# pause()
