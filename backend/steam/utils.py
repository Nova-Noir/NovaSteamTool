from hashlib import sha1
from binascii import hexlify

from typing import AnyStr


def gen_device_id(txt: AnyStr = 'NovaSteamMarket') -> str:
    """
    Generate Device_ID by text
    :param txt: any
    :return: Device ID
    """

    if isinstance(txt, str):
        sha = sha1(txt.encode('UTF-8')).digest()
    else:
        sha = sha1(txt).hexdigest()
    src = hexlify(sha).decode("ascii")
    return f"android:{src[:8]}-{src[8:12]}-{src[12:16]}-{src[16:20]}-{src[20:28]}"
