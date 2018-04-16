import socket
import ujson
from base64 import b64decode

import cv2
import numpy as np

from easyinference.utils.context_timer import ContextTimer


class UnityInterface:
    def __init__(self, host, port, timeout=2000):
        self.host = host
        self.port = port
        self.connection = None
        self._last_image = None  # For sending an image in case of error

        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.settimeout(timeout)
        self.connect()

    def get_state(self):
        """ Returns a picture of the current game state, and the current score of the game """
        data = self._read_message()
        image = self._decode_image(data["encodedImage"])
        score = data["gameScore"]
        is_over = data["gameOver"]

        # Record the previous image to send in case of image decoding errors
        self._last_image = image

        return is_over, image, score

    def send_state(self, action):
        """ Send an action command to the game """
        self._write_message(
            '{"action":' + str(int(action)) + ',"resetGame":false}')

    def send_reset(self):
        # print("send_reset()")
        self._write_message('{"action":-1, "resetGame":true}')

    def close(self):
        self.soc.close()

    def _read_message(self):
        main_data = ''
        while True:
            data = self.connection.recv(1000000).decode('utf-8')

            if "QUITING!" in data:
                print("Unity closing! Trying to reconnect...")
                self.connection.close()
                self.connect()
                return self._read_message()

            main_data += data
            if "}" in data: break

        # BUG FIX: If there was extra data, strip it out
        # main_data[0] != '{' and main_data[-1] != '}'
        if main_data.count('{') > 1:
            first_open = main_data.index('{')
            last_open = main_data.rindex('{')
            first_close = main_data.index('}')
            last_close = main_data.rindex('}')

            if last_open < last_close:
                fixed_data = main_data[last_open:last_close + 1]
            elif first_open < first_close:
                fixed_data = main_data[first_open:first_close + 1]
        else:
            fixed_data = main_data

        # Get rid of any other data there
        try:
            decoded = ujson.loads(fixed_data)
        except Exception as e:
            print("ERROR while decoding\n", main_data)
            return self._last_image
        return decoded

    def _write_message(self, msg):
        self.connection.sendall(bytearray(msg, 'utf-8'))

    def _decode_image(self, base64_img):
        a = b64decode(base64_img)
        np_arr = np.fromstring(a, np.uint8)
        img_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img_np

    def connect(self):
        print("Connecting to client...")
        try:
            self.soc.bind((self.host, self.port))
        except socket.error as e:
            print("Failed to bind to socket. Error: ", e)

        # Start listening on socket
        self.soc.listen(0)
        self.connection, addr = self.soc.accept()
        print("Connected with ", addr)

    def disconnect(self):
        self.connection.close()

if __name__ == "__main__":
    from time import sleep, time
    from random import choice

    client = UnityInterface('localhost', 1234)

    print("Server Started Successfully")
    last_key = 0

    client.send_reset()
    is_over, image, score = client.get_state()
    while True:
        cv2.imshow("image", image)
        key = cv2.waitKey(1)
        if key == -1: continue

        if key == ord('c'):
            client.send_state(choice([0, 1, 2, 3, 4, 5]))
        elif key == ord('r'):
            client.send_reset()
        elif key == ord(' '):
            client.send_state(-1)
        else:
            client.send_state(int(key) - 48)

        is_over, image, score = client.get_state()
        if is_over:
            client.send_reset()
            client.get_state()
