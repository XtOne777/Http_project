from flask import Flask
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from flask import render_template, redirect
from flask import request
from flask_login import LoginManager, login_user, logout_user
import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init('db/users.db')
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
login_manager = LoginManager()
login_manager.init_app(app)

test_data = {}
questions_index = 1
answers = []


def load_tests(num):
    global test_data, questions_index, answers
    test_data = {}
    questions_index = 1
    answers = []
    with open('tests/tests.json', 'r') as f:
        a = json.load(f)
    test_data = a[num]
    questions_index = 1


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


'''
@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")
'''


@app.route('/register', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(name=form.name.data, email=form.email.data, about=form.about.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
def log_out():
    logout_user()  # Надо сделать предупреждение
    return redirect('/login')


@app.route('/')
def main_route():
    return render_template('index.html', title='Главная страница')


@app.route('/test', methods=['GET', 'POST'])
def tests():
    global questions_index
    if request.method == 'GET':
        questions = {}
        for i in request.values.items():
            if 'a' == i[0]:
                if i[1] == '1':
                    load_tests("1")
                if i[1] == '2':
                    load_tests("2")
                if i[1] == '3':
                    load_tests("3")

        if str(questions_index) not in test_data:
            return redirect('/success')

        try:
            questions['a'] = test_data[str(questions_index)]
        except KeyError:
            return redirect('/')

        return render_template('tests.html', title='Тесты', questions=questions)

    if request.method == 'POST':
        if request.form.get('question'):
            answers.append((int(request.form.get('question')), test_data[str(questions_index)][2]))
            questions_index += 1
        return redirect('/test')


@app.route('/success')
def results():
    if answers:
        return render_template('success.html', title='На главную страницу',
                               results=f'{sum([1 for i in answers if i[0] == i[1]])} из {len(answers)}')
    else:
        return redirect('/')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
