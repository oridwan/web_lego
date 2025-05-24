"""WSGI Flask-app for browsing a database.

::

    +---------------------+
    | layout.html         |
    | +-----------------+ |    +--------------+
    | | search.html     | |    | layout.html  |
    | |     +           | |    | +---------+  |
    | | table.html ----------->| |row.html |  |
    | |                 | |    | +---------+  |
    | +-----------------+ |    +--------------+
    +---------------------+

You can launch Flask's local webserver like this::

    $ ase db abc.db -w

or this::

    $ python3 -m ase.db.app abc.db

"""

import io
import sys
from typing import Dict, Any
from flask import Flask, render_template, request, Response
from ase.db import connect
from ase.db.core import Database
from ase.formula import Formula
from ase.db.web import  Session
from ase.db.row import row2dct, AtomsRow
from ase.db.table import all_columns
from plotly_band import plot_all, get_path_table, get_pt_tables
from ase.db.config import Config
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../ase_root')))
app = Flask(__name__)
app.config.from_object(Config)
def create_key_descriptions(keys):
    """Return dictionary of key -> (name, unit, description)."""
    key_descriptions = {}
    for key in keys:
        name, unit, description = keys[key] if isinstance(keys[key], tuple) else (key, '', '')
        key_descriptions[key] = (name or key, unit, description)
    return key_descriptions
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='TPDB Error Traceback',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('./logs'):
        os.mkdir('./logs')
    file_handler = RotatingFileHandler('./logs/tpdb.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('TPDB startup')

projects = {}  # type: Dict[str, Dict[str, Any]]

@app.route('/<project_name>/search')
def search(project_name: str):
    """Search page.

    Contains input form for database query and a table result rows.
    """
    session = Session(project_name)
    project = projects[project_name]
    return render_template(project['search_template'],
                           p=project,
                           session_id=session.id)


@app.route('/update/<int:sid>/<what>/<x>/')
def update(sid: int, what: str, x: str):
    """Update table of rows inside search page.

    ``what`` must be one of:

    * query: execute query in request.args (x not used)
    * limit: set number of rows to show to x
    * toggle: toggle column x
    * sort: sort after column x
    * page: show page x
    """
    session = Session.get(sid)
    project = projects[session.project_name]
    session.update(what, x, request.args, project)
    table = session.create_table(project['database'], project['uid_key'])
    return render_template('table.html',
                           t=table,
                           p=project,
                           s=session)


@app.route('/<project_name>/materials/<uid>')
def row(project_name: str, uid: str):
    """Show details for one database row."""
    project = projects[project_name]
    uid_key = project['uid_key']
    row = project['database'].get('{uid_key}={uid}'
                                  .format(uid_key=uid_key, uid=uid))
    dct = project['row_to_dict_function'](row, project)
    dct['data']['plotly_HTML'] = plot_all(
                                         dct['data']['plotly_data']['frequencies'],
                                         dct['data']['plotly_data']['distances'],
                                         dct['data']['plotly_data']['path_connections'],
                                         dct['data']['plotly_data']['labels'],
                                         dct['data']['plotly_data']['freq_pts'],
                                         dct['data']['plotly_data']['dos'],
                                         dct['data']['plotly_data']['pts'],
                                         dct['data']['plotly_data']['lines'],
                                         dct['data']['plotly_data']['title'],
                                         )
    dct['data']['path_table'] = get_path_table(
                                               dct['data']['plotly_data']['paths'],
                                               dct['data']['plotly_data']['_labels'],
                                              )
    dct['data']['pt_tables'] = get_pt_tables(dct['data']['plotly_data']['pts'])
 
    return render_template(project['row_template'],
                           d=dct, row=row, p=project, uid=uid)


@app.route('/hidden')
def hidden():
    """Hidden page

    Temporary page used for webserver staging and testing. 
    """
    return render_template('hidden.html')


@app.route('/')
@app.route('/home')
def home():
    """Home page.

    Main home page for the database.
    """
    return render_template('home.html')


@app.route('/news')
def news():
    """News page.

    Contains news about the database.
    """
    return render_template('news.html')


@app.route('/csv/<int:sid>/')
def csv(sid: int):
    """Respond with .csv of the search table for download."""
    session = Session.get(sid)
    project = projects[session.project_name]
    #session.update('limit', 10000, request.args, project)
    table = session.create_table(project['database'], project['uid_key'], all=True)
    csv = table.write_csv(disp=False)
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=table.csv"})


@app.route('/atoms/<project_name>/<int:id>/<type>')
def atoms(project_name: str, id: int, type: str):
    """Return atomic structure as cif, xyz or json."""
    row = projects[project_name]['database'].get(id=id)
    a = row.toatoms()
    if type == 'cif':
        fd = io.BytesIO()
        a.write(fd, 'cif')
        return fd.getvalue(), 200, []

    fd = io.StringIO()
    if type == 'xyz':
        a.write(fd, 'xyz')
    elif type == 'json':
        con = connect(fd, type='json')
        con.write(row,
                  data=row.get('data', {}),
                  **row.get('key_value_pairs', {}))
    else:
        1 / 0

    headers = [('Content-Disposition',
                'attachment; filename="{project_name}-{id}.{type}"'
                .format(project_name=project_name, id=id, type=type))]
    txt = fd.getvalue()
    return txt, 200, headers


@app.route('/gui/<int:id>')
def gui(id: int):
    """Pop ud ase gui window."""
    from ase.visualize import view
    atoms = projects['default']['database'].get_atoms(id)
    view(atoms)
    return '', 204, []


@app.route('/test')
def test():
    from pyjokes import get_joke as j
    1 / 0
    return j()


@app.route('/robots.txt')
def robots():
    return ('User-agent: *\n'
            'Disallow: /\n'
            '\n'
            'User-agent: Baiduspider\n'
            'Disallow: /\n'
            '\n'
            'User-agent: SiteCheck-sitecrawl by Siteimprove.com\n'
            'Disallow: /\n',
            200)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
    

@app.route('/favicon.ico')
def favicon():
    return ''


def handle_query(args) -> str:
    """Converts request args to ase.db query string."""
    return args['query']


def row_to_dict(row: AtomsRow, project: Dict[str, Any]) -> Dict[str, Any]:
    """Convert row to dict for use in html template."""
    dct = row2dct(row, project['key_descriptions'])
    dct['formula'] = Formula(Formula(row.formula).format('abc')).format('html')
    return dct


def add_project(db: Database) -> None:
    """Add database to projects with name 'default'."""
    all_keys = set()
    for row in db.select(columns=['key_value_pairs'], include_data=False):
        all_keys.update(row._keys)
    kd = {key: (key, '', '') for key in all_keys}
    projects['default'] = {
        'name': 'default',
        'uid_key': 'mat_id',
        'key_descriptions': create_key_descriptions(kd),
        'database': db,
        'row_to_dict_function': row_to_dict,
        'handle_query_function': handle_query,
        'default_columns': all_columns[:],
        'search_template': 'search.html',
        'row_template': 'row.html'}
if __name__ == '__main__':
    from ase.db import connect
    import os

    # Load the database (make sure tp01.db exists in the same directory)
    db_path = os.path.join(os.path.dirname(__file__), 'tp01.db')
    db = connect(db_path)
    add_project(db)

    # Use Render's dynamic port environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
