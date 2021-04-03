from abc import ABC

from CONSTS import C
from requests import Session
from html.parser import HTMLParser
# from requests_oauthlib import OAuth2Session


class WardenclyffeHiddenParamParser(HTMLParser, ABC):
    def __init__(self):
        super().__init__()
        self.in_form = False
        self.hidden_data = {}

    def handle_starttag(self, tag, attrs):
        d_attrs = dict(attrs)
        if str(tag) == 'form':
            self.in_form = True
            print('yup!')
        elif str(tag) == 'input' and self.in_form and d_attrs.get('type', '').lower() == 'hidden':
            if 'name' in d_attrs and 'value' in d_attrs:
                self.hidden_data[d_attrs['name']] = d_attrs['value']
                print('name: %s' % d_attrs['name'], 'value: %s' % d_attrs['value'])

    def handle_endtag(self, tag):
        pass
        # print("Encountered an end tag :", tag)

    def handle_data(self, data):
        pass
        # print("Encountered some data  :", data)


class ProjectWardenclyffe(Session):
    def __init__(self, username, password, **kwargs):
        super(ProjectWardenclyffe, self).__init__()

        self.username = username
        self.password = password

    def authenticate(self):
        p = WardenclyffeHiddenParamParser()
        # TODO: consider using `from requests_oauthlib import OAuth2Session` instead.
        r = self.get(C.AUTH_BASE_URL + C.AUTH_ENDPOINT_V3_AUTHORIZE, params=C.AUTH_INIT_VALUES)
        print(r.status_code)
        p.feed(r.text)
        # oauth = OAuth2Session(client_id=C.HTTP_GET_VALUE_OWNERAPI, scope=('openid', 'email', 'offline_access'),
        #                       redirect_uri=C.HTTP_GET_VALUE_VOID_CALLBACK)


def main():
    # for k,v in C.AUTH_INIT_VALUES.items():
    #     if isinstance(v, bytes):
    #         print(k)


    pw = ProjectWardenclyffe(C.USERNAME, C.PASSWORD)
    pw.authenticate()


if __name__ == '__main__':
    main()