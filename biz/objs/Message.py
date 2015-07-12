# coding: utf-8
import json


class Level(object):
    sys = 0b1
    user = 0b10
    info = 0b100
    warn = 0b1000


class Msg(object):
    __slots__ = ('level', 'title', 'content')

    def __init__(self, title='untitled', content='nothing', level=Level.sys | Level.info):
        self.title = title
        self.content = content
        self.level = level


    def toString(self):
        return json.dumps({
            'level': self.level,
            'title': self.title,
            'content': self.content
        })
