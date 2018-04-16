from abc import ABC, abstractmethod
from pathlib import Path
import subprocess


import cv2

from unity_server.server import UnityInterface


class UnityALEWrapper(ABC):
    def __init__(self, executable_path, action_set, screen_dim, host, port):
        """
        :param action_set: An array of integers to send to unity
        :param screen_dim: (width, height) of the screen
        :param record_data: True/False. If true, images will be saved
        """
        self.executable_path = executable_path
        self.action_set = action_set
        self.screen_dim = screen_dim

        self.loadROM()

        self.server = UnityInterface(host, port)
        self.reset_game()

    def kill_process(self):
        process_name = Path(self.executable_path).name
        print("Killing Unity: ", "taskkill /IM " + process_name)
        subprocess.call("taskkill /IM " + process_name)


    def act(self, action):
        """ Must return the reward """
        self.is_game_over, latest_color_frame, new_score = self.server.get_state()

        # Calculate reward and store the new score
        reward = new_score - self.latest_total_score
        self.latest_total_score = new_score

        # Convert the latest frame to grayscale
        self.latest_frame_bgr = latest_color_frame
        self.server.send_state(action)

        if reward != 0: print("Received reward of ", reward)
        return reward

    def getScreenGrayscale(self, screen_buffer):
        """ Fill the screen buffer with the latest frame """
        gray = cv2.cvtColor(self.latest_frame_bgr, cv2.COLOR_BGR2GRAY)
        screen_buffer[...] = gray

    def getScreenColor(self, screen_buffer):
        """ Fill the screen buffer with the latest frame """
        screen_buffer[...] = self.latest_frame_bgr

    def reset_game(self):
        self.server.get_state()
        self.server.send_reset()
        self.is_game_over = False
        self.latest_total_score = 0
        self.latest_frame_bgr = None

    def lives(self):
        return 1

    def game_over(self):
        """ Returns True or False """
        return self.is_game_over

    def getScreenDims(self):
        """ Return width, height of the screen"""
        return self.screen_dim

    def getMinimalActionSet(self):
        return self.action_set

    # The following functions are only there to maintain compatibility
    def setInt(self, *args): pass

    def setBool(self, *args): pass

    def setFloat(self, *args): pass

    def loadROM(self, *args):
        print("Starting Unity: ", self.executable_path)
        subprocess.Popen([self.executable_path])