from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from hhub.config import get_default_cfg

cfg = get_default_cfg()

app = Flask(__name__)
app.debug = cfg.get('debug', False)
Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
