
class SteamURL:
    BASE_STEAM_URL = "https://steamcommunity.com"
    GET_RSA_KEY_API_URL = f"{BASE_STEAM_URL}/login/getrsakey/"
    DO_LOGIN_API_URL = f"{BASE_STEAM_URL}/login/dologin/"
    LOGIN_URL = BASE_STEAM_URL + "/login?oauth_client_id=DEADBEEF&oauth_scope=read_profile%20write_profile" \
                                 "%20read_client%20write_client "
    MOBILECONF_URL = f"{BASE_STEAM_URL}/mobileconf/conf"
    CONF_AJAX_POST_URL = f"{BASE_STEAM_URL}/mobileconf/ajaxop"
    CONF_DETAIL_URL = f"{BASE_STEAM_URL}/mobileconf/details/"
