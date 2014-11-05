import json
from unittest import TestCase

__author__ = 'HUNGPHONGPC'


class TestScheduleList(TestCase):
    def test_download(self):
        from bk.data.list import ScheduleList

        s = ScheduleList()
        s.download('51202744')
        print json.dumps(s, default=lambda o: o.__dict__)
        self.assertEqual(True, True, '')