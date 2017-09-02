import telepot
import pprint
import telepot.loop
import time
from googletrans import Translator
import os
import pycountry

bot = telepot.Bot(os.environ['telegram_apikey'])
translator = Translator()
target_language = 'en'

def handle(msg):
    pprint.pprint(msg)
    if 'text' in msg:
        message = msg['text']
        r = translator.detect(message)
        pprint.pprint(r.lang)
        pprint.pprint(r.confidence)
        if r.lang != target_language and r.confidence > 0.5:
            translated = translator.translate(message,target_language)
            bot.sendMessage(msg['chat']['id'], translated.text + ' (' + pycountry.languages.get(alpha_2=r.lang[:2]).name + ')', reply_to_message_id=msg['message_id'])

pprint.pprint(bot.getMe())
telepot.loop.MessageLoop(bot,handle).run_as_thread()

while 1:
    time.sleep(10)
