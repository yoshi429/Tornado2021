from flask import url_for, redirect, request
import flask_admin as admin
from flask_login import current_user, login_user, logout_user
from flask_admin.contrib import sqla
from flask_admin import helpers, expose

from tornado import login_manager, db, bcrypt
from tornado.models import AdminUser
from tornado.admin.forms import LoginForm, RegistrationForm


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(AdminUser).get(user_id)


class MyModelView(sqla.ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


class MyAdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = '<p>アカウント未作成用 <a href="' + url_for('.register_view') + '">ここをクリック</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = AdminUser()

            form.populate_obj(user)
            user.password = bcrypt.generate_password_hash(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('.index'))
        link = '<p>既にアカウントを持っている場合は <a href="' + url_for('.login_view') + '">ここをクリックしてログイン</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))