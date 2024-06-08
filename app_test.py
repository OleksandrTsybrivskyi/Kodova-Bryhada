import pytest
import app


app.app.config['TESTING'] = True
ctx = app.app.app_context()
ctx.push()


def test_home():
    assert app.home()

def test_Admin_own():
    assert app.Admin_own()

def test_admin_login():
    response = app.app.test_client().post('/login', data=dict(
        email='Admin@gmail.com',
        password='Admin'
    ),follow_redirects=True)
    assert response.request.path == '/account/Admin'


@pytest.mark.parametrize(
    ("email", "role", "fill_name", "password", "password2"),
    (
        ("abc@gmail.com", "password"),
    ),
)
def test_sign_up()
