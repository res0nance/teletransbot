import app
import math

def test_lambda():
    assert app.isascii('a') == True
    assert app.isascii('る') == False

def test_init():
    app.init()

def test_confidence():
    assert math.isclose(app.get_required_confidence("derp"), 0.5)

def test_split():
    assert app.split_words("What the fuck")[0].strip() == "What the fuck"
