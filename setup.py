from setuptools import setup, find_packages

setup(
    name='dqn_playground',
    version='0.1',
    description='A work directory for testing and creating Reinforcement Learning Models',
    author='Alex Thiel',
    author_email='Alex.D.Thiel@gmail.com',
    keywords='sample setuptools development',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'tensorflow']),
    install_requires=['ujson'],
)