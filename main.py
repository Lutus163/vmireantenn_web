from flask import Flask, render_template, request, redirect, session, jsonify, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash #хеширование пароля
#from ngrok_script import ngrok_script_output
from werkzeug.utils import secure_filename
#emzl uelf xkla hnvq pass

import uuid
from yookassa import Configuration, Payment
from datetime import datetime

import os.path as op
import os

import hmac
import hashlib

import jwt
from time import time
from send_email import send_email




Configuration.account_id = '370092'
Configuration.secret_key = 'test_z-eLiG9HezOmeea744_7d734tqfrp3SBjwnyCGIID0Q'

app = Flask(__name__) #создаем веб приложение
app.config['TELEGRAM_BOT_TOKEN'] = '6779027788:AAGrfHq5F11bvIfW0Gnw6uGpZ9xAr6pVI_k'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3' #инициализация базы данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #?
upload_folder = op.join('static', 'users images')
app.config['UPLOAD_PATH'] = upload_folder

db = SQLAlchemy(app) #поключаем приложение к БД
app.jinja_env.globals.update(BOTID = '6779027788') #айди бота из токена до знака ":"
app.jinja_env.globals.update(BOTNAME = 'vmireantenn_bot') #имя вашего бота с приставкой bot
app.jinja_env.globals.update(BOTDOMAIN ='https://vmireantenn.cloudpub.ru/') #домен вашего сайта
app.secret_key = '75f60d91830f2120a0270441bf56a75d0eb947ad'

from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin import Admin, expose, AdminIndexView,BaseView

def check_response(data):
    d = data.copy()
    del d['hash']
    d_list = []
    for key in sorted(d.keys()):
        if d[key] != None:
            d_list.append(key + '=' + d[key])
    data_string = bytes('\n'.join(d_list), 'utf-8')

    secret_key = hashlib.sha256(app.config['TELEGRAM_BOT_TOKEN'].encode('utf-8')).digest()
    hmac_string = hmac.new(secret_key, data_string, hashlib.sha256).hexdigest()
    if hmac_string == data['hash']:
        return True
    return False

class Item(db.Model): #создаем таблицу "товар"
    id = db.Column(db.Integer, primary_key=True) #добавляем айди с автоинкрементированием
    title = db.Column(db.String(100), nullable=False) #создаем название
    photo = db.Column(db.String(50))
    price = db.Column(db.Integer, nullable=False) #создаем цену
    isActive = db.Column(db.Boolean, default=True) #проверка на наличие

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100))
    second_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(50))
    password_hash = db.Column(db.String(256))
    photo = db.Column(db.String(50))
    status = db.Column(db.String(8), default='site')
    is_active = db.Column(db.Boolean, default=True)
    id_role = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, id_role):
        if self.id_role == int(id_role):
            return True
        return False

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Order(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    payment_status = db.Column(db.String(10), nullable=False)
    payment_url = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default = True)


class Buy(db.Model):  # создаем таблицу "товар"
    id = db.Column(db.Integer, primary_key=True)
    id_order = db.Column(db.String(50), db.ForeignKey('order.id'))
    id_item = db.Column(db.Integer, db.ForeignKey('item.id'))

with app.app_context():
    db.create_all()


@app.route('/ban')
@login_required
def ban():
    user_id = current_user.id  # Предположим, что у вас есть объект current_user, который представляет текущего пользователя
    user = User.query.get(user_id)
    if user:
        user.is_active = False
        db.session.commit()  # Предполагается, что у вас есть объект db.session для взаимодействия с базой данных
        return render_template('index.html', login_required=True)
    else:
        return render_template('error.html', message='Пользователь не найден')



