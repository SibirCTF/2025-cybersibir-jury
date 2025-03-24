#!/usr/bin/env python3

import sys
import uuid
import socket
import random
from bs4 import BeautifulSoup
import os
import errno
import requests
import sqlite3

# the flag putting/checking into the service is successful
def service_up():
    print("[service is worked] - 101")
    exit(101)

# service is available (available tcp connection) but it's impossible to put/get the flag
def service_corrupt():
    print("[service is corrupt] - 102")
    exit(102)

# waited for a time (for example: for 5 sec), but service hasn't replied
def service_mumble():
    print("[service is mumble] - 103")
    exit(103)

# service is not available (maybe blocked port or service is down)
def service_down():
    print("[service is down] - 104")
    exit(104)

# checker is shit
def checker_is_shit():
    print("[checker is shit] - 1015")
    exit(1015)

# func to create local DB
def initialize_db():
    db = sqlite3.connect(f"{host}_MSPD.db")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS checker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT,
            flag_id TEXT,
            flag TEXT,
            username TEXT,
            password TEXT,
            sus_id INT
        )
        """
    )
    db.commit()
    db.close()

if len(sys.argv) != 5:
    print("\nUsage:\n\t" + sys.argv[0] + " <host> (put|check) <flag_id> <flag>\n")
    print("Example:\n\t" + sys.argv[0] + " \"127.0.0.1\" put \"abcdifghr\" \"c01d4567-e89b-12d3-a456-426600000010\" \n")
    print("\n")
    exit(0)

host = sys.argv[1]
port = 1015
command = sys.argv[2]
flag_id = sys.argv[3]
flag = sys.argv[4]

def put_flag():
    global host, port, flag_id, flag
    db_name = f"{host}_MSPD.db"
    url = f"http://{host}:{port}"
    username = str(uuid.uuid4())
    password = str(uuid.uuid4())
    creds = {"username":username,"password":password}
    try:
        # пытаемся достучаться до сервиса
        req = requests.get(url, timeout=2)
    except:
        service_down()
    try:
        s = requests.Session()
        req = s.post(url+"/register", creds, timeout=2)
        req = s.post(url+"/authorize", creds, timeout=2)
        gender = random.choice(["male","female"])
        with open(f"{gender}_namelist.txt", 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines if line.strip()]
            sus_name = random.choice(lines)
            gender = random.choice([gender,gender,gender,"robot"])
            if gender == "robot":
                age = str(random.randint(1, 20))
            else:
                age = str(random.randint(16, 50))
            sus_desc = gender + " " + age + " y.o."
            sus_desc = f"{gender.capitalize()} {age} y.o."
        with open("crimelist.txt", 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines if line.strip()]
            crime_desc = random.choice(lines)
        data = {
            'sus_name': sus_name,
            'sus_desc': sus_desc,
            'crime_desc': crime_desc,
            'sbertoken': flag
        }
        img_count = len([f for f in os.listdir("img") if f.endswith('.png')])
        image_path = f"img/{str(random.randint(1, img_count))}.png"
        with open(image_path, 'rb') as img:
            files = {
                'sus_img': img
            }
            response = s.post(url+"/create_sus", data=data, files=files, timeout=2)
            redirect_response = response.history[-1]
            redirect_url = redirect_response.headers['Location']
            susid = int(redirect_url.strip("/sus_browser?err=successful_upload&id="))
            if not susid:
                service_corrupt()
    except Exception as e:
        print(e)
        service_corrupt()
    try:
        db = sqlite3.connect(db_name)
        cursor = db.execute('INSERT INTO checker (host, flag_id, flag, username, password, sus_id) VALUES (?, ?, ?, ?, ?, ?)', (host, flag_id, flag, username, password, susid))
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        print(e)
        checker_is_shit()

def check_flag():
    global host, port, flag_id, flag
    url = f"http://{host}:{port}"
    db_name = db_name = f"{host}_MSPD.db"
    try:
        db = sqlite3.connect(db_name)
        cursor = db.execute('SELECT username, password, sus_id FROM checker WHERE flag=?', ([flag]))
        db_response = cursor.fetchone()
        creds = {'username':db_response[0],'password':db_response[1]}
        susid = str(db_response[2])
        cursor.close()
        db.close()
    except:
        # в этом случае все траблы на стороне чекера
        checker_is_shit()
    try:
        # пытаемся достучаться до сервиса
        req = requests.get(url, timeout=2)
    except:
        service_down()
    try:
        # логинимся как владелец и проверяем наличие флага
        s = requests.Session()
        req = s.post(url+"/authorize", creds, timeout=2)
        req = s.get(url+"/sus/"+susid, timeout=2)
        soup = BeautifulSoup(req.text, 'html.parser')
        flag_to_check = soup.find('p', id='Sbertoken').text.strip("Sbertoken: ")
        if flag != flag_to_check:
            service_corrupt()
        # логинимся как левый пользователь и делаем заявку на получение флага
        s2 = requests.Session()
        second_creds = {"username":str(uuid.uuid4()),"password":str(uuid.uuid4())}
        req = s2.post(url+"/register", second_creds, timeout=2)
        req = s2.post(url+"/authorize", second_creds, timeout=2)
        req = s2.post(url+"/create_claim", data={"ID":susid}, timeout=2)
        redirect_response = req.history[-1]
        redirect_url = redirect_response.headers['Location']
        claim_id = redirect_url.strip("/sus_browser?err=successful_accept&id=")
        # принимаем заявку
        req = s.post(url+"/accept_claim", data={"ID":claim_id}, timeout=2)
        # проверяем получен ли флаг
        req = s2.get(url+"/claim_browser", timeout=2)
        soup = BeautifulSoup(req.text, 'html.parser')
        claims = soup.find_all(class_='sus-tile')
        flags = [claim.find('p', id='Reward').text for claim in claims if claim.find('p', id='Reward')]
        if flag not in flags:
            service_corrupt()
    except Exception as e:
        print(e)
        service_corrupt()

initialize_db()
if command == "put":
    put_flag()
    check_flag()
    service_up()

if command == "check":
    check_flag()
    service_up()