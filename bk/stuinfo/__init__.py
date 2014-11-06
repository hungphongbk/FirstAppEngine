# -*- coding: utf-8 -*-
import base64
import json
import re
import urllib

import webapp2

from bk.data import StudentModel
from bk.data.list import ScheduleList, ExamList
from bk.util import send_post_request, BKException


class StuInfoObject(object):
    __regex = re.compile(r'<font[\s\S]+?color=\"#3300CC\"([\s\S])+?><[^>]+?>(([\s\S])+?)\.</[^>]+?></font>')

    def __init__(self, mssv):
        self.mssv = mssv
        self.__stu_name = self.name = ''
        self.__schedule_last = None
        self.__exam_last = None
        self.ava = ''

    def get_name(self):
        svs = StudentModel.find(self.mssv, 'bk')
        if len(svs) > 0:
            self.__stu_name = svs[0].student_name
            self.__schedule_last = svs[0].schedule_last_updated.isoformat()
            self.__exam_last = svs[0].exam_last_updated.isoformat()
            self.ava = svs[0].student_avatar

        # fix dieu kien tra ve du lieu day du hay thoi gian cap nhat cuoi
        if len(self.__stu_name) == 0:
            url = u'http://www.aao.hcmut.edu.vn/v_old/php/aao_tkb.php?goto='
            formdata = urllib.urlencode({'HOC_KY': '20141',
                                         'mssv': self.mssv})
            try:
                data = send_post_request(url, formdata)
                print len(data)
                stu_name = re.search(self.__regex, data)
                if stu_name:
                    self.name = stu_name.group(2).split('-')[0]

                    self.schedule = ScheduleList(mssv=self.mssv)
                    self.exam = ExamList(mssv=self.mssv)
                else:
                    self.name = 'not found'
                    # self.name = base64.b64encode(self.name)
            except BKException, e:
                # self.name = base64.b64encode(str(e))
                self.name = str(e)

            # store thong tin sv moi vao db
            sv = StudentModel(parent=StudentModel.stu_key('bk'),
                              student_id=self.mssv,
                              student_name=self.name)
            sv.put()
        else:
            self.name = self.__stu_name
            self.schedule = ScheduleList(mssv=self.mssv, status='loaded before')
            self.exam = ExamList(mssv=self.mssv, status='loaded before')

    def set_ava(self, ava):
        svs = StudentModel.find(self.mssv, 'bk')
        if len(svs) > 0:
            sv = svs[0]
            sv.student_avatar = str(ava)
            sv.put()

            self.ava = str(ava)


class StuInfo(webapp2.RequestHandler):
    def post(self):
        mssv = self.request.get('mssv', '')
        self.response.headers['Content-Type'] = 'application/json'
        current = StuInfoObject(mssv=mssv)
        try:
            current.get_name()
            content = json.dumps(current,
                                 default=lambda o: {k: v for k, v in o.__dict__.iteritems() if
                                                    not (k.startswith('_') or v is None)})
            # content=unicode(content,'utf-8')
            self.response.write(content)
        except BKException:
            self.response.write("{ \"mssv\" : \"not found\" }")


class StuInfoUploadAva(webapp2.RequestHandler):
    def post(self):
        print 'catched'
        self.response.headers['Content-Type'] = 'application/json'

        mssv = self.request.get('mssv', '')
        img = self.request.POST.get('img', None)
        current = StuInfoObject(mssv=mssv)

        if img is not None:
            print img
            img_type = img.type
            img_enc = base64.b64encode(img.file.read())
            img_enc_struct = "data:%s;base64,%s" % (img_type, img_enc)
        else:
            img_enc_struct = ""

        current.set_ava(img_enc_struct)
        self.response.write("{'upload_status':'OK'}")


app = webapp2.WSGIApplication([('/bkstuinfo', StuInfo),
                               ('/bkstuinfo/update-ava', StuInfoUploadAva)], debug=True)