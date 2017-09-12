import telepot
import pprint
import telepot.loop
import time
from googletrans import Translator
import os
import pycountry
import re

bot = telepot.Bot(os.environ['telegram_apikey'])
translator = Translator()
target_language = 'en'
isascii = lambda s: len(s) == len(s.encode())

def handle(msg):
    pprint.pprint(msg)
    if 'text' in msg:
        message = msg['text']
        msglist = []
        currentWords = ""
        asciimode = True
        wordlist = message.split(' ')
        for word in wordlist:
            swap = False
            for t in word:
                if not isascii(t) and asciimode:
                    print(currentWord)
                    msglist.append(currentWord)
                    currentWords = word + ' '
                    asciimode = not asciimode
                    swap = True
                    break
                elif isascii and not asciimode:
                    print(currentWord)
                    msglist.append(currentWord)
                    currentWords = word + ' '
                    asciimode = not asciimode
                    swap = True
                    break
            if not swap:
                currentWords += word
        msglist.append(currentWord)
        translate = False
        translist = []
        for w in msglist:
            r = translator.detect(w)
            pprint.pprint(w)
            pprint.pprint(r.lang)
            pprint.pprint(r.confidence)
            if r.lang != target_language and r.confidence > 0.5 and translator:
                transtext = translator.translate(w,target_language).text
                if transtext != w:
                    translist.append(translator.translate(w,target_language).text + ' (' + pycountry.languages.get(alpha_2=r.lang[:2]).name + ') ')
                    translate = True
                else:
                    translist.append(w + ' ')
            else:
                translist.append(w + ' ')
        if translate:
            message = ''.join(translist)
            bot.sendMessage(msg['chat']['id'], message, reply_to_message_id=msg['message_id'])

pprint.pprint(bot.getMe())
telepot.loop.MessageLoop(bot,handle).run_as_thread()

while 1:
    time.sleep(10)
