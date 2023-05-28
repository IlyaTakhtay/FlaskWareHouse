import json

from flask import Flask, render_template, session
from auth.routes import blueprint_auth
from report.routes import blueprint_report
from order.routes import blueprint_order
from queries.routes import blueprint_queries
from access import login_required

app = Flask(__name__)
app.secret_key = 'SuperKey'

app.register_blueprint(blueprint_auth, url_prefix='/auth')
app.register_blueprint(blueprint_queries, url_prefix='/queries')
app.register_blueprint(blueprint_order, url_prefix='/order')
app.register_blueprint(blueprint_report, url_prefix='/report')

app.config['db_config'] = json.load(open('configs/dbconfig.json'))
app.config['access_config'] = json.load(open('configs/access.json'))


@app.route('/')
@login_required
def menu_choice():
    if session.get('user_group', None) == 'loader':
        return render_template('loader_menu.html')
    elif session.get('user_group', None) == 'manager':
        return render_template('manager_menu.html')
    elif session.get('user_group', None) == 'director':
        return render_template('director_menu.html')
    else:
        return render_template('external_user_menu.html')


@app.route('/exit')
@login_required
def exit_func():
    session.clear()
    return render_template('exit.html')


app.debug = True

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
