import functools
import logging
from pkg_resources import iter_entry_points

class Plugin(object):
    def __init__(self, config, bus, loop):
        self.config = config
        self._bus = bus
        self._bus.register(self.channel, self)
        self._loop = loop

    def on_event(self, **kwargs):
        pass

    def send_event(self, name, **kwargs):
        partial = functools.partial(self._bus.notify, name, **kwargs)
        self._loop.run_in_executor(None, partial)

    def add_timer(self, timeout, cb, *args, **kwargs):
        partial = functools.partial(cb, *args, **kwargs)
        return self._loop.call_later(timeout, partial)

class LightsPlugin(Plugin):
    channel = 'lights'

class PresencePlugin(Plugin):
    channel = 'presence'
