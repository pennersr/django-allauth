from enum import Enum


class Client(str, Enum):
    APP = "app"
    BROWSER = "browser"
