import subprocess
import os
from pathlib import Path

import cv2
import numpy as np
from gym import spaces

from easyinference.utils.context_timer import ContextTimer
from unity_server.server import UnityInterface

EXECUTABLE_PATH = ""
NUM_ACTIONS = 3

class Wrapper:
    pass

class CustomUnityEnv(Wrapper):
    MIN_STEPS_BETWEEN_RESTARTS = 540000
    EXECUTABLE_PATH = "C:\\Users\\Alex Thiel\\Google Drive\\Project - 2018 - Deep Reinforcement Learning\\DRL_Playground\\build\\ballgame.exe"

    observation_space = spaces.Box(0, 0, shape=(84, 84, 1))
    action_space = spaces.Discrete(n=NUM_ACTIONS)

    def __init__(self):
        self.steps_since_restart = 0
        self.total_steps_ever = 0
        self.latest_total_score = 0
        self.episode_rewards = []

        # Make sure there aren't any other unity processes running
        self._kill_unity()

        # Run server
        self._open_unity()
        self.server = UnityInterface("localhost", 1234)


    @property
    def env(self):
        # This is for fooling the get_wrapper_by_name function
        parent = self
        class Monitor:
            def get_total_steps(self):
                return parent.total_steps_ever
            def get_episode_rewards(self):
                return parent.episode_rewards
        return Monitor()

    def step(self, action):
        """Return observation, reward, done, info
        info is unused"""
        self.steps_since_restart += 1
        self.total_steps_ever += 1

        # Send a state and get a response
        with ContextTimer(post_print=False) as timer:
            self.server.send_state(action)
            is_over, image, new_score = self._get_state()

        # Print FPS?
        if self.total_steps_ever % 1000 == 0:
            print("FPS", 1 / timer.elapsed)

        # Update the score and log info
        reward = new_score - self.latest_total_score
        self.latest_total_score = new_score
        self.episode_rewards.append(reward)

        return image, reward, is_over, None

    def reset(self):
        """Return the first observation after reset"""
        # Reset the game
        self.server.send_reset()
        is_over, image, new_score = self._get_state()
        self.latest_total_score = new_score
        self.episode_rewards = []
        return image

    def close(self):
        """Called after all training is done"""
        pass

    def _get_state(self):
        """"""
        is_over, image, new_score = self.server.get_state()
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_gray = np.expand_dims(image_gray, axis=2)
        return is_over, image_gray, new_score

    def _open_unity(self):
        print("Running Unity process")
        subprocess.Popen([self.EXECUTABLE_PATH])

    def _kill_unity(self):
        process_name = Path(self.EXECUTABLE_PATH).name
        print("Killing Unity process", process_name)
        os.system("taskkill /f /im " + process_name)


def benchmark_spec(*args, **kwargs):
    class Task:
        max_timesteps = 40000000

    class Benchmark:
        tasks = [Task(), Task(), Task(), Task()]

    return Benchmark()


def make(*args, **kwargs):
    print("Getting environment!")
    return CustomUnityEnv()
