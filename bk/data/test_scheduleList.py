import json
from unittest import TestCase

__author__ = 'HUNGPHONGPC'


class TestScheduleList(TestCase):
    def test_download(self):
        from bk.data.list import ScheduleList

        s = ScheduleList('51202744')
        print s.details[0].__dict__
        print json.dumps(s, default=lambda o: {k: v for k, v in o.__dict__.iteritems() if
                                                    not (k.startswith('_') or v is None)})
        self.assertEqual(True, True, '')