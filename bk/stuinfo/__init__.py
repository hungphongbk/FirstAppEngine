# -*- coding: utf-8 -*-
import base64
import json
import re
import urllib
import datetime
from string import maketrans

import webapp2

from bk.data import StudentModel, OfflineScheduleEntity, GlobalData
from bk.data.list import ScheduleList, ExamList, SummaryList, _ScheduleList
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
        print self.mssv
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
                    self.summary = SummaryList(mssv=self.mssv)
                else:
                    self.name = 'not found'
                    return
            except BKException, e:
                self.name = str(e)

            # store thong tin sv moi vao db
            sv = StudentModel(parent=StudentModel.stu_key('bk'),
                              student_id=self.mssv,
                              student_name=self.name)
            sv.put()

        else:
            self.name = self.__stu_name

            if len(svs[0].student_offline_sc) == 0:
                self.schedule = ScheduleList(mssv=self.mssv, status='loaded before')
            else:
                self.schedule = ScheduleList(mssv=self.mssv, status='newest')
                self.schedule.details.append(
                    self.__schedulelist_from_offline(newest_sem=_ScheduleList(mssv=self.mssv, hoc_ki='20141'),
                                                     offline=svs[0].student_offline_sc))
            self.exam = ExamList(mssv=self.mssv, status='loaded before')
            self.summary = SummaryList(mssv=self.mssv, status='loaded before')

    def set_ava(self, ava):
        svs = StudentModel.find(self.mssv, 'bk')
        if len(svs) > 0:
            sv = svs[0]
            sv.student_avatar = str(ava)
            sv.put()

            self.ava = str(ava)

    def begin_update_offline_sc(self):
        svs = StudentModel.find(self.mssv, 'bk')
        if len(svs) > 0:
            sv = svs[0]
            sv.student_offline_sc = []
            sv.put()

    def add_offline_sc(self, arr):
        svs = StudentModel.find(self.mssv, 'bk')
        trans = maketrans(' ', '-')
        if len(svs) > 0:
            sv = svs[0]
            arr2 = arr[1].split()
            try:
                sv.student_offline_sc.append(OfflineScheduleEntity(subject_code=arr2[0],
                                                                   group=arr2[1],
                                                                   subject_name=arr[2],
                                                                   period=arr[3],
                                                                   room=arr[4],
                                                                   day=arr[0],
                                                                   week=arr[5].translate(trans)))
            except IndexError, e:
                print arr
            sv.put()

    def __schedulelist_from_offline(self, newest_sem, offline):
        from datetime import datetime

        newest_sem.details = []

        now = datetime.today()
        begin = GlobalData.get_semester_beginning()
        week = (now - begin).days / 7 + 1

        for entity in offline:
            print "\"%s\"" % entity.week
            if entity.week[week] != '-':
                newest_sem.details.append({'code': entity.subject_code,
                                           'name': entity.subject_name,
                                           'group': entity.group,
                                           'day': entity.day,
                                           'period': entity.period,
                                           'room': entity.room,
                                           'day2': '', 'period2': '', 'room2': ''})
        return newest_sem


class StuInfo(webapp2.RequestHandler):
    def get(self):
        param = self.request.get('param', '');
        if len(param) == 0:
            self.error(400)
        elif param == 'del':
            self.__delete(self.request.get('mssv', ''))
        elif param == 'showall':
            self.__show_all_entities()

    def post(self):
        param = self.request.get('param', '');
        if len(param) == 0:
            self.error(400)
        elif param == 'all':
            self.__get_all()

    def __get_all(self):
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

    def __delete(self, mssv):
        StudentModel.remove(mssv=mssv, school='bk')

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write("{ \"status\": \"OK\" }")

    def __show_all_entities(self):
        self.response.headers['Content-Type'] = 'application/json'

        lst = StudentModel.find(mssv=None, school='bk')
        if len(lst) == 0:
            self.response.write("{ \"status\": \"Empty\" }")
        else:
            rs = [{"student_id": i.student_id, "student_name": i.student_name}
                  for i in lst]
            content = {"status": str(len(lst)), "result": rs}
            self.response.write(json.dumps(content))


class StuInfoUpdate(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'application/json'

        typ = self.request.get('type', '')
        # print typ
        if len(typ) == 0:
            self.error(400)
        elif typ == 'ava':
            self.upload_ava()
        elif typ == 'offline_sc':
            self.upload_offline_schedule()
        elif typ == 'global':
            self.update_globaldata()

    def success(self):
        self.response.write("{\"upload_status\":\"OK\"}")

    def upload_ava(self):
        mssv = self.request.POST.get('mssv', '')
        img = self.request.POST.get('img', None)
        current = StuInfoObject(mssv=mssv)

        if img is not None:
            img_type = img.type
            img_enc = base64.b64encode(img.file.read())
            img_enc_struct = "data:%s;base64,%s" % (img_type, img_enc)
        else:
            img_enc_struct = ""

        current.set_ava(img_enc_struct)
        self.success()

    def upload_offline_schedule(self):
        mssv = self.request.POST.get('mssv', '')
        scfile = self.request.POST.get('scfile', None)
        current = StuInfoObject(mssv=mssv)

        current.begin_update_offline_sc()
        rawdata = []
        if scfile is not None:
            for line in scfile.file:
                arr = [l for l in line.split('|') if len(l) > 0]
                arr[0] = arr[0].strip()
                if len(arr) >= 5 and len(arr[0]) <= 2:
                    rawdata.append(arr)
        for i in range(0, len(rawdata)):
            if len(rawdata[i][0]) == 0:
                rawdata[i][0] = rawdata[i - 1][0]
            current.add_offline_sc(rawdata[i])
        self.success()

    def update_globaldata(self):
        date = self.request.POST.get('semester_beginning', '')
        if len(date) == 0:
            self.error(400)
            return
        GlobalData.update(date=datetime.datetime.strptime(date, u'%d-%m-%Y'))
        self.success()


app = webapp2.WSGIApplication([('/bkstuinfo', StuInfo),
                               ('/bkstuinfo/update', StuInfoUpdate)], debug=True)