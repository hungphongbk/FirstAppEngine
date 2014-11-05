from google.appengine.api import urlfetch

__author__ = 'HUNGPHONGPC'

class BKException(Exception):
    pass

def send_get_request(url):
    try:
        httpresp = urlfetch.fetch(url=url, method=urlfetch.GET)
    except:
        import requests

        httpresp = requests.get(url)
    code = httpresp.status_code
    if code == 200:
        return httpresp.content
    else:
        raise BKException('Server error')


def send_post_request(url, form):
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'text/html'}
    try:
        httpresp = urlfetch.fetch(url=url, method=urlfetch.POST, headers=headers, payload=form)
    except:
        import requests

        httpresp = requests.post(url, data=form, headers=headers)
    code = httpresp.status_code
    if code == 200:
        return httpresp.content
    else:
        raise BKException("Server error")