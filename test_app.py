import app

def test_lambda():
    assert app.isascii('a') == True

def test_init():
    app.Init()
