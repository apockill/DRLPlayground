import socket
import json
from base64 import b64decode

import cv2
import numpy as np


class UnityInterface:


    def __init__(self, host, port, timeout=2000):
        self.host = host
        self.port = port
        self.connection = None

        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.settimeout(timeout)
        self._connect()

    def get_state(self):
        """ Returns a picture of the current game state, and the current score of the game """
        data = self._read_message()
        image = self._decode_image(data["encodedImage"])
        score = data["gameScore"]
        is_over = data["gameOver"]
        # print("get_state() score: {}, is_over: {}".format(score, is_over))
        return is_over, image, score

    def send_state(self, action):
        """ Send an action command to the game """
        # print("send_state() action: {}".format(action))
        self._write_message('{"action":' + str(int(action)) + ',"resetGame":false}')

    def reset_game(self):
        # print("reset_game()")
        self._write_message('{"action":-1, "resetGame":true}')

    def close(self):
        self.soc.close()

    def _read_message(self):
        main_data = ''
        while True:
            data = self.connection.recv(1000).decode('utf-8')

            if "QUITING!" in data:
                print("Unity closing! Trying to reconnect...")
                self.connection.close()
                self._connect()
                return self._read_message()

            main_data += data
            if "}" in data: break

        try:
            decoded = json.loads(main_data)
        except json.JSONDecodeError as e:
            print("ERROR while decoding\n", main_data)
            raise e
        return decoded

    def _write_message(self, msg):
        self.connection.sendall(bytearray(msg, 'utf-8'))


    def _decode_image(self, base64_img):
        a = b64decode(base64_img)
        np_arr = np.fromstring(a, np.uint8)
        img_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img_np

    def _connect(self):
        print("Connecting to client...")
        try:
            self.soc.bind((self.host, self.port))
        except socket.error as e:
            print("Failed to bind to socket. Error: ", e)

        # Start listening on socket
        self.soc.listen(0)
        self.connection, addr = self.soc.accept()

        print("Connected with ", addr)


if __name__ == "__main__":
    from time import sleep, time
    from random import choice, randint

    client = UnityInterface('localhost', 1234)

    print("Server Started Successfully")
    last_key = 0
    while True:
        is_over, image, score = client.get_state()

        if is_over:
            print("Game over!")
            client.reset_game()
            continue

        # cv2.imshow('BrainServer', image)

        # cv2.waitKey(1)
        # k = cv2.waitKey(1) - 48
        # if k in [UP, DOWN, LEFT, RIGHT, WAIT]:
        #     last_key = k
        client.send_state(choice([0, 1, 2, 3, 4]))  # choice([UP, DOWN, LEFT, RIGHT]))




