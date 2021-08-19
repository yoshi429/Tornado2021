from wtforms import form, fields, validators

from tornado import db, bcrypt
from tornado.models import AdminUser


class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('ユーザー名もしくはパスワードが違います。')

        if not bcrypt.check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('ユーザー名もしくはパスワードが違います。')

    def get_user(self):
        return db.session.query(AdminUser).filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if db.session.query(AdminUser).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('同じユーザー名が存在します。')