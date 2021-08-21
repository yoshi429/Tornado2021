from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from tornado import app, db
from tornado.models import User, Profile, Post, PostChild, Comment, Category, Tag
# from tornado.admin.routes import MyAdminIndexView, MyModelView


migrate = Migrate(app, db)

# 管理設定
# admin = Admin(app, '管理者画面', index_view=MyAdminIndexView(), base_template='admin/my_master.html')
admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Profile, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Tag, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(PostChild, db.session))
# admin.add_view(ModelView(Good, db.session))
admin.add_view(ModelView(Comment, db.session))
# admin.add_view(MyModelView(AdminUser, db.session))

if __name__ == '__main__':
    app.run(debug=True)