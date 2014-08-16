import argparse
import logging
import asyncio
import json
import sys

from .config import get_default_cfg

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
    port = cfg.getint('port')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_and_send('localhost', port, data))

if __name__ == "__main__":
    client()
