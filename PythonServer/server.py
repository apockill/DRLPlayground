import socket
import sys
from base64 import b64decode

import cv2
import numpy as np


HOST = 'localhost'  # Symbolic name, meaning all available interfaces
PORT = 1234  # Arbitrary non-privileged port

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

# Bind socket to local host and port
try:
    soc.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

print('Socket bind complete')

# Start listening on socket
soc.listen(10)
print('Socket now listening')
conn, addr = soc.accept()
print('Connected with ' + addr[0] + ':' + str(addr[1]))



while 1:
    # wait to accept a connection - blocking call
    print('top')

    # Receive the byte size of the incoming image
    length = conn.recv(1024)
    length = int(length)
    # print 'length',length


    k = int(length / 1024)
    j = length % 1024

    maindata = b''
    i = 0
    while i < k:
        i = i + 1
        data = conn.recv(1024)
        maindata = maindata + data

    if j != 0:
        data = conn.recv(j)
        maindata = maindata + data

    print("Before base64 decode", len(maindata))

    a = b64decode(maindata)
    nparr = np.fromstring(a, np.uint8)
    print("NUMPY LEN", len(nparr))
    img_np = cv2.imdecode(nparr, cv2.IMREAD_ANYDEPTH)


    cv2.imshow("frame", img_np)
    cv2.waitKey(10000)
    conn.sendall(bytes("face"))

soc.close()