import app
import math

def test_lambda():
    assert app.isascii('a') == True
    assert app.isascii('る') == False

def test_init():
    app.init()

def test_confidence():
    assert math.isclose(app.get_required_confidence("derp"), 0.525)
    assert math.isclose(app.get_required_confidence("omg wtf bbq this is totally a legit sequance of words"),0.2)

def test_split_trivial():
    assert app.split_words("What the fuck")[0].strip() == "What the fuck"

def test_split_mixed():
    words = app.split_words("没有人 overnight 的")
    assert words[0].strip() == "没有人"
    assert words[1].strip() == "overnight"
    assert words[2].strip() == "的"

def test_translate():
    app.init()
    lang, text = app.translate_text("lul")
    assert lang == 'nl'
    assert text == 'dick (Dutch : 0.93)'
    lang, text = app.translate_text("hello")
    assert text == ""

def test_handle():
    msg = {}
    msg['text'] = 'Fake message'
    msg['from'] = {}
    app.handle(msg)
