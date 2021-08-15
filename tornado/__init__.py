from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('tornado.config')
db = SQLAlchemy(app)


from tornado import routes