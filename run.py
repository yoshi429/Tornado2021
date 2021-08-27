from flask_migrate import Migrate
from flask_admin import Admin
from tornado import app, db
from tornado.models import User, Profile, Post, PostChild, Comment, Category, Tag
from tornado.admin.routes import MyModelView


migrate = Migrate(app, db)

# 管理設定
# admin = Admin(app, '管理者画面', index_view=MyAdminIndexView(), base_template='admin/my_master.html')
admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Profile, db.session))
admin.add_view(MyModelView(Category, db.session))
admin.add_view(MyModelView(Tag, db.session))
admin.add_view(MyModelView(Post, db.session))
admin.add_view(MyModelView(PostChild, db.session))
admin.add_view(MyModelView(Comment, db.session))


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port='5000')