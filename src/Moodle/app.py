from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///spl.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    role = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Account %r>' % self.id

with app.app_context():
    account = Account(email="Admin@gmail.com", full_name="Admin", password="Admin", role="Admin")
    try:
        db.session.add(account)
        db.session.commit()
    except:
        pass

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/account/Admin")
def Admin_own():
    return render_template("Admin_account.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        account = Account.query.filter_by(email=email).first()
        if account:
            if account.password == password:
                if email == "Admin@gmail.com":
                    return redirect("/account/Admin")
                else:
                    return redirect(f"/account/{account.id}")
            else:
                return render_template("login.html", message="Неправильний пароль")
        else:
            return render_template("login.html", message="Акаунт з такою електронною адресою не існує")
    return render_template("login.html", message=False)


@app.route("/account/<int:id>")
def your_account(id):
    account = Account.query.get(id)
    return render_template("your_account.html", account=account)


@app.route("/sign_up", methods=['POST', 'GET'])
def sign_up():
    if request.method == "POST":
        email = request.form["email"]
        role = "Учень" if request.form.get("role") == "on" else "вчитиль"
        full_name = request.form["full_name"]
        password = request.form["password"]
        password2 = request.form["password2"]
        if password != password2:
            return render_template("sign_up.html", message="Введіть два однакові паролі")

        # Створення нового об'єкта Account
        account = Account(email=email, full_name=full_name, password=password, role=role)

        try:
            # Додавання об'єкта до сесії
            db.session.add(account)
            # Збереження змін до бази даних
            db.session.commit()
            return redirect(f"/account/{account.id}")

        except IntegrityError:
            # Обробка випадку, коли обліковий запис з такою електронною адресою вже існує
            return render_template("sign_up.html", message="Цей обліковий запис вже існує")

    else:
        return render_template("sign_up.html")


if __name__ == "__main__":
    app.run(debug=True)