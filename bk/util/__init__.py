from google.appengine.api import urlfetch

__author__ = 'HUNGPHONGPC'


class BKException(Exception):
    pass


def send_get_request(url):
    try:
        http_resp = urlfetch.fetch(url=url, method=urlfetch.GET)
    except:
        import requests

        http_resp = requests.get(url)
    code = http_resp.status_code
    if code == 200:
        return http_resp.content
    else:
        raise BKException('Server error')


def send_post_request(url, form):
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'text/html'}
    try:
        http_resp = urlfetch.fetch(url=url, method=urlfetch.POST, headers=headers, payload=form)
    except:
        import requests

        http_resp = requests.post(url, data=form, headers=headers)
    code = http_resp.status_code
    if code == 200:
        return http_resp.content
    else:
        raise BKException("Server error")