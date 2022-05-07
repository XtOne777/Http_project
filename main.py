# Flask
from flask import Flask
from flask import render_template, redirect
from flask import request
# База данных и формы
from data import db_session
from data.users import User
from forms.task import CreateForm
# Формы регистрации и входа
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required
# Стандартные библиотеки
import datetime
import json
# Импортирование библиотек

# Инициализация сайта
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
# База данных и куки данных
db_session.global_init('db/users.db')
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
login_manager = LoginManager()
login_manager.init_app(app)

# Важные значения
test_data = {}  # Вопросники
questions = {}  # Точные вопросы
questions_index = 1  # Индекс вопросов
answers = []  # Ответы
user_name = ''  # Имя пользователя
user_id = None  # Айди пользователя


# Загрузка вопрос из test.json
def load_tests(num):
    global test_data, questions_index, answers
    test_data = {}
    questions_index = 1
    answers = []
    with open('tests/tests.json', 'r') as f:
        a = json.load(f)
    if num in a:
        # Загрузка определённого теста
        test_data = a[num]
        questions_index = 1
    else:
        pass


# Создание заданий
@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    form = [CreateForm() for _ in range(20)]
    if request.method == 'POST':
        gg = {}  # Формы для вопросов
        num = 1  # Номер вопроса
        for i in form:
            # Передача данных из строк
            gg[str(num)] = [[i.answers_1.data,
                             i.answers_2.data,
                             i.answers_3.data,
                             i.answers_4.data],
                            i.question.data,
                            i.true_answer.data]
            num += 1
        # Взятие данных из json вопросов
        with open('tests/tests.json', 'r') as f:
            a = json.load(f)
        # Перезапись с новыми значениями
        with open('tests/tests.json', 'w') as f:
            a[f"{len(a) + 1}"] = gg
            print(a)
            json.dump(a, f)
    # Проверка на наличие админа
    if db_session.create_session().query(User).get(user_id).admin:
        return render_template('create_tasks.html', form=form, title='Создание заданий')
    return redirect('/')


# Автоподключение к аккаунту
@login_manager.user_loader
def load_user(user_id_got):
    db_sess = db_session.create_session()
    # Проверка на подключение
    global user_name, user_id
    if db_sess.query(User).filter(User.id == user_id_got).all():
        user_name, user_id = \
            db_sess.query(User).get(user_id_got).name,\
            db_sess.query(User).get(user_id_got).id
    # Возрат аккаунта подключения
    return db_sess.query(User).get(user_id_got)


# Профиль
@app.route('/profile')
@login_required
def profile():
    global user_name, user_id
    is_admin = db_session.create_session().query(User).get(user_id).admin  # Проверка на наличие админа
    return render_template('profile.html', title='Профиль',
                           user_name=user_name, is_admin=is_admin)


# Исключение ошибок
@app.errorhandler(Exception)
def error(e):
    # Стандартная ошибка при подключение аккаунта
    # Связанна с тем что Flask сперва прогружает страничку, а затем аккаунт
    if e != "'NoneType' object has no attribute 'admin'":
        print(e)
    return redirect('/')


# Вход в аккаунт
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Создание формы
    form = LoginForm()
    # Проверка на подтверждение
    if form.validate_on_submit():
        # Подключение к бд
        db_sess = db_session.create_session()
        # Поиск почты
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        # Проверка пароля
        if user and user.check_password(form.password.data):
            # Подкючение к аккаунту
            login_user(user, remember=form.remember_me.data)
            return redirect("/")  # Перенаправление на главную страницу
        # Ошибка при неправильном логине или пароле
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    # Отправка странички с авторизацией
    return render_template('login.html',
                           title='Авторизация', form=form)


# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def registration():
    # Создание формы регистрации
    form = RegisterForm()
    # Проверка на подтверждение действий
    if form.validate_on_submit():
        # Проверка на повторный пароль
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        # Подключение к бд
        db_sess = db_session.create_session()
        # Проверка на наличие таких же почт в бд
        if db_sess.query(User).filter(User.email == form.email.data).first():
            # Возрат ошибки
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        # Создание класса пользователя
        user = User()
        # Передание значений с полей ввода
        user.name, user.email, user.about =\
            form.name.data, form.email.data, form.about.data
        # Хэширование пароля
        user.set_password(form.password.data)
        # Сохранение данных в бд
        db_sess.add(user)
        db_sess.commit()
        # Перенаправление на авторизацию
        return redirect('/login')
    # Отправка странички регистрации
    return render_template('register.html', title='Регистрация', form=form)


# Выход из аккаунта
@app.route('/logout')
def log_out():
    logout_user()
    return redirect('/login')


# Главная страница
@app.route('/')
def main_route():
    # Прогрузка тестов
    with open('tests/tests.json', 'r') as f:
        a = json.load(f)
    global user_name
    # Передача главной страницы
    return render_template('index.html', title='Главная страница',
                           count=range(1, len(a) + 1), user_name=user_name)


# Задания
@app.route('/test', methods=['GET', 'POST'])
@login_required  # Запрет для тех кто не подключён к аккаунту
def tests():
    global questions_index, questions
    # Проверка на первое подключение
    if request.method == 'GET':
        # Сохранение вопросов в переменную
        questions = {}
        for i in request.values.items():
            if 'a' == i[0]:
                load_tests(i[1])
        if str(questions_index) not in test_data:
            return redirect('/success')
        try:
            questions['a'] = test_data[str(questions_index)]
        except KeyError:
            return redirect('/')
        # Отправка страницы теста
        return render_template('tests.html', title='Тесты',
                               questions=questions)
    # Проверка на отправку формы
    if request.method == 'POST':
        # Проверка на отправку вопроса
        if request.form.get('question'):
            answers.append((int(request.form.get('question')),
                            test_data[str(questions_index)][2]))
            questions_index += 1
        # Иначе отправить ошибку о выборе варианта
        else:
            return render_template('tests.html', title='Тесты',
                                   questions=questions, message="* Выберите вариант ответа!")
        # Перенаправка обратно на страницу
        return redirect('/test')


# Результаты теста
@app.route('/success')
def results():
    # Проверка на наличие ответов
    if answers:
        k = {}
        # Подсчёт результатов
        for i in test_data:
            k[i] = [test_data[i][0][answers[int(i) - 1][0] - 1], test_data[i][0][test_data[i][2] - 1]]
        # Возрат странички с результатом и ошибками
        return render_template('success.html', title='На главную страницу',
                               results=f'{sum([1 for i in answers if i[0] == i[1]])} из {len(answers)}',
                               test_data=test_data, answer=k)
    return redirect('/')


# Запуск кода
if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
