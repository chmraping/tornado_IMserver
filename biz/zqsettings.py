# coding: utf-8
from lib.autoconf import conf_drawer


urls = {}
zq_events = {}
zq_events_txt = {}
STATUS = {}


@conf_drawer.register_my_setup(look='live_zq')
def setup(c):
    urls.update(c.get('urls'))
    zq_events.update(c.get('zq_events'))
    zq_events_txt.update(c.get('zq_events_txt'))
    STATUS.update(c.get('onlive_status'))