login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/profile')

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first()

        if user and user.status == 'site' and user.verify_password(password):
            rm = True if request.form.get('rememberMe') else False
            login_user(user, remember=rm)
            return redirect(request.args.get('next') or '/profile')
        else:
            flash('Неверный логин или пароль!', category='alert-danger')
            return render_template('login.html')

    user_id = request.args.get("id")

    if user_id:
        first_name = request.args.get("first_name")
        last_name = request.args.get('last_name')
        username = request.args.get('username')
        photo_url = request.args.get("photo_url")
        auth_date = request.args.get('auth_date')
        hash = request.args.get('hash')

        user_tg = User.query.filter_by(login=user_id, status='tg').first()

        if user_tg:
            remember_me = True if request.form.get('rememberMe') else False
            login_user(user_tg, remember=remember_me)
        else:
            if not photo_url:  # Если photo_url пусто, установить значение по умолчанию
                photo_url = 'default.png'

            new_user_tg = User(login=user_id, first_name=first_name, second_name=last_name, photo=photo_url, status='tg', created_at=datetime.utcfromtimestamp(int(auth_date)))
            db.session.add(new_user_tg)
            db.session.commit()

            remember_me = True if request.form.get('rememberMe') else False
            login_user(new_user_tg, remember=remember_me)

        return redirect(request.args.get('next') or '/profile')

    return render_template('login.html')

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(subject ='[Shop] Cброс вашего пароля',
               recipients=user.email,
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token),
                                         email_from= 'Adgthr')


@app.route('/example') #спросить
def example_page():
    return render_template('/example.html')

