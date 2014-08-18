from flask import Flask, render_template, g
from flask_bootstrap import Bootstrap
from hhub.config import get_default_cfg
from hhub.registry import discover_plugins

cfg = get_default_cfg()

app = Flask(__name__)
app.debug = cfg.get('debug', False)
Bootstrap(app)

plugins = discover_plugins(cfg)
for registry, cls in plugins:
    if getattr(cls, 'admin', None):
        app.register_blueprint(cls.admin, url_prefix='/%s' % cls.plugin_id)

@app.route('/')
def index():
    g.plugins = []
    for registry, cls in discover_plugins(cfg):
        g.plugins.append({
            'name'      : cls.plugin_id,
            'enabled'   : registry['enabled'],
            'url'       : '/' + cls.plugin_id,
        })
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
