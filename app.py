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

    def __repr__(self):
        return '<Account %r>' % self.id

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Subject %r>' % self.id

class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    SS_id = db.Column(db.Integer)
    value = db.Column(db.Integer)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Mark %r>' % self.id

class StudentSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    subject_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<StudentSubject %r>' % self.id

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


@app.route("/account/<int:id>",methods=['POST', 'GET'])
def your_account(id):
    account = Account.query.get(id)
    return render_template("your_account.html", account=account)

@app.route("/greate_subgect/<int:id>", methods=['POST', 'GET'])
def greate_subgect(id):
    account = Account.query.get(id)
    print(account.role)
    if account.role == "вчитиль":
        if request.method == "POST":
            subject_name = request.form["subject_name"]
            subject = Subject(subject_name=subject_name, teacher_id=id)

            try:
                db.session.add(subject)
                db.session.commit()
            except:
                return render_template("greate_subgect.html", message="error", account=account)
        try:
            subjects = Subject.query.filter_by(teacher_id=id).order_by(Subject.subject_name).all()
            return render_template("greate_subgect.html", account=account, subjects=subjects)
        except:
            return render_template("greate_subgect.html", account=account)
    elif account.role == "учень":
        if request.method == "POST":

            subject_id = request.form["subject_name"]
            subject_name = Subject.query.get(subject_id).subject_name
            ss = StudentSubject(subject_id=subject_id, user_id=id, subject_name=subject_name)
            db.session.add(ss)
            db.session.commit()
            sss = StudentSubject.query.filter_by(user_id=id).all()
            return render_template("greate_subgect.html", account=account, sss=sss)

    return render_template("greate_subgect.html", account=account) # Додайте цей рядок




@app.route("/sign_up", methods=['POST', 'GET'])
def sign_up():
    if request.method == "POST":
        email = request.form["email"]
        print(request.form.get("role"))
        role = "учень" if request.form.get("role") == "student" else "вчитиль"
        full_name = request.form["full_name"]
        password = request.form["password"]
        password2 = request.form["password2"]
        if password != password2:
            return render_template("sign_up.html", message="Введіть два однакові паролі")

        # Створення нового об'єкта Account
        with app.app_context():
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