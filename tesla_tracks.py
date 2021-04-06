import json
from abc import ABC
from CONSTS import C
from urllib import parse
from requests import Session
from html.parser import HTMLParser
# from requests_oauthlib import OAuth2Session


class HiddenDataInForm(dict):
    # Wrapper class for self._ParseForHiddenData so that usage and accessing data is more intuitive
    def __init__(self, html):
        pfhd = self._ParseForHiddenData()
        pfhd.feed(html)
        self.update(pfhd.hidden_data)

    class _ParseForHiddenData(HTMLParser, ABC):
        def __init__(self):
            super().__init__()
            self.in_form = False
            self.hidden_data = {}

        def handle_starttag(self, tag, attrs):
            d_attrs = dict(attrs)
            if str(tag) == 'form':
                self.in_form = True
            elif str(tag) == 'input' and self.in_form and d_attrs.get('type', '').lower() == 'hidden':
                if 'name' in d_attrs and 'value' in d_attrs:
                    self.hidden_data[d_attrs['name']] = d_attrs['value']

        def handle_endtag(self, tag):
            if str(tag) == 'form':
                self.in_form = False

        def handle_data(self, data):
            # This function is here for future reference.
            pass


class ProjectWardenclyffe(Session):
    def __init__(self, *args, **kwargs):
        super(ProjectWardenclyffe, self).__init__()

    def authenticate(self):
        # FUTURE,1: consider using `from requests_oauthlib import OAuth2Session` instead.
        # TODO,1: Test that response.status_code is in sensible range.
        # TODO,2: With value for login_hint populated, A 303 code means that you're trying to auth against region A but
        # TODO,2: user belongs to region B (e.g. you used auth.tesla.com when auth.tesla.cn is needed)

        # Send initial request to get header value and hidden input params required for auth
        response = self.get(C.AUTH_BASE_URL + C.AUTH_ENDPOINT_V3_AUTHORIZE, params=C.AUTH_INIT_VALUES, headers=C.HEADERS)
        form_data = HiddenDataInForm(response.text)

        # Update headers/data for next auth step
        C.HEADERS.update({'Cookie': response.headers['set-cookie']})
        form_data.update({'identity': C.USERNAME, 'credential': C.PASSWORD})

        # Submit credentials to get an authorization code
        response = self.post(C.AUTH_BASE_URL + C.AUTH_ENDPOINT_V3_AUTHORIZE, data=form_data, headers=C.HEADERS, allow_redirects=False)
        # TODO,3: Status code of 200 here means that we probably got the login page again. Locked account?
        # print(response.status_code)
        # print(response.headers['Location'])
        # print(response.text)

        auth_code = parse.parse_qs(parse.urlparse(response.headers['Location']).query)['code']
        # print('auth code:', auth_code[0])
        payload = {
            'grant_type': 'authorization_code',
            C.HTTP_GET_KEYWORD_CLIENT_ID:  C.HTTP_GET_VALUE_OWNERAPI,
            'code': auth_code,
            'code_verifier': C.AUTH_GET_CODE_VERIFY,
            C.HTTP_GET_KEYWORD_REDIRECT_URI: C.HTTP_GET_VALUE_VOID_CALLBACK
        }
        response = self.post(C.AUTH_BASE_URL + C.AUTH_ENDPOINT_V3_TOKEN, data=payload, headers=C.HEADERS)
        # print(response.status_code)
        # print(response.headers)
        # print(response.text)

        bearer_token = response.json()['access_token']
        C.HEADERS.pop('Cookie')
        C.HEADERS['Authorization'] = 'Bearer %s' % bearer_token
        payload = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'client_id': '81527cff06843c8634fdc09e8ac0abefb46ac849f38fe1e431c2ef2106796384',
            'client_secret': 'c7257eb71a564034f9419ee651c7d0e5f7aa6bfbd18bafb5c5c033b093bb2fa3'
        }
        response = self.post(C.API_BASE_URL + C.AUTH_ENDPOINT_TOKEN, data=payload, headers=C.HEADERS)
        print(response.status_code)
        print(response.headers)
        print(response.text)


def main():
    pw = ProjectWardenclyffe()
    pw.authenticate()


if __name__ == '__main__':
    main()
