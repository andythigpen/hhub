import asyncio
import logging
import functools
import signal
import os
import json
import sys
import argparse

from .config import get_default_cfg
from .plugins import load_plugins

DEFAULT_PORT=11410

class NotificationChannel(object):
    def __init__(self):
        self._observers = {}

    def register(self, name, observer):
        if name not in self._observers:
            self._observers[name] = []
        if observer not in self._observers[name]:
            self._observers[name].append(observer)

    def unregister(self, name, observer):
        self._observers[name].remove(observer)

    def notify(self, name, sender=None, **kwargs):
        for observer in self._observers.get(name, []):
            if sender == observer:
                continue
            observer.on_event(**kwargs)

def sighandler(loop, signame):
    logging.info("got signal %s" % signame)
    loop.stop()

@asyncio.coroutine
def notify_channel(channel, name, event):
    channel.notify(name, **event)
    return True

@asyncio.coroutine
def accept_client(channel, reader, writer):
    logging.debug('accepted new connection')
    data = yield from asyncio.wait_for(reader.read(1024), timeout=10.0)
    if data is None:
        logging.warn('No data received')
        return
    elif len(data) == 1024 and not reader.at_eof():
        logging.error('JSON message too large')
        return
    events = json.loads(data.decode())
    for name, event in events.items():
        task = asyncio.Task(notify_channel(channel, name, event))
        result = yield from asyncio.wait_for(task, timeout=5.0)

@asyncio.coroutine
def connect_and_send(host, port, data):
    logging.debug("Connecting to %s %d", host, port)
    reader, writer = yield from asyncio.open_connection(host, port)
    logging.info("Connected to %s %d", host, port)
    writer.write(json.dumps(data).encode())

def client():
    parser = argparse.ArgumentParser(description='Send messages to hhub')
    parser.add_argument('-t', '--type', dest='event_type', required=True,
                        help='event type')
    parser.add_argument('-l', '--level', dest='level', default='INFO',
                        help='log level')
    parser.add_argument('data', nargs=argparse.REMAINDER, help='event data')
    args = parser.parse_args(sys.argv[1:])

    logging.basicConfig(level=getattr(logging, args.level.upper()))
    data = {}
    data[args.event_type] = {}
    try:
        for arg in args.data:
            k,v = arg.split(':')
            data[args.event_type][k] = v
    except ValueError:
        logging.error('Invalid data')
        return
    cfg = get_default_cfg()
    port = cfg.get('port', DEFAULT_PORT)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_and_send('localhost', port, data))


def daemon():
    parser = argparse.ArgumentParser(description='Send messages to hhub')
    parser.add_argument('-l', '--level', dest='level', default='INFO',
                        help='log level')
    args = parser.parse_args(sys.argv[1:])

    logging.basicConfig(level=getattr(logging, args.level.upper()))
    cfg = get_default_cfg()
    loop = asyncio.get_event_loop()

    channel = NotificationChannel()
    plugins = load_plugins(cfg, loop, channel)
    if len(plugins) == 0:
        logging.warn('No plugins registered')

    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(sighandler, loop, signame))

    port = cfg.get('port', DEFAULT_PORT)
    co = asyncio.start_server(functools.partial(accept_client, channel),
            port=port, loop=loop)
    logging.info('Listening for connections on %s', port)

    try:
        logging.info("Running event loop [pid %s]" % (os.getpid()))
        server = loop.run_until_complete(co)
        loop.run_forever()
    finally:
        loop.close()

if __name__ == "__main__":
    daemon()
