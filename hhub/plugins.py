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

def load_plugins(config, loop, channel):
    plugins = []
    for obj in iter_entry_points(group='hhub.plugin', name=None):
        cls = obj.load()
        logging.info('Found %s plugin: %s' % (cls.channel, cls.name))
        plugin_cfg = config['plugins'].getboolean(cls.name, fallback=False)
        if not plugin_cfg:
            continue
        logging.info('Registered %s plugin: %s' % (cls.channel, cls.name))
        plugin = cls({}, channel, loop)
        plugins.append(plugin)
    return plugins

