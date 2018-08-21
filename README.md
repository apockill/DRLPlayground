# Deep Reinforcement Learning Playground
A deep reinforcement learning playground with Unity running the game physics, and Python handling the reinforcement learning algorithms.

The Unity server has a script that hosts a server which waits for a python process to connect to it. Once it has connected, it will forward images of the game world (and information about the game state) to the python process, and wait for a response. The python process is expected to respond with some action to perform in the game. Unity will perform this action, and render the next frame.
