import logging
from pkg_resources import iter_entry_points

def discover_plugins(cfg):
    discovered = []
    for obj in iter_entry_points(group='hhub.plugin', name=None):
        cls = obj.load()
        logging.info('Found %s plugin: %s' % (cls.channel, cls.plugin_id))
        registry = cfg['plugins'].get(cls.plugin_id, False)
        if not registry:
            registry = {'enabled' : False}
            cfg['plugins'][cls.plugin_id] = registry
            logging.info('Registered %s plugin: %s' % (cls.channel,
                cls.plugin_id))
        discovered.append((registry, cls))
    return discovered

def load_plugins(cfg, loop, channel):
    plugins = []
    for registry, cls in discover_plugins(cfg):
        if not registry['enabled']:
            continue
        logging.info('Enabling %s plugin: %s' % (cls.channel, cls.plugin_id))
        try:
            plugin = cls(cfg.get(cls.plugin_id, {}), channel, loop)
            plugins.append(plugin)
        except:
            logging.exception('Failed to create an instance of %s plugin:' % cls.plugin_id)
    return plugins
