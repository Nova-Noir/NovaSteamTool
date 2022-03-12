from typing import AnyStr, Dict, Union
from http.cookies import SimpleCookie

from utils import gen_device_id


class Steam2FA:
    shared_secret: str
    identity_secret: str
    device_id: str

    def __init__(self, conf: Dict):
        self.shared_secret = conf.get('shared_secret', '')
        self.identity_secret = conf.get('identity_secret', '')
        self.device_id = conf.get('device_id', gen_device_id())


class U_Dict(Dict):
    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)


class Response(U_Dict):
    cookie_object: SimpleCookie
    success: bool


class SteamSession(U_Dict):
    steamid: str
    token_secure: str
    auth: str
    webcookie: str
    cookie: str
    cookie_O: SimpleCookie

    def __init__(self, resp: Response):
        super().__init__()
        auth = resp.transfer_parameters
        self.steamid = auth.get('steamid')
        self.token_secure = auth.get('token_secure')
        self.auth = auth.get('auth')
        self.webcookie = auth.get('webcookie')
        self.cookie = resp.cookie
        self.cookie_O = resp.cookie_object
