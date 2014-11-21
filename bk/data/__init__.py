from bk.util import BKException

__author__ = 'HUNGPHONGPC'
from google.appengine.ext import ndb


class GlobalData(ndb.Model):
    semester_beginning = ndb.DateTimeProperty()

    @classmethod
    def update(cls, date, school='bk'):
        lst = cls.query(ancestor=cls.global_key(school=school)).fetch()
        if len(lst) == 0:
            dt = GlobalData(parent=cls.global_key(school=school),
                            semester_beginning=date)
            dt.put()
        else:
            lst[0].semester_beginning = date
            lst[0].put()

    @classmethod
    def get_semester_beginning(cls,school='bk'):
        lst = cls.query(ancestor=cls.global_key(school=school)).fetch()
        if len(lst)==0:
            raise BKException('null')
        else:
            return lst[0].semester_beginning

    @classmethod
    def global_key(cls, school):
        return ndb.Key('school_name', school)


class OfflineScheduleEntity(ndb.Model):
    subject_code = ndb.StringProperty()
    subject_name = ndb.StringProperty()
    group = ndb.StringProperty()
    day = ndb.StringProperty()
    period = ndb.StringProperty()
    room = ndb.StringProperty()
    week = ndb.StringProperty()


class StudentModel(ndb.Model):
    student_id = ndb.StringProperty(repeated=False)
    student_name = ndb.StringProperty()
    student_avatar = ndb.TextProperty(default=None)

    schedule_last_updated = ndb.DateTimeProperty(auto_now_add=True)
    exam_last_updated = ndb.DateTimeProperty(auto_now_add=True)
    student_offline_sc = ndb.StructuredProperty(OfflineScheduleEntity, repeated=True)

    @classmethod
    def find(cls, mssv, school):
        if mssv is None or len(mssv) == 0:
            return cls.query(ancestor=cls.stu_key(school)).fetch()
        return cls.query(ancestor=cls.stu_key(school)).filter(cls.student_id == mssv).fetch()

    @classmethod
    def remove(cls, mssv, school):
        if len(mssv) == 0:
            result = cls.find(mssv=mssv, school=school)
            if len(result) > 0:
                result[0].key.delete()
        else:
            result = cls.find(school=school)
        for item in result:
            item.key.delete()

    @classmethod
    def stu_key(cls, school):
        return ndb.Key('school_name', school)


