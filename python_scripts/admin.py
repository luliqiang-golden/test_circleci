import flask_login as login
from flask import Blueprint
from flask import json, g, session, flash, request, redirect, url_for, render_template
from flask_admin import Admin, expose, BaseView, helpers
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.form import AdminModelConverter
from flask_admin.model import typefmt
from flask_admin.model.form import converts
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from sqlalchemy import DateTime, func
from werkzeug.security import check_password_hash
from wtforms import StringField, PasswordField
from wtforms.fields import TextAreaField
from wtforms.validators import InputRequired, Length, ValidationError

from api_encoder import CustomJSONEncoder
from app import app
from app import db
from models.activity import Activity
from models.admin_users import AdminUser
from models.inventory import Inventory
from models.signature import Signature

Bootstrap(app)


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(AdminUser).get(user_id)


init_login()


class DictToJSONField(TextAreaField):
    def process_data(self, value):
        if value is None:
            value = {}

        self.data = json.dumps(value, cls=CustomJSONEncoder)

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = json.loads(valuelist[0])
        else:
            self.data = '{}'


class CustomAdminConverter(AdminModelConverter):
    @converts('JSONB')
    def conv_JSONB(self, field_args, **extra):
        return DictToJSONField(**field_args)


def json_format(view, values):
    return json.dumps(values, cls=CustomJSONEncoder)


JSONB_FORMATTERS = typefmt.BASE_FORMATTERS.copy()
JSONB_FORMATTERS.update({
    dict: json_format
})


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

    def get_user(self):
        return db.session.query(AdminUser).filter_by(username=self.username.data).first()

    def validate_username(self, _):
        user = self.get_user()
        if user is None:
            raise ValidationError('Invalid user')

        if not check_password_hash(user.password, self.password.data):
            raise ValidationError('Invalid password')


class DataModelView(ModelView):
    column_display_pk = True
    column_type_formatters = JSONB_FORMATTERS
    model_form_converter = CustomAdminConverter
    action_disallowed_list = ['delete']
    column_searchable_list = ['id']
    page_size = 200
    can_export = True

    def is_accessible(self):
        return login.current_user.is_authenticated


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('admin.login'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login(self):
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


def config_admin(app, db):
    admin = Admin(app,
                  name='Seed admin',
                  template_mode='bootstrap4',
                  index_view=MyAdminIndexView(template='index.html',
                                              url='/admin'))

    app.secret_key = "05HB0wyX0S834cAnwmNoxfs9iwLagOgP"
    admin.add_view(DataModelView(Activity, db.session))
    admin.add_view(DataModelView(Inventory, db.session))
    admin.add_view(DataModelView(Signature, db.session))
