import time
import webbrowser
from threading import Thread

import requests
import uncurl
from stem import Signal
from stem.control import Controller

from keyword_parse import keywords, search_engine_keyword, search_engine_domain_tld
from parse_curl import websites_with_timer, websites_without_timer, search_engines

COUNTER = 0


# signal TOR for a new connection
def renew_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="$!@#$!#!@E")
        controller.signal(Signal.NEWNYM)


# https://avilpage.com/2018/03/convert-browser-requests-to-python-requests.html
def get_tor_session():
    # renew connection after every 5 request
    global COUNTER
    COUNTER += 1
    if COUNTER == 5:
        renew_connection()
        COUNTER = 0
    #renew_connection()
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    return session


def false_request(req):
    with open('false.txt', 'r', encoding='utf-8') as f:
        false_keyword = f.readlines()
    for i in false_keyword:
        if (i in req.text) or (400 == req.status_code):
            return False
    return True


def make_request(curl_command):
    try:
        # parse request
        parsed_curl = uncurl.parse_context(curl_command)
        # print(parsed_curl.data)
        # create session for request
        session = get_tor_session()
        print("TOR IP" + session.get("http://httpbin.org/ip").text)

        # send request with Tor
        req = session.post(parsed_curl.url,
                           headers=parsed_curl.headers,
                           cookies=parsed_curl.cookies,
                           params=parsed_curl.data)
        # send request with your ip
        # req = requests.post(parsed_curl.url, headers=parsed_curl.headers, cookies=parsed_curl.cookies, params=parsed_curl.data)

        if (false_request(req)):
            webbrowser.open(req.url)

    except Exception as e:
        print(e)


def without_timer(curl_command):
    for i in range(len(keywords)):
        # look for the first keyword
        if 'KEYWORD' in curl_command:
            curl_command = curl_command.replace('KEYWORD', keywords[i])
        # change changed keyword
        else:
            curl_command = curl_command.replace(keywords[i - 1], keywords[i])
        # send request
        make_request(curl_command)
        time.sleep(0.2)


def with_timer(curl_command):
    for i in range(len(keywords)):
        # look for the first keyword
        if 'KEYWORD' in curl_command:
            curl_command = curl_command.replace('KEYWORD', keywords[i])
        # change changed keyword
        else:
            curl_command = curl_command.replace(keywords[i - 1], keywords[i])
        # send request
        make_request(curl_command)
        time.sleep(40)


def open_with_search_engine(curl_command):
    for i in range(len(search_engine_keyword)):
        # look for the first keyword
        if 'KEYWORD' in curl_command:
            curl_command = curl_command.replace('KEYWORD',
                                                search_engine_keyword[i])
        # change changed keyword
        else:
            curl_command = curl_command.replace(search_engine_keyword[i - 1],
                                                search_engine_keyword[i])
        for j in range(len(search_engine_domain_tld)):
            # send request change domain.
            if 'test.com' in curl_command:
                curl_command = curl_command.replace(
                    'test.com', search_engine_domain_tld[j])
            else:
                curl_command = curl_command.replace(
                    search_engine_domain_tld[j - 1],
                    search_engine_domain_tld[j])

            make_request(curl_command)
            time.sleep(0.2)


def multi_threading(web_list, function):
    threads = []
    for i in web_list:
        t = Thread(target=function, args=[
            i,
        ])
        t.start()
        threads.append(t)


t1 = Thread(target=multi_threading, args=[websites_with_timer, with_timer])
t2 = Thread(target=multi_threading,
            args=[websites_without_timer, without_timer])
t3 = Thread(target=multi_threading,
            args=[search_engines, open_with_search_engine])

if __name__ == '__main__':
    t1.start()
    t2.start()
    t3.start()
