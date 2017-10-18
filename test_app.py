import app
import math

def test_lambda():
    assert app.isascii('a') == True
    assert app.isascii('る') == False

def test_init():
    app.init()

def test_confidence():
    assert math.isclose(app.get_required_confidence("derp"), 0.5)
    assert math.isclose(app.get_required_confidence("omg wtf bbq this is totally a legit sequance of words"),0.1)

def test_split_trivial():
    assert app.split_words("What the fuck")[0].strip() == "What the fuck"

def test_split_mixed():
    words = app.split_words("没有人overnight的")
    assert words[1].strip() == "没有人"
    assert words[2].strip() == "overnight"
    assert words[3].strip() == "的"
