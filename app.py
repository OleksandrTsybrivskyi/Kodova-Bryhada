from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import math

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///spl.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), )
    email = db.Column(db.String(30), nullable=False, unique=True)
    role = db.Column(db.String(30) )
    password = db.Column(db.String(100))

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
    ss_id = db.Column(db.Integer)
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

class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_topic = db.Column(db.String(100))
    article_text = db.Column(db.String(1000))
    teacher_id = db.Column(db.Integer)

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
    account = Account.query.get(1)
    return render_template("your_account.html", account=account)

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



@app.route("/greate_subgect/page=<int:page>/<int:id>", methods=['POST', 'GET'])
def greate_subgect(id, page):
    account = Account.query.get(id)
    if account.role == "вчитиль":
        if request.method == "POST":
            subject_name = request.form["subject_name"]
            subject = Subject(subject_name=subject_name, teacher_id=id)

            try:
                db.session.add(subject)
                db.session.commit()
            except:
                return render_template("greate_subgect.html", message="error", account=account, page=page)
        try:
            subjects = Subject.query.filter_by(teacher_id=id).order_by(Subject.subject_name).all()

            page_size=4 # Задаємо кількість записів на сторінці
            # Перевіряємо, чи ми не зайшли на номер сторінки, якої немає
            pages_count = math.ceil(len(subjects) / page_size)
            if page < 1 or pages_count == 0:
                page = 1
            elif page > pages_count:
                page = pages_count
            
            # Отримуємо тільки записи зі сторінки, на якій ми знаходимося
            subjects = subjects[page_size*(page-1):page_size*page]
            return render_template("greate_subgect.html", account=account, subjects=subjects, page=page)
        except:
            return render_template("greate_subgect.html", account=account, page=page)
    elif account.role == "учень":
        if request.method == "POST":
            subject_id = request.form["subject_name"]
            try:
                subject_name = Subject.query.get(subject_id).subject_name
                ss = StudentSubject(subject_id=subject_id, user_id=id, subject_name=subject_name)
                db.session.add(ss)
                db.session.commit()
            except:
                return render_template("greate_subgect.html", message="Предмету з таким айді не існує", account=account, page=page)
        try:
            sss = StudentSubject.query.filter_by(user_id=id).all()
            page_size=4 # Задаємо кількість записів на сторінці

            # Перевіряємо, чи ми не зайшли на номер сторінки, якої немає
            pages_count = math.ceil(len(sss) / page_size)
            if page < 1 or pages_count == 0:
                page = 1
            elif page > pages_count:
                page = pages_count
            
            # Отримуємо тільки записи зі сторінки, на якій ми знаходимося
            sss = sss[page_size*(page-1):page_size*page]
            return render_template("greate_subgect.html", account=account, sss=sss, page=page)
        except:
            return render_template("greate_subgect.html", account=account, page=page)
    else:
        if request.method == "POST":
            subject_name = request.form["subject_name"]
            teacher_email = request.form["teacher_email"]

            try:
                teacher_id = Account.query.filter_by(email=teacher_email).first().id
                subject = Subject(subject_name=subject_name, teacher_id=teacher_id)
                db.session.add(subject)
                db.session.commit()
                subjects = Subject.query.all()

                page_size=4 # Задаємо кількість записів на сторінці
                # Перевіряємо, чи ми не зайшли на номер сторінки, якої немає
                pages_count = math.ceil(len(subjects) / page_size)
                if page < 1 or pages_count == 0:
                    page = 1
                elif page > pages_count:
                    page = pages_count
                
                # Отримуємо тільки записи зі сторінки, на якій ми знаходимося
                subjects = subjects[page_size*(page-1):page_size*page]
                return render_template("admin_add_subgect.html", subjects=subjects,account=account, page=page)
            except:
                return render_template("admin_add_subgect.html", message="error", page=page)
        subjects = Subject.query.all()

        page_size=4 # Задаємо кількість записів на сторінці
        # Перевіряємо, чи ми не зайшли на номер сторінки, якої немає
        pages_count = math.ceil(len(subjects) / page_size)
        if page < 1 or pages_count == 0:
            page = 1
        elif page > pages_count:
            page = pages_count
        
        # Отримуємо тільки записи зі сторінки, на якій ми знаходимося
        subjects = subjects[page_size*(page-1):page_size*page]
        return render_template("admin_add_subgect.html", account=account, subjects=subjects, page=page)

    return render_template("greate_subgect.html", account=account) # Додайте цей рядок




