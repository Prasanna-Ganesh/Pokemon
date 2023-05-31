from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_pyfile("config.py")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

try:
    from app import views

    app.register_blueprint(views.pokemonapi)

except Exception as e:
    import traceback

    traceback.print_exc()
    app.logger.error(e)
