import json
import ssl
import urllib.request
import urllib.parse
from multiprocessing import Process
# from multiprocessing import Queue
from time import sleep
import time
from datetime import datetime

from AIDA_Bot import cycle, query_result, welcome

bot_id = 'yourBotID'
owner_chat_id = 'Your_Chat_ID'


def bot_check():
    i = 0
    base_url = 'https://api.telegram.org/' + bot_id + '/sendMessage?chat_id=' + owner_chat_id + '&text='
    while True:

        try:
            x = urllib.request.urlopen('http://aidabot.ddns.net/')
            y = urllib.request.urlopen('https://aidabot.ddns.net/', context=ssl.SSLContext())
            r = x.read()
            r1 = y.read()
            if 'A Conversational Agent to Explore Scholarly Knowledge Graphs' not in str(r):
                print('Error! Http server down!', datetime.now())
                msg_url = base_url + 'http_error'
                z = urllib.request.urlopen(msg_url, context=ssl.SSLContext())
            elif i % 10 == 0:
                print('Http Ok', datetime.now())
                msg_url = base_url + 'http_ok'
                z = urllib.request.urlopen(msg_url, context=ssl.SSLContext())
            if 'A Conversational Agent to Explore Scholarly Knowledge Graphs' not in str(r1):
                print('Error! Https server down!', datetime.now())
                msg_url = base_url + 'https_error'
                z = urllib.request.urlopen(msg_url, context=ssl.SSLContext())
            elif i % 10 == 0:
                print('Https Ok', datetime.now())
                msg_url = base_url + 'https_ok'
                z = urllib.request.urlopen(msg_url, context=ssl.SSLContext())
            time.sleep(360)
            i += 1

        except:
            print("An exception occurred")
            msg_url = base_url + 'Exception_error'
            z = urllib.request.urlopen(msg_url, context=ssl.SSLContext())
            time.sleep(60)


def get_updates(update_id):
    try:
        url = 'https://api.telegram.org/' + bot_id + '/getUpdates'
        offset = '?offset='

        if update_id is not None:
            url2 = offset + str(update_id + 1)
        else:
            url2 = ''
        r = urllib.request.urlopen(url + url2, context=ssl.SSLContext()).read()
        update = json.loads(r)
        if len(update['result']) > 0:
            update_id = update['result'][len(update['result']) - 1].get('update_id')
            return [update['result'], update_id]
        return None
    except:
        print("An exception occurred")
        url3 = 'https://api.telegram.org/' + bot_id + '/sendMessage?chat_id=' + chat_id + '?text=Exception_error'
        z = urllib.request.urlopen(url3, context=ssl.SSLContext())
        return None


if __name__ == '__main__':
    p = Process(target=bot_check, args=())
    p.start()
    upd_id = None
    while True:
        try:
            res = get_updates(upd_id)
            if res is not None:
                msg_list, upd_id = res
                for msg in msg_list:
                    text = msg['message'].get('text')
                    if text is None:
                        text = ''
                    elif text[0] == '/':
                        welcome()
                    else:
                        cycle(text)

                    chat_id = msg['message']['chat'].get('id')
                    # print(msg)
                    print(text, chat_id)
                    answer = query_result.get('answer')
                    url_answer = 'https://api.telegram.org/' + bot_id + '/sendMessage'
                    url_answer += '?chat_id=' + str(chat_id) + '&text=' + urllib.parse.quote(str(answer))
                    url_answer += '&parse_mode=html'
                    z = urllib.request.urlopen(url_answer, context=ssl.SSLContext())
            sleep(2)
        except:
            print('Error in main')
