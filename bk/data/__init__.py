__author__ = 'HUNGPHONGPC'
from google.appengine.ext import ndb


class StudentModel(ndb.Model):
    student_id = ndb.StringProperty(repeated=False)
    student_name = ndb.StringProperty()
    schedule_last_updated = ndb.DateTimeProperty(auto_now_add=True)
    exam_last_updated = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def find(cls, mssv, school):
        return cls.query(ancestor=cls.stu_key(school)).filter(cls.student_id == mssv).fetch()

    @classmethod
    def stu_key(cls, school):
        return ndb.Key('school_name', school)