__author__ = 'HUNGPHONGPC'
class ItemBase:
    def __init__(self):
        pass
    def __init__(self,attrs):
        for attr in attrs:
            setattr(self,attr,attrs[attr])

class ScheduleItem(ItemBase):
    pass