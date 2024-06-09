import pytest
import app
from bs4 import BeautifulSoup


app.app.config['TESTING'] = True
ctx = app.app.app_context()
ctx.push()


def test_home():
    response = app.app.test_client().post('/',follow_redirects=True)
    assert response.request.path == "/"


def test_Admin_own():
    response = app.app.test_client().post('/account/Admin',follow_redirects=True)
    assert response.request.path == "/account/Admin"


def test_sign_up_different_passwords():
    response = app.app.test_client().post('/sign_up', data=dict(
        email='test@gmail.com',
        role="Учень",
        full_name="Test Test",
        password='pass_1',
        password2="pass_2"
    ),follow_redirects=True)
    assert response.request.path == "/sign_up"


def test_sign_up_account_exists():
    response = app.app.test_client().post('/sign_up', data=dict(
        email='test@gmail.com',
        role="Учень",
        full_name="Test Test",
        password='pass',
        password2="pass"
    ),follow_redirects=True)
    response = app.app.test_client().post('/sign_up', data=dict(
        email='test@gmail.com',
        role="Учень",
        full_name="Test Test",
        password='pass',
        password2="pass"
    ),follow_redirects=True)
    assert response.request.path == "/sign_up"


@pytest.mark.parametrize(
    ("email", "role", "full_name", "password", "password2"),
    (
        ("test1@gmail.com", "Учень", "Мельник Андрій", "123", "123"),
        ("test2@gmail.com", "вчитиль", "Волошина Анастасія", "abcABC абвАБВ123!@№", "abcABC абвАБВ123!@№"),
        ("test3@ukr.net", "вчитиль", "Андрусяк Вадим", "pass", "pass"),
    ),
)
def test_sign_up_successful(email, role, full_name, password, password2):
    response = app.app.test_client().post('/sign_up', data=dict(
        email=email,
        role=role,
        full_name=full_name,
        password=password,
        password2=password2
    ),follow_redirects=True)
    assert "/account/" in response.request.path


def test_login_admin_account():
    response = app.app.test_client().post('/login', data=dict(
        email='Admin@gmail.com',
        password='Admin'
    ),follow_redirects=True)
    assert response.request.path == '/account/Admin'


def test_login_wrong_password():
    response = app.app.test_client().post('/login', data=dict(
        email='test1@gmail.com',
        password='wrong_password'
    ),follow_redirects=True)
    assert response.request.path == '/login'


def test_login_acount_does_not_exist():
    response = app.app.test_client().post('/login', data=dict(
        email='test123@gmail.com',
        password='123'
    ),follow_redirects=True)
    assert response.request.path == '/login'


@pytest.mark.parametrize(
    ("email", "password"),
    (
        ("test1@gmail.com", "123"),
        ("test2@gmail.com", "abcABC абвАБВ123!@№"),
        ("test3@ukr.net", "pass"),
    ),
)
def test_login_successful(email, password):
    response = app.app.test_client().post('/login', data=dict(
        email=email,
        password=password,
    ),follow_redirects=True)
    assert "/account/" in response.request.path


@pytest.mark.parametrize(
    ("id", "expected"),
    (
        ("1", "/account/1"),
        ("2", "/account/2"),
        ("3", "/account/3"),
    ),
)
def test_your_account(id, expected):
    response = app.app.test_client().post('/account/'+id, follow_redirects=True)
    assert response.request.path == expected
