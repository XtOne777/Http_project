from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, NumberRange


class CreateForm(FlaskForm):
    question = StringField('Вопрос:', validators=[DataRequired()])
    answers_1, answers_2, answers_3, answers_4 = (StringField('Ответ 1:', validators=[DataRequired()]),
                                                  StringField('Ответ 2:', validators=[DataRequired()]),
                                                  StringField('Ответ 3:', validators=[DataRequired()]),
                                                  StringField('Ответ 4:', validators=[DataRequired()]))
    true_answer = IntegerField('Правильный ответ:', validators=[DataRequired(), NumberRange(min=1, max=4)])
