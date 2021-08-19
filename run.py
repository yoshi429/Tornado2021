from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from tornado import app, db
from tornado.models import User, Profile, Post, PostChild, Good, Comment

migrate = Migrate(app, db)

admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Profile, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(PostChild, db.session))
admin.add_view(ModelView(Good, db.session))
admin.add_view(ModelView(Comment, db.session))

if __name__ == '__main__':
    app.run(debug=True)