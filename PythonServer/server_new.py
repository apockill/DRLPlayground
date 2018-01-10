import socket
from base64 import b64decode

import cv2
import numpy as np


class UnityInterface:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = None

        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect(self.host, self.port)

    def receive_image(self):
        # Receive the byte size of the incoming image
        length = self.connection.recv(1024)
        length = int(length)

        # Figure out how many chunks of data the socket will send
        k = int(length / 1024)
        j = length % 1024

        maindata = b''
        i = 0
        while i < k:
            i = i + 1
            data = self.connection.recv(1024)
            maindata = maindata + data

        if j != 0:
            data = self.connection.recv(j)
            maindata = maindata + data

        a = b64decode(maindata)
        np_arr = np.fromstring(a, np.uint8)
        img_np = cv2.imdecode(np_arr, cv2.IMREAD_ANYDEPTH)
        print(img_np.shape)
        return img_np

    def close(self):
        self.soc.close()


    def _connect(self, host, port):
        try:
            self.soc.bind((host, port))
        except socket.error as e:
            print("Failed to bind to socket. Error: ", e)

        # Start listening on socket
        self.soc.listen(10)
        self.connection, addr = self.soc.accept()
        print("Connected with ", addr)


if __name__ == "__main__":
    client = UnityInterface('localhost', 1234)
    while cv2.waitKey(1) != 'q':
        image = client.receive_image()
        cv2.imshow('Press Q to Exit', image)

    client.close()

