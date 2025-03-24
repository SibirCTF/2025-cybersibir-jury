#!/usr/bin/env python3

import requests
import json
import random
import string
import sys
import time


def service_up():
    print("[service is worked] - 101")
    exit(101)


def service_corrupt():
    print("[service is corrupt] - 102")
    exit(102)


def service_mumble():
    print("[service is mumble] - 103")
    exit(103)


def service_down():
    print("[service is down] - 104")
    exit(104)


if len(sys.argv) != 5:
    print("\nUsage:\n\t" + sys.argv[0] + " <host> (put|check) <flag_id> <flag>\n")
    print("Example:\n\t" + sys.argv[0] + " \"127.0.0.1\" put \"abcdifghr\" \"c01d4567-e89b-12d3-a456-426600000010\" \n")
    print("\n")
    exit(0)


host = sys.argv[1]
port = 1337
command = sys.argv[2]
f_id = sys.argv[3]
flag = sys.argv[4]


class MumbleException(Exception):
    pass


class CorruptException(Exception):
    pass


class Url():
    REGISTER_URL = f'http://{host}:{port}/api/register'
    LOGIN_URL = f'http://{host}:{port}/api/login'
    LOGOUT_URL = f'http://{host}:{port}/api/logout'
    CREATE_URL = f'http://{host}:{port}/api/products/create'
    PRODUCTS_URL = f'http://{host}:{port}/api/products'
    IMAGE_URL = f'http://{host}:{port}/api/public/images'


def assert_exception(response, status):
    if response.status_code != status:
        raise MumbleException()
    elif response.status_code >= 500:
        raise CorruptException()
    

def register(user_data):
    r = requests.post(
        Url.REGISTER_URL, 
        headers={'Content-Type': 'application/json'}, 
        data=json.dumps(user_data),
        timeout=3.1)
    
    if r.status_code == 401: # user already exists
        return None
        
    assert_exception(r, 201)
    return r


def login(user_data):
    r = requests.post(
        Url.LOGIN_URL, 
        headers={'Content-Type': 'application/json'}, 
        data=json.dumps(user_data),
        timeout=3.1)
    
    assert_exception(r, 201)
    return r


def logout(jwt):
    r = requests.get(Url.LOGOUT_URL, cookies={'jwt': jwt}, timeout=3.1)
    assert_exception(r, 200)


def create(jwt, product_data):
    r = requests.post(Url.CREATE_URL, 
        headers={'Content-Type': 'application/json'}, 
        data=json.dumps(product_data),
        cookies={'jwt': jwt},
        timeout=3.1)
    
    if r.status_code == 400 and 'already exist' in r.text:
        return None
    
    assert_exception(r, 201)
    return r


def products(jwt):
    r = requests.get(Url.PRODUCTS_URL, cookies={'jwt': jwt}, timeout=3.1)
    
    assert_exception(r, 200)
    return r


def product(jwt, pid):
    r = requests.get(f'{Url.PRODUCTS_URL}/{pid}', cookies={'jwt': jwt}, timeout=3.1)
    
    assert_exception(r, 200)
    return r


def buy_product(jwt, pid):
    r = requests.put(
        f'{Url.PRODUCTS_URL}/{pid}/buy', 
        headers={"Content-Type": "application/json"}, 
        data=json.dumps({'pid': pid, 'reason': 'buy'}),
        cookies={'jwt': jwt}, timeout=3.1)
    
    assert_exception(r, 201)
    return r


def check_image(image_path):
    r = requests.get(f'{Url.IMAGE_URL}/{image_path}', timeout=3.1)
    assert_exception(r, 200)
    

def check_product_buy(jwt):
    second_jwt = get_jwt()
    content = get_random_string()
    product_data = get_new_product(
        desc=get_random_string(),
        content=content,
        price=100)
    
    create_resp = None
    while not create_resp:
        create_resp = create(second_jwt, product_data)
    
    test_product = create_resp.json()
    buy_product(jwt, test_product.get('id'))
    
    # time.sleep(.5)
    # if product(jwt, test_product.get('id')).json().get('content') != content:
    #     raise CorruptException()


def get_random_string(size=16, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_new_user():
    return {
        'username': get_random_string(),
        'password': get_random_string()
    }
    
    
def get_new_product(desc=f_id, content=flag, price=31337):
    return {
        'description': desc,
        'content': content,
        'price': price,
    }
    

def get_jwt():
    user_data = get_new_user()

    if not register(user_data):
        get_jwt()
    
    jwt = login(user_data).cookies.get('jwt')
    if not jwt:
        raise MumbleException()
    
    return jwt


def put_flag():
    try:
        jwt = get_jwt()
        product_data = get_new_product()
        
        jury_product = create(jwt, product_data)
        
        if not jury_product:
            raise MumbleException()
        
        # time.sleep(1.5)
        # if product_data.get('content') != jury_product.json().get('content'):
        #     print("Content missmatch")
        #     raise CorruptException()
        
        #check_product_buy(jwt)
        logout(jwt)
        
    except requests.exceptions.ConnectionError:
        service_down()
    except requests.exceptions.ConnectTimeout:
        service_down()
    except MumbleException:
        service_corrupt()
    except CorruptException:
        service_corrupt()
    except Exception as e:
        print(e)
        service_corrupt()


def check_flag():
    try:
        jwt = get_jwt()
        
        product_list = products(jwt).json()
        jury_product = [product for product in product_list if product.get('description') == f_id]
        
        if len(jury_product) > 1:
            raise MumbleException()
        elif len(jury_product) == 0:
            raise CorruptException()
        elif not jury_product[0].get('content'):
            raise CorruptException()
        
        check_image(jury_product[0].get('image_path'))
        logout(jwt)
        
    except requests.exceptions.ConnectionError:
        service_down()
    except requests.exceptions.ConnectTimeout:
        service_down()
    except MumbleException:
        service_mumble()
    except CorruptException:
        service_corrupt()
    except Exception:
        service_corrupt()


if command == "put":
    put_flag()
    check_flag()
    service_up()

if command == "check":
    check_flag()
    service_up()
