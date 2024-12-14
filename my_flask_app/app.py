from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

# Модели базы данных
class User(UserMixin, db.Model):
    __tablename__ = 'user'  # Явно указано имя таблицы
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    # Добавляем параметр extend_existing=True, чтобы избежать ошибок переопределения таблицы
    __table_args__ = {'extend_existing': True}

# Загружаем пользователя для сессии
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Проверка, если пользователь - администратор
class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.username == "Daniil" and current_user.password == "Daniil"

# Добавляем админ панель с проверкой
admin.add_view(AdminView(User, db.session))

# Создание таблиц (обязательно выполните это только один раз, чтобы избежать дублирования)
with app.app_context():
    db.create_all()

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.username == "Daniil" and current_user.password == "Daniil":
        return redirect('/admin')  # Перенаправление на админ панель
    return redirect(url_for('index'))  # Если пользователь не Daniil, возвращаем на главную страницу


@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
