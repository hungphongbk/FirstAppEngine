import threading
import urllib
import datetime

from lxml import html

from bk.util import send_post_request, BKException, send_get_request


__author__ = 'HUNGPHONGPC'


def sem_list(url):
    try:
        htm = html.fromstring(send_get_request(url))
    except BKException, e:
        raise e
    return [e.get('value') for e in htm.xpath('//select[@name="HOC_KY"]/option')]


class _ScheduleList(threading.Thread):
    def run(self):
        self.__download(self.__mssv, self.hoc_ki)

    __tags = ['code', 'name', 'group', 'day', 'period', 'room', 'day2', 'period2', 'room2']

    def __init__(self, mssv, hoc_ki):
        threading.Thread.__init__(self)
        self.__mssv = mssv
        self.hoc_ki = hoc_ki

    def __download(self, mssv, hoc_ki):
        def make_item_from_elem(_elem):
            item = dict()
            pre = zip(_ScheduleList.__tags, [i for i in _elem.itertext()])
            for key, val in pre:
                item.update({key: val})
            if len(item) == 3:
                item['group'] = item['group'].split(':')[1].strip()
            return item

        # self.hoc_ki = '20141'
        url = u'http://www.aao.hcmut.edu.vn/v_old/php/aao_tkb.php?goto='
        form_data = urllib.urlencode({'HOC_KY': hoc_ki,
                                      'mssv': mssv})
        try:
            data = send_post_request(url, form_data)
            htm = html.fromstring(data)
            elems = htm.xpath('//table[@width="100%" and contains(.,"MH")]//tr[position()>1]')
            self.details = [make_item_from_elem(elem) for elem in elems]
        except BKException, e:
            raise e


class ScheduleList:
    def __init__(self, mssv, status='not yet', last_time=datetime.datetime.now().isoformat()):
        self.status = status

        if self.status == 'not yet':
            self.__download(mssv)
        else:
            self.last_updated = last_time

    def __download(self, mssv):
        url = u'http://www.aao.hcmut.edu.vn/v_old/php/aao_tkb.php?goto='
        try:
            elems = sem_list(url)
            self.details = [_ScheduleList(mssv, e) for e in elems]
            # for e in elems:
            #    sem = _ScheduleList()
            #    sem.download(mssv, e)
            #    if len(sem) == 0:
            #        break
            #    self.list.update({e: sem})
            for t in self.details:
                t.start()
            for t in self.details:
                t.join()
        except BKException, e:
            raise e


class _ExamList(threading.Thread):
    def __init__(self, mssv, hoc_ki):
        threading.Thread.__init__(self)
        self.__mssv = mssv
        self.hoc_ki = hoc_ki

    def run(self):
        super(_ExamList, self).run()

    __tags = ['code', 'name', 'group', 'daygk', 'timegk', 'roomgk', 'dayck', 'timeck', 'roomck']

    def download(self, mssv, hoc_ki):
        def make_item_from_elem(_elem):
            item = dict()
            pre = zip(_ExamList.__tags, [i for i in _elem.itertext()])
            for key, val in pre:
                item.update({key: val})
            return item

        url = u'http://www.aao.hcmut.edu.vn/v_old/php/aao_lt.php?goto='
        form_data = urllib.urlencode({'HOC_KY': hoc_ki,
                                      'mssv': mssv})
        try:
            data = send_post_request(url, form_data)
            htm = html.fromstring(data)
            elems = htm.xpath('//table[@width="100%" and contains(.,"MH")]//tr[position()>2]')
            self.details = [make_item_from_elem(elem) for elem in elems]
        except BKException, e:
            raise e


class ExamList:
    def __init__(self, mssv, status='not yet', last_time=datetime.datetime.now().isoformat()):
        self.status = status

        if self.status == 'not yet':
            self.__download(mssv)
        else:
            self.last_updated = last_time

    def __download(self, mssv):
        url = u'http://www.aao.hcmut.edu.vn/v_old/php/aao_lt.php?goto='
        try:
            self.list = dict()
            elems = sem_list(url)
            self.details = [_ScheduleList(mssv, e) for e in elems]
            for t in self.details:
                t.start()
            for t in self.details:
                t.join()
        except BKException, e:
            raise e