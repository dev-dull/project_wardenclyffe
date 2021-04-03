import os
import yaml
from hashlib import sha256
from random import shuffle
from base64 import urlsafe_b64encode
from string import ascii_letters, digits

# This file hijacks the order in which Python parses the file in order to create user-configurable items.
class C(object):
    # Below are user-configurable items via config.yaml and creds.yaml
    API_BASE_URL = 'https://owner-api.teslamotors.com/'
    AUTH_BASE_URL = 'https://auth.tesla.com/'

    USERNAME = ''
    PASSWORD = ''

    SSL_VERIFY = True

    # Below are items that the user should not be allowed to set via configuration file
    # This section only exists so IDEs won't complain about missing variables.
    AUTH_ENDPOINT_V3_AUTHORIZE = ''
    AUTH_ENDPOINT_VOID_CALLBACK = ''

    HEADER_KEYWORD_USER_AGENT = ''

    HEADER_VALUE_USER_AGENT = ''

    HEADERS = None

    HTTP_GET_KEYWORD_CLIENT_ID = ''
    HTTP_GET_KEYWORD_CODE_CHALLENGE = ''
    HTTP_GET_KEYWORD_CODE_CHALLENGE_METHOD = ''
    HTTP_GET_KEYWORD_REDIRECT_URI = ''
    HTTP_GET_KEYWORD_RESPONSE_TYPE = ''
    HTTP_GET_KEYWORD_SCOPE = ''
    HTTP_GET_KEYWORD_STATE = ''
    HTTP_GET_KEYWORD_LOGIN_HINT = ''

    HTTP_GET_VALUE_OWNERAPI = ''
    HTTP_GET_VALUE_S256 = ''
    HTTP_GET_VALUE_VOID_CALLBACK = ''
    HTTP_GET_VALUE_CODE = ''
    HTTP_GET_VALUE_OPENID_EMAIL_OFFLINE_ACCESS = ''

    AUTH_CODE_CHARACTER_SET = None
    AUTH_CODE_VERIFY = ''
    AUTH_CODE_CHALLENGE = ''

    AUTH_INIT_VALUES = None


# This takes the contents of config.yaml and creds.yaml and updates the values in class C
for configuration_filename in ['config.yaml', 'creds.yaml']:
    _fin = open(configuration_filename, 'r')
    yams = _fin.read()
    _fin.close()
    yaml_config = yaml.load(yams, Loader=yaml.SafeLoader)
    for k, v in yaml_config.items():
        setattr(C, k, v)


# Finally, set the constant values where the user can no longer update them
C.HEADER_KEYWORD_USER_AGENT = 'User-Agent'
C.HEADER_VALUE_USER_AGENT = 'adrong+TeslaTest@gmail.com'
C.HEADERS = {C.HEADER_KEYWORD_USER_AGENT: C.HEADER_VALUE_USER_AGENT}

C.AUTH_ENDPOINT_V3_AUTHORIZE = 'oauth2/v3/authorize'
C.AUTH_ENDPOINT_VOID_CALLBACK = 'void/callback'

C.HTTP_GET_KEYWORD_CLIENT_ID = 'client_id'
C.HTTP_GET_KEYWORD_CODE_CHALLENGE = 'code_challenge'
C.HTTP_GET_KEYWORD_CODE_CHALLENGE_METHOD = 'code_challenge_method'
C.HTTP_GET_KEYWORD_REDIRECT_URI = 'redirect_uri'
C.HTTP_GET_KEYWORD_RESPONSE_TYPE = 'response_type'
C.HTTP_GET_KEYWORD_SCOPE = 'scope'
C.HTTP_GET_KEYWORD_STATE = 'state'
C.HTTP_GET_KEYWORD_LOGIN_HINT = 'login_hint'

C.HTTP_GET_VALUE_OWNERAPI = 'ownerapi'
C.HTTP_GET_VALUE_S256 = 'S256'
C.HTTP_GET_VALUE_VOID_CALLBACK = C.AUTH_BASE_URL + C.AUTH_ENDPOINT_VOID_CALLBACK
C.HTTP_GET_VALUE_CODE = 'code'
C.HTTP_GET_VALUE_OPENID_EMAIL_OFFLINE_ACCESS = 'openid email offline_access'


# code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=')
# unencoded_digest = hashlib.sha256(code_verifier).digest()
# code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier).digest()).rstrip(b'=')

# C.AUTH_CODE_CHARACTER_SET = list(ascii_letters*2 + digits*2)
# shuffle(C.AUTH_CODE_CHARACTER_SET)
C.AUTH_GET_CODE_VERIFY = urlsafe_b64encode(os.urandom(32)).rstrip(b'=')
C.AUTH_GET_CODE_CHALLENGE = urlsafe_b64encode(sha256(C.AUTH_GET_CODE_VERIFY).digest()).rstrip(b'=')

C.AUTH_INIT_VALUES = {
    C.HTTP_GET_KEYWORD_CLIENT_ID: C.HTTP_GET_VALUE_OWNERAPI,
    C.HTTP_GET_KEYWORD_CODE_CHALLENGE: str(C.AUTH_GET_CODE_CHALLENGE),
    C.HTTP_GET_KEYWORD_CODE_CHALLENGE_METHOD: C.HTTP_GET_VALUE_S256,
    C.HTTP_GET_KEYWORD_REDIRECT_URI: C.HTTP_GET_VALUE_VOID_CALLBACK,
    C.HTTP_GET_KEYWORD_RESPONSE_TYPE: C.HTTP_GET_VALUE_CODE,
    C.HTTP_GET_KEYWORD_SCOPE: C.HTTP_GET_VALUE_OPENID_EMAIL_OFFLINE_ACCESS,
    C.HTTP_GET_KEYWORD_STATE: 'Any random string?',  # "The OAuth state value. Any random string."
    C.HTTP_GET_KEYWORD_LOGIN_HINT: C.USERNAME
}