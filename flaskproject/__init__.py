
import os

from flask import abort, Flask, g, render_template, request
from flask_security import SQLAlchemyUserDatastore, current_user

from flaskproject.utils import get_instance_folder_path
# from flaskproject.main.views import main
# from flaskproject.admin.views import admin
# from flaskproject.users.views import user
# from flaskproject.events.views import mod as eventsModule
from flaskproject.cache import cache
# from flaskproject.config import configure_app

from .core import db, mail, security
from .models import User, Role

app = Flask(__name__,
            instance_path=get_instance_folder_path(),
            instance_relative_config=True,
            template_folder='templates')


# configure_app(app)
app.config.from_object('flaskproject.settings')
app.config.from_pyfile('config.cfg', silent=True)
# app.config.from_object(settings_override)


cache.init_app(app)

db.init_app(app)
mail.init_app(app)
security.init_app(app, SQLAlchemyUserDatastore(db, User, Role))

app.jinja_env.add_extension('jinja2.ext.loopcontrols')

@app.errorhandler(404)
def page_not_found(error):
	app.logger.error('Page not found: %s', (request.path, error))
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def unhandled_exception(error):
    app.logger.error('Unhandled Exception: %s', (error))
    return render_template('500.html'), 500

@app.context_processor
def inject_user():
    return dict(user=current_user)

@app.route('/')
@cache.cached(300)
def home():
    return render_template('index.html')


from flaskproject.main.views import main
from flaskproject.admin.views import admin
from flaskproject.users.views import user
from flaskproject.events.views import mod as eventsModule
from flaskproject.entries.views import entries

app.register_blueprint(main, url_prefix='/main')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(eventsModule, url_prefix='/events')
app.register_blueprint(entries, url_prefix='/entries')
