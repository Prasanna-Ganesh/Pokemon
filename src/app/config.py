class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:postgres@localhost/pokemon"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAGE_LIMIT = 20
    SECRET_KEY = "password"