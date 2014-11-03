# -*- coding: utf-8 -*-
import json
import re
import urllib

from google.appengine.api import urlfetch
import webapp2


class BKException(Exception):
    pass


class StuInfoObject(object):
    __regex = re.compile(r'<font[\s\S]+?color=\"#3300CC\"([\s\S])+?><[^>]+?>(([\s\S])+?)\.</[^>]+?></font>')

    def __init__(self):
        self.mssv = ''
        self.name = ''

    def __init__(self, mssv):
        self.mssv = mssv

    def getName(self):
        url = u'http://www.aao.hcmut.edu.vn/v_old/php/aao_tkb.php?goto='
        formdata = urllib.urlencode({'HOC_KY': '20141',
                                     'mssv': self.mssv})
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/html'}

        httpresp = urlfetch.fetch(url=url, payload=formdata, method=urlfetch.POST, headers=headers)
        if httpresp.status_code == 200:
            data = httpresp.content
            # print data
            mStuName = re.search(self.__regex, data)
            if mStuName:
                self.name = mStuName.group(2).split('-')[0].decode('utf-8')
            else:
                self.name = 'not found'
        else:
            raise BKException("Server error")


class StuInfo(webapp2.RequestHandler):
    def post(self):
        mssv = self.request.get('mssv', '')
        self.response.headers['Content-Type'] = 'application/json'
        current = StuInfoObject(mssv=mssv)
        try:
            current.getName()
            content=json.dumps(current, default=lambda o: o.__dict__)
            #content=unicode(content,'utf-8')
            self.response.write(content)
        except BKException:
            self.response.write("{ \"mssv\" : \"not found\" }")


app = webapp2.WSGIApplication([('/stuinfo', StuInfo)], debug=True)