@app.route('/login_error') #спросить
def log_err():
    return render_template('/login_error.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(id_user=current_user.id).all()
    for order in orders:
        if order.payment_status == 'pending':
            payment = Payment.find_one(order.id)
            order.payment_status = payment.status
            db.session.commit()
    return render_template('profile.html', data = orders, login_required = login_required)


@app.route('/profile/edit_<id>', methods=['GET', 'POST'])
@login_required
def profile_edit(id):
    if request.method == 'POST':

        if 'login' in request.form:
            login = request.form['login']
            existing_user = User.query.filter_by(login=login).first()
            if existing_user:
                # Обработка ошибки: пользователь с таким логином уже существует
                flash('Пользователь с таким логином уже существует', category='error')
            else:
                user = User.query.get(current_user.id)
                if login != '':
                    user.login = login
                    db.session.commit()
                    return redirect('/profile')
        if 'phone' in request.form:
            phone = request.form['phone']
            existing_phone = User.query.filter_by(phone=phone).first()
            if existing_phone:
                flash('Пользователь с таким телефоном уже существует', category='error')
            else:
                user = User.query.get(current_user.id)
                user.phone = phone
                db.session.commit()
                return redirect('/profile')
        if 'email' in request.form:
            email = request.form['email']
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('Пользователь с такой почтой уже существует', category='error')
            else:
                user = User.query.get(current_user.id)
                user.email = email
                db.session.commit()
                return redirect('/profile')
        if 'password' in request.form:
            user = User.query.get(current_user.id)
            password = request.form['password']
            if password != '':
                user.password = password
                db.session.commit()
                return redirect('/profile')
            else:
                flash('Поле пароль должно быть заполнено', category='error')

            # Проверка, существует ли пользователь с таким логином

            return redirect(f'/profile/edit_{current_user.id}')
        if 'file' in request.files:
            user = User.query.get(current_user.id)
            file = request.files['file']
            if file.filename != '':
                login = current_user.login
                file.filename = f'{login}.gif'
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                user.photo = file.filename
                db.session.commit()
                return redirect('/profile')
            else:
                flash('Фото должно быть  загружено', category='error')
    return render_template('profile_edit.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        file  = request.files['file']
        # Проверка, существует ли пользователь с таким логином
        if login != "" and password != "" and phone != "" and email != "":
            existing_phone = User.query.filter_by(phone=phone).first()
            existing_login = User.query.filter_by(login=login).first()
            existing_email = User.query.filter_by(email=email).first()
            if existing_phone:
                flash('Пользователь с таким номером уже существует!')
            elif existing_login:
                flash('Пользователь с таким логином уже существует!')
            elif existing_email:
                flash('Пользователь с такой почтой уже существует!')
            else:
                user = User(login=login, password=password, phone=phone, email=email)
                if file.filename != '':
                    file.filename = f'{login}.gif'
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                    user.photo = 'static/users images/'
                    user.photo += file.filename
                else:
                    user.photo = 'default.png'
                    db.session.add(user)
                    db.session.commit()
                return redirect('/login')
        else:
            flash('Все поля должны быть заполнены')
    return render_template('register.html')


@app.route('/') #создаем корневой декоратор
def index(): #функция
    items = Item.query.order_by(Item.price) #сортировка по цене
    return render_template('index.html', data = items, login_required=login_required) #запуск html страницы и динамическая передача товаров из базы данных

@app.route('/about') #декоратор для описания
def about(): #функция для запуска страницы about ?
    return render_template('about.html', login_required=login_required)

@app.route('/create', methods=['POST', 'GET']) #декоратор для создания товаров

def create():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']

        item = Item(title=title, price=price) #pf

        if title != "" and price != "": #?
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        else:
            return render_template('create.html', login_required=login_required)
    else:
        return render_template('create.html', login_required=login_required)

@app.route('/cart')
@login_required
def cart():
    if 'cart' not in session:
        session['cart'] = {}
    if 'total' not in session:
        session['total'] = 0
    total = session['total']
    return render_template('cart.html', total = total)


@app.route('/add_to_cart/<id>', methods=['POST'])
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = {}
    if 'total' not in session:
        session['total'] = 0
    item = Item.query.get(id)

    if id not in session['cart']:
        session['cart'][id] = {'title': item.title, 'price': item.price, 'amount': 1} #вложенная стр-ра
        session['total'] += item.price
    else:
        session['cart'][id]['amount'] += 1
        session['total'] += item.price

    data = {
        'response': 'OK',
    }
    return jsonify(data)


@app.route('/increase_amount/<id>', methods=['POST'])
def increase_amount(id):
    if 'cart' not in session:
        session['cart'] = {}
    if 'total' not in session:
        session['total'] = 0
    item = Item.query.get(id)

    if id not in session['cart']:
        session['cart'][id] = {'title': item.title, 'price': item.price, 'amount': 1}
        session['total'] += item.price
    else:
        session['cart'][id]['amount'] += 1
        session['total'] += item.price

    total = session['total']
    # amouint = session['cart'][id]['amount']
    # print(f'increase total: {total}')
    # print(f'increase amouint: {amouint}')

    data = {
        'response': 'OK',
    }
    return jsonify(data)


@app.route('/decrease_amount/<id>', methods=['POST'])
def decrease_amount(id):
    item = Item.query.get(id)
    if 'cart' not in session:
        session['cart'] = {}
    if 'total' not in session:
        session['total'] = 0
    item = Item.query.get(id)

    if id not in session['cart']:
        session['cart'][id] = {'title': item.title, 'price': item.price, 'amount': 0}
    else:
        if session['cart'][id]['amount'] > 0:
            session['cart'][id]['amount'] -= 1
            session['total'] -= item.price

    # total = session['total']
    # amouint = session['cart'][id]['amount']
    # print(f'increase total: {total}')
    # print(f'increase amouint: {amouint}')

    data = {
        'response': 'OK',
    }
    return jsonify(data)


@app.route('/delete_item/<id>', methods=['POST'])
def delete_item(id):
    if 'cart' not in session:
        session['cart'] = {}
    if 'total' not in session:
        session['total'] = 0
    if id in session['cart']:
        session['total'] -= session['cart'][id]['amount'] * session['cart'][id]['price']
        session['cart'].pop(id)

        data = {
            'response': 'OK',
        }
        return jsonify(data)


@app.route('/amount_items_cart')
def amount_items_cart():
    amount = len(session['cart'].keys())
    keys = list(session['cart'].keys()) #ключи (айди) из словаря корзины /values - значения
    data = {
    'amount': amount,
    'keys' : keys
    }
    return jsonify(data)

@app.route('/amount_items') #для главной страницы->кнопки для гл страницы из js файла/словарь json (ключ значение)
def amount_items():
    amount = Item.query.count()
    data = {
    'amount': amount,
    }
    return jsonify(data)

@app.route('/cart_total', methods = ['POST'])
def cart_total():
    if 'total' in session:
        data = {
        'total': session['total'],
        }
    else:
        data = {
        'total': '0',
        }
    return jsonify(data)

@app.route('/buy')
@login_required
def buy():
    total = session['total']

    if total > 0:
        id = str(uuid.uuid4())
        description = ''
        for key, value in session['cart'].items():
            description += value['title'] + ' - '+ str(value['amount']) + 'шт'+ '; '
        payment = Payment.create({
            "amount": {
                "value": str(session['total']) + ".00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://vmireantenn.cloudpub.ru/order_status"
            },
            "capture": True})

        order_date = datetime.strptime(payment.created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        order = Order(
            id=payment.id,
            id_user=current_user.id,
            price=session['total'],
            description=description,
            payment_status=payment.status,
            created_at=order_date,
            payment_url=payment.confirmation.confirmation_url)
        db.session.add(order)
        db.session.commit()
        for key in session['cart'].keys():
            buy = Buy(id_order=order.id, id_item = key)
            db.session.add(buy)
            db.session.commit()
        session['cart'] = {}
        session['total'] = 0
        return redirect(payment.confirmation.confirmation_url)
    else:
        if 'cart' in session:
            session['cart'] = {}
            session['total'] = 0
        return redirect('/cart')




@app.route('/order_status')
@login_required
def order_status():
    order = Order.query.filter_by(id_user=current_user.id).order_by(db.desc(Order.created_at)).first()
    description = order.description
    description = description.split(';')
    payment = Payment.find_one(order.id)

    order.payment_status = payment.status
    db.session.commit()
    items = Buy.query.filter_by(id_order=order.id).all()
    data = {}
    for i in range(len(items)):
        data[items[i].id_item] = description[i]
    return render_template('order_status.html', status = payment.status, data = data)

@app.route('/')
class MyHomeView(AdminIndexView): #отображение гл страницы админ панели
    @expose('/')
    def index(self):
        amount_succeeded = Order.query.filter_by(payment_status = 'succeeded').count()
        amount_pending = Order.query.filter_by(payment_status = 'pending').count()
        amount_canceled = Order.query.filter_by(payment_status = 'canceled').count()
        amount_active_items = Item.query.filter_by(isActive = True).count()
        amount_disactive_items = Item.query.filter_by(isActive = False).count()
        amount_users = User.query.count()
        data = {
            'amount_succeeded': amount_succeeded,
            'amount_pending': amount_pending,
            'amount_canceled': amount_canceled,
            'amount_active_items': amount_active_items,
            'amount_disactive_items': amount_disactive_items,
            'amount_users': amount_users
            }
        return self.render('admin/index.html', data = data)
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('1')

class MyModelView(ModelView):#проверка доступа просмотра таблиц БД
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('1')

class LogoutView(BaseView): #кнопка в шапке
    @expose('/')
    def logout(self):
        return redirect(url_for('profile'))
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('1')

#app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='Shop', template_mode='bootstrap4',index_view=MyHomeView(url='/admin_panel', name = 'Главная'))
path = op.join(op.dirname(__file__), 'static') #
admin.add_view(MyModelView(User, db.session, name='Пользователи'))
admin.add_view(MyModelView(Item, db.session, name='Товары'))
admin.add_view(MyModelView(Order, db.session, name='Заказы'))
admin.add_view(LogoutView(name='Выход'))

@app.errorhandler(403)
def forbidden(e):
    return redirect(url_for('login'))


class LogoutView(BaseView):
    @expose('/')
    def logout(self):
        return redirect(url_for('profile'))
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('1')



@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        if 'email' in request.form:
            email = request.form['email']
            user = User.query.filter_by(email = email).first()
            if user:
                send_password_reset_email(user)
        flash('Следуйте инструкциям для сброса пароля')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html')



@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if 'password' in request.form:
            password = request.form['password']
            user.password = password
            db.session.add(user)
            db.session.commit()
            flash('Ваш пароль был востановлен!')
            return redirect(url_for('login'))
    return render_template('reset_password.html')


@app.route('/api', methods=['POST'])
def api():
    data = request.json
    print(data)
    return 'OK'









if __name__ == "__main__":
    app.run(debug=True)