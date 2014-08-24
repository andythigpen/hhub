from flask import Flask, render_template, g, request
from flask_bootstrap import Bootstrap
from hhub.config import get_default_cfg
from hhub.registry import discover_plugins
from hhub.client import send_event

cfg = get_default_cfg()

app = Flask(__name__)
app.debug = cfg.get('debug', False)
app.cfg = cfg
Bootstrap(app)

for registry, cls in discover_plugins(cfg):
    if getattr(cls, 'admin', None):
        app.register_blueprint(cls.admin, url_prefix='/%s' % cls.plugin_id)

@app.route('/plugins', methods=['GET', 'POST'])
def plugins():
    if request.method == 'POST':
        r = request.get_json()
        for registry, _ in discover_plugins(cfg, r['name']):
            registry['enabled'] = r['enabled']
        cfg.save()
        return '', 200
    else:
        return '', 501

@app.route('/event/<etype>', methods=['POST', 'PUT'])
def event(etype):
    data = request.get_json()
    send_event({etype : data})
    return '', 200

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
