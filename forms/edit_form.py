from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class EditForm(FlaskForm):
    name = StringField('Имя пользователя:', validators=[DataRequired()])
    password = PasswordField('Старый пароль:', validators=[DataRequired()])
    password_new = PasswordField('Новый пароль(Необязательно):')
    password_new_again = PasswordField('Повторите новый пароль(В случае создания нового пароля):')
    about = TextAreaField("Немного о себе:")
    submit = SubmitField('Подтвердить')
