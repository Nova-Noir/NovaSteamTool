import time
import rsa
import base64

from typing import Dict
from aiohttp import ClientSession

from steam_enums import SteamURL
from steam_typing import Response


class SteamLogin:
    username: str
    _password: str

    def __init__(self, username: str, password: str):
        self.username = username
        self._password = password

    async def login(self,
                    guard_code: str = '',
                    captcha_id: str = '',
                    captcha_text: str = '',
                    email_auth: str = '',
                    headers: Dict = None,
                    cookies: Dict = None,
                    **kwargs
                    ):
        if headers is None:
            headers = {
                "X-Requested-With": "com.valvesoftware.android.steam.community",
                "Referer": "https://steamcommunity.com/mobilelogin?oauth_client_id=DEADBEEF&oauth_scope"
                           "=read_profile%20write_profile%20read_client%20write_client"
            }
        if cookies is None:
            cookies = {
                "mobileClientVersion": "0 (2.3.13)",
                "mobileClient": "android",
                "Steam_Language": "schinese"
            }

        async with ClientSession(headers=headers, cookies=cookies, **kwargs) as session:
            data = {
                "donotcache": int(time.time() * 1000),
                "username": self.username
            }
            async with session.post(SteamURL.GET_RSA_KEY_API_URL, data=data) as resp:
                if resp.status == 200 and (response := await resp.json()).get("success"):
                    response = Response(response)
                    modulus = int(response.publickey_mod, 16)
                    exponent = int(response.publickey_exp, 16)
                    rsa_timestamp = response.timestamp
                else:
                    if resp.status == 200:
                        raise ConnectionError(f"Get RSA Key Error! [{resp.status}]: {response}")
                    else:
                        raise ConnectionError(f"Get RSA Key Error! Error Code: {resp.status}")

            data = {
                "donotcache": int(time.time() * 1000),
                "username": self.username,
                "password": self.gen_rsa_password(modulus, exponent),
                "rsatimestamp": rsa_timestamp,
                "remember_login": True
            }
            if guard_code:
                data['twofactorcode'] = guard_code
            if email_auth:
                data['emailauth'] = email_auth
            if captcha_id and captcha_text:
                data["captchagid"] = captcha_id
                data["captcha_text"] = captcha_text

            async with session.post(SteamURL.DO_LOGIN_API_URL, data=data) as resp:

                if resp.status == 200:
                    response = Response(await resp.json())
                    if response.success:
                        response.cookie = resp.cookies.output()
                        response.cookie_object = resp.cookies
                    return response
                else:
                    raise ConnectionError(f"Login Error! Error Code: {resp.status}")

    def gen_rsa_password(self, m: int, e: int) -> str:
        public_key = rsa.PublicKey(m, e)
        en_password = self._password.encode(encoding='UTF-8')
        en_password = rsa.encrypt(en_password, public_key)
        en_password = base64.b64encode(en_password)
        return en_password.decode("UTF-8")
