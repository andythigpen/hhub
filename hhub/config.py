import os
import json

def get_default_cfg():
    cfgfile = os.path.expanduser("~/.hhub/config.json")
    if not os.path.exists(os.path.dirname(cfgfile)):
        os.makedirs(os.path.dirname(cfgfile))
    if not os.path.exists(cfgfile):
        with open(cfgfile, 'w') as f:
            f.write(json.dumps({
                'plugins': {},
            }, indent=4))
    return Config(cfgfile)

class Config(dict):
    def __init__(self, fname):
        if not os.path.exists(fname):
            raise Exception("File does not exist: %s" % fname)
        with open(fname, 'r') as f:
            self.fname = fname
            try:
                self.update(json.load(f))
            except ValueError:
                pass

    def save(self):
        with open(self.fname, 'w') as f:
            json.dump(self, f, indent=4)

