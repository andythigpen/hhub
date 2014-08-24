import argparse
import logging
import asyncio
import json
import sys
import socket

from hhub.config import get_default_cfg

@asyncio.coroutine
def connect_and_send(host, port, data):
    logging.debug("Connecting to %s %d", host, port)
    try:
        reader, writer = yield from asyncio.open_connection(host, port)
        logging.info("Connected to %s %d", host, port)
        writer.write(json.dumps(data).encode())
    finally:
        writer.close()

def async_send_event(data):
    cfg = get_default_cfg()
    port = cfg.get('port')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_and_send('localhost', port, data))

def send_event(data):
    cfg = get_default_cfg()
    port = cfg.get('port')
    with socket.create_connection(('localhost', port)) as s:
        s.sendall(json.dumps(data).encode())

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
            if v.isnumeric():
                v = int(v)
            elif v in ['true','yes','y']:
                v = True
            elif v in ['false','no','n']:
                v = False
            else:
                try:
                    v = float(v)
                except ValueError:
                    pass
            data[args.event_type][k] = v
    except ValueError:
        logging.error('Invalid data')
        return
    async_send_event(data)

if __name__ == "__main__":
    client()