@app.route("/sign_up", methods=['POST', 'GET'])
def sign_up():
    if request.method == "POST":
        email = request.form["email"]
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
                db.session.rollback()
                return render_template("sign_up.html", message="Цей обліковий запис вже існує")

    else:
        return render_template("sign_up.html")

@app.route("/account/marks/<int:id>", methods=['POST', 'GET'])
def marks(id):
    account = Account.query.get(id)
    if account.role == "вчитиль":
        subjects = Subject.query.filter_by(teacher_id=id).all()
        if request.method == "POST":
            subject_name = request.form["subject_name"]
            subject = Subject.query.filter_by(subject_name=subject_name).first()
            sss = [[Account.query.get(ss.user_id).full_name, Mark.query.filter_by(ss_id=ss.id).all()] for ss in StudentSubject.query.filter_by(subject_id=subject.id).all()]
            return render_template("teacher_Marks.html", account=account, sss=sss, subjects=subjects)
        else:
            return render_template("teacher_Marks.html", account=account, subjects=subjects)
        

@app.route("/account/students_list/page=<int:page>/<int:id>", methods=['POST', 'GET'])
def students_list(id, page):
    account = Account.query.get(id)
    if request.method == "POST":
        if "Назад" in request.form:
            print(1)
        if "Вперід" in request.form:
            print(2)
    page_size=4
    try:
        students_list = Account.query.filter_by(role="учень").order_by(Account.full_name).all()

        #Перевіряємо, чи ми не зайшли на номер сторінки, якої немає
        pages_count = math.ceil(len(students_list) / page_size)
        if page < 1 or pages_count == 0:
            page = 1
        elif page > pages_count:
            page = pages_count
        
        students_list = students_list[page_size*(page-1):page_size*page]

        return render_template("students_list.html", account=account, students_list=students_list, page=page)
    except:
        return render_template("students_list.html", message="error", account=account, page=page)


@app.route("/account/teachers_list/page=<int:page>/<int:id>", methods=['POST', 'GET'])
def teachers_list(id, page):
    account = Account.query.get(id)
    if request.method == "POST":
        if "Назад" in request.form:
            print(1)
        if "Вперід" in request.form:
            print(2)
    page_size=4
    try:
        teachers_list = Account.query.filter_by(role="вчитиль").order_by(Account.full_name).all()

        #Перевіряємо, чи ми не зайшли на номер сторінки, якої немає
        pages_count = math.ceil(len(teachers_list) / page_size)
        if page < 1 or pages_count == 0:
            page = 1
        elif page > pages_count:
            page = pages_count
        
        teachers_list = teachers_list[page_size*(page-1):page_size*page]

        return render_template("teachers_list.html", account=account, teachers_list=teachers_list, page=page)
    except:
        return render_template("teachers_list.html", message="error", account=account, page=page)
    

@app.route("/account/articles_list/page=<int:page>/<int:id>", methods=['POST', 'GET'])
def articles_list(id, page):
    account = Account.query.get(id)

    # Можливість створити новину
    if account.role == "вчитиль" or account.role == "Admin":
        if request.method == "POST":
            article_topic = request.form["article_topic"]
            article_text = request.form["article_text"]
            article = Articles(article_topic=article_topic, article_text=article_text, teacher_id=id)

            try:
                db.session.add(article)
                db.session.commit()
            except:
                db.session.rollback()
                return render_template("articles_list.html", message="Помилка")

    page_size=4 # Задаємо кількість записів на сторінці
    try:
        articles_list = Articles.query.order_by(Articles.id.desc()).all()

        # Перевіряємо, чи ми не зайшли на номер сторінки, якої немає
        pages_count = math.ceil(len(articles_list) / page_size)
        if page < 1 or pages_count == 0:
            page = 1
        elif page > pages_count:
            page = pages_count
        
        # Отримуємо тільки записи зі сторінки, на якій ми знаходимося
        articles_list = articles_list[page_size*(page-1):page_size*page]

        return render_template("articles_list.html", account=account, articles_list=articles_list, page=page)
    except:
        return render_template("articles_list.html", message="error", account=account, page=page)


if __name__ == "__main__":
    app.run(debug=True)