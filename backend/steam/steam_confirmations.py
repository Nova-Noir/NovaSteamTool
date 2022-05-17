import time
import base64
import hmac
import hashlib

from typing import Union, Dict, List
from aiohttp import ClientSession
from urllib.parse import urlencode
from bs4 import BeautifulSoup


from steam_enums import SteamURL
from steam_typing import SteamSession


class SteamConfirmation:

    def __init__(self, identity_secret: str, device_id: str, cookie: SteamSession):
        self.identity_secret = identity_secret
        self.device_id = device_id
        self.cookie = cookie

    def _gen_confirmation_key(self, times: Union[int, float] = None, tag: str = 'conf') -> str:
        if times is None:
            times = int(time.time())
        elif isinstance(times, float):
            times = int(times)
        msg = times.to_bytes(8, byteorder='big', signed=False) + tag.encode('UTF-8')
        key = base64.b64decode(self.identity_secret.encode('UTF-8'))
        secret = hmac.new(key, msg, hashlib.sha1).digest()
        return base64.b64encode(secret).decode('UTF-8')

    async def fetch_confirmation_query(self,
                                       tag: str = "conf",
                                       m: str = "android",
                                       headers: Dict = None,
                                       **kwargs) -> Dict[str, Union[str, List[Dict]]]:
        if headers is None:
            headers = {
                "X-Requested-With": "com.valvesoftware.android.steam.community",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
        times = int(time.time())
        query = {
            "p": self.device_id,
            "a": self.cookie.steamid,
            "k": self._gen_confirmation_key(times),
            "t": times,
            "m": m,
            "tag": tag
        }

        async with ClientSession(headers=headers, cookies=self.cookie.cookie_O, **kwargs) as session:
            async with session.get(f'{SteamURL.MOBILECONF_URL}?{urlencode(query)}') as resp:
                if resp.status == 200:
                    return SteamParser.steam_confirmation_parser((await resp.read()).decode('UTF-8'))
                else:
                    raise ConnectionError(f"Fetch Confirmation Error! Error Code: {resp.status}")

    async def send_confirmation_ajax(self,
                                     cid: str,
                                     ck: str,
                                     times: Union[int, float] = None,
                                     op: str = "allow",
                                     m: str = "android",
                                     headers: Dict = None) -> bool:
        if times is None:
            times = int(time.time())
        elif isinstance(times, float):
            times = int(times)
        if headers is None:
            headers = {
                "X-Requested-With": "XMLHttpRequest",
            }
        query = {
            "op": op,
            "tag": op,
            "p": self.device_id,
            "a": self.cookie.steamid,
            "k": self._gen_confirmation_key(times, op),
            "t": times,
            "m": m,
            "cid": cid,
            "ck": ck
        }
        async with ClientSession(headers=headers, cookies=self.cookie.cookie_O) as session:
            async with session.post(f'{SteamURL.CONF_AJAX_POST_URL}?{urlencode(query)}') as resp:
                if resp.status == 200:
                    return (await resp.json()).get('success')
                else:
                    raise ConnectionError(f"Send Confirmation Ajax Error! Error Code: {resp.status}")

    async def fetch_confirmation_details(self,
                                         cid: str,
                                         times: Union[int, float] = None,
                                         m: str = "android",
                                         headers: Dict = None) -> Dict[str, str]:
        if headers is None:
            headers = {
                "X-Requested-With": "com.valvesoftware.android.steam.community",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
        if times is None:
            times = int(time.time())
        elif isinstance(times, float):
            times = int(times)
        tag = f"details{cid}"
        query = {
            "tag": tag,
            "p": self.device_id,
            "a": self.cookie.steamid,
            "k": self._gen_confirmation_key(times, tag),
            "t": times,
            "m": m,
        }
        async with ClientSession(headers=headers, cookies=self.cookie.cookie_O) as session:
            async with session.get(SteamURL.CONF_DETAIL_URL + cid + '?' + urlencode(query)) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise ConnectionError(f"Fetch Confirmation Details Error! Error Code: {resp.status}")


class SteamParser:
    @staticmethod
    def steam_confirmation_parser(html: str):
        soup = BeautifulSoup(html, 'lxml')
        confirmations = soup.find_all("div", class_="mobileconf_list_entry")
        if len(confirmations):
            data_list = []
            for confirmation in confirmations:
                data = {
                    "type": confirmation.get('data-type'),
                    "confid": confirmation.get('data-confid'),
                    "key": confirmation.get('data-key'),
                    "creator": confirmation.get('data-creator'),
                    "accept_text": confirmation.get('data-accept'),
                    "cancel_text": confirmation.get('data-cancel'),
                    "img": confirmation.find('img')['src'],
                    "desc": "\n".join(confirmation.stripped_strings)
                }
                data_list.append(data)
            return {
                "success": True,
                "data": data_list
            }
        return {
            "success": soup.find('div', id="mobileconf_empty") is not None,
            "data": ["\n".join(soup.find('div', id="mobileconf_empty").stripped_strings)]
            if soup.find('div', id="mobileconf_empty") else ["Invalid Html\nIt is not a parsable html."]
        }
