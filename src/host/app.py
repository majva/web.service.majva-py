"""
    - created at 04/05/2025 by mehrad ghasempour
    - email: topcodermc@gmail.com
    - this code is entry point of application
"""

from os import path as os_path
from sys import path as sys_path, exit as sys_exit
from urllib3.exceptions import InsecureRequestWarning
import requests

# Add the project root directory to Python path
sys_path.append(os_path.dirname(os_path.dirname(os_path.dirname(os_path.abspath(__file__)))))

from src.host.host_collection import WebHostCollection

# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class App:

    def __init__(self):
        pass

    def start_up(self):
        WebHostCollection.main()


if __name__ == '__main__':
    try:
        App().start_up()
    except KeyboardInterrupt:
        print("[-] Somebody stop the service ...")
        sys_exit(0)
