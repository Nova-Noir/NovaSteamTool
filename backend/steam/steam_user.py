from typing import Dict

from steam_typing import Steam2FA, SteamSession
from steam_login import SteamLogin
from steam_guard import SteamGuard
from steam_exceptions import LoginRequired, LoginFailed
from steam_confirmations import SteamConfirmation


def login_required(func):
    def wrapper(self, *args, **kwargs):
        if self.is_login:
            return func(self, *args, **kwargs)
        else:
            raise LoginRequired("You should first login your steam first")
    return wrapper


class SteamUser:
    username: str
    _password: str
    _twofactor: Steam2FA
    has_two_factor: bool
    has_identity_secret: bool
    _guard: SteamGuard
    is_login: bool
    _session: SteamSession
    _confirmation: SteamConfirmation

    def __init__(self, username: str, password: str, conf: Dict = None):
        self.has_two_factor = False
        self.has_identity_secret = False
        self.is_login = False
        self.update(username, password, conf)

    async def login(self, **kwargs):
        login = SteamLogin(self.username, self._password)
        if self.has_two_factor:
            res = await login.login(guard_code=self.get_guard_code(), **kwargs)
        else:
            res = await login.login(**kwargs)
        if res.success:
            self.is_login = True
            self._session = SteamSession(res)
            self._confirmation = SteamConfirmation(self._twofactor.identity_secret,
                                                   self._twofactor.device_id,
                                                   self._session)
        else:
            if res.requires_twofactor:
                raise LoginFailed("Two Factor Authentication Code needed or was wrong set!")
            if res.captcha_needed:
                raise LoginFailed(f"Captcha needed! captcha_gid = {res.captcha_gid}")
            else:
                raise LoginFailed(f"Login Failed! Message: {res.message}")

    def update(self, username: str = None, password: str = None, conf: Dict = None):
        if username:
            self.username = username
        if password:
            self._password = password
        if conf is None:
            conf = {}
        self._twofactor = Steam2FA(conf)
        if self._twofactor.shared_secret:
            self._guard = SteamGuard(self._twofactor.shared_secret)
            self.has_two_factor = True
        if self._twofactor.identity_secret:
            self.has_identity_secret = True

    def get_guard_code(self) -> str:
        return self._guard.gen_guard_code()

    @login_required
    async def fetch_confirmations(self):
        if self.has_identity_secret:
            return await self._confirmation.fetch_confirmation_query()
