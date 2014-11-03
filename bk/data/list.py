import urllib

from lxml import html
from google.appengine.api import urlfetch


__author__ = 'HUNGPHONGPC'

class ScheduleList(list):
    def __init__(self,*args):
        list.__init__(self,*args)
    def __getitem__(self, key):
        return list.__getitem__(self,key-1)
    def download(self,mssv):
        url = u'http://www.aao.hcmut.edu.vn/v_old/php/aao_tkb.php?goto='
        formdata = urllib.urlencode({'HOC_KY': '20141',
                                     'mssv': mssv})
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/html'}
        httpresp = urlfetch.fetch(url=url, payload=formdata, method=urlfetch.POST, headers=headers)
        if httpresp.status_code == 200:
            data = httpresp.content
            htm=html.fromstring(data)
            elems=htm.xpath('//table[@width=\'100%\' and contains(./\'MH\')]/tbody/tr[position()>1]')