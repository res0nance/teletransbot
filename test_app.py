import app
import math

def test_lambda():
    assert app.isascii('a') == True

def test_init():
    app.Init()

def test_confidence():
    assert math.isclose(app.get_required_confidence("derp"), 0.5)
