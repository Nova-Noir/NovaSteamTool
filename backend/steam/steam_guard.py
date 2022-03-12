import base64
import time
import hmac
import hashlib

from typing import Union


class SteamGuard:
    def __init__(self, shared_secret: str):
        self.shared_secret = shared_secret.encode('UTF-8')

    def gen_guard_code(self, times: Union[float, int] = None) -> str:
        if times is None:
            times = int(time.time())
        else:
            if isinstance(time, float):
                times = int(times)
        time_bytes = (times // 30).to_bytes(8, byteorder='big')
        hmac_code = hmac.new(base64.b64decode(self.shared_secret), time_bytes, hashlib.sha1).digest()
        byte_offset = hmac_code[-1] & 0xf
        code_int = (
                (hmac_code[byte_offset] & 0x7f) << 24 |
                (hmac_code[byte_offset + 1] & 0xff) << 16 |
                (hmac_code[byte_offset + 2] & 0xff) << 8 |
                (hmac_code[byte_offset + 3] & 0xff)
        )
        CODE_CHARSET = [50, 51, 52, 53, 54, 55, 56, 57, 66, 67, 68, 70, 71,
                        72, 74, 75, 77, 78, 80, 81, 82, 84, 86, 87, 88, 89]
        codes = ''
        for _ in range(5):
            code_int, i = divmod(code_int, len(CODE_CHARSET))
            codes += chr(CODE_CHARSET[i])
        return codes
