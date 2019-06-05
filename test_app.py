import app
import math
from datetime import datetime

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
    lang, text = app.translate_text("wo bu yao")
    assert lang == 'zh'
    lang, text = app.translate_text("hello")
    assert text == ""

def test_handle():
    # msg = {}
    # msg['text'] = 'Fake message'
    # msg['from'] = {}
    # msg['chat'] = {'id' : 0}
    app.handle('Fake message', 0)

def test_handle_translate1():
    app.test_mode()
    # msg = {}
    # msg['text'] = 'dui you ne?'
    # msg['from'] = {}
    # msg['message_id'] = 0
    # msg['chat'] = {'id' : 0}
    app.handle('dui you ne?', 0,)

def test_handle_translate2():
    app.test_mode()
    # msg = {}
    # msg['text'] = '没有人 overnight 的'
    # msg['from'] = {}
    # msg['message_id'] = 0
    # msg['chat'] = {'id' : 0}
    app.handle('没有人 overnight 的',0)

def test_handle_command_lyrics():
    app.test_mode()
    # msg = {}
    # msg['text'] = '/lyrics the art of dying by gojira'
    # msg['from'] = {}
    # msg['message_id'] = 0
    # msg['chat'] = {'id' : 0}
    app.handle('/lyrics the art of dying by gojira', 0)

def test_handle_back():
    # msg = {'date' : 0}
    app.handle('',0, datetime.utcfromtimestamp(0))

def test_wiki1():
    app.test_mode()
    app.handle_command('/wiki metallica', 0)

def test_wiki2():
    app.test_mode()
    app.handle_command('/wiki battery', 0)

def test_wiki3():
    app.test_mode()
    app.handle_command('/wiki asdhajshdkhwirqwiofhaishd', 0)

def test_lyrics1():
    app.test_mode()
    app.handle_command('/lyrics backbone by gojira', 0)

def test_lyrics2():
    app.test_mode()
    app.handle_command('/lyrics Rapid Elemental Dissolve', 0)

def test_lyrics3():
    app.test_mode()
    app.handle_command('/lyrics asdwqjwodjaosjdoqjwodjaosd', 0)

def test_lyrics4():
    app.test_mode()
    app.handle_command('/lyrics asdwqjwodjaosjdoqjwodjaosd by qiwjdoijasidjoqiwjdoiajsodijqwd', 0)

def test_no_command():
    app.test_mode()
    assert app.handle_command('peanut', 0) == False
