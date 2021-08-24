from flask_login import current_user
from flask_admin.contrib import sqla


class MyModelView(sqla.ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin