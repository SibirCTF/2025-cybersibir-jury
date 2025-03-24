import random
import dataclasses
import hashlib
from names import Names

MAX_IMPLANTS = 8


@dataclasses.dataclass
class User:
    username: str
    password: str


def hash_int(string: str) -> int:
    return int(hashlib.sha1(string.encode("utf8")).hexdigest(), 16)


def gen_username(flag_id: str) -> str:
    return f"user{str(hash_int('username' + flag_id))[:8]}"


def generate_user(flag_id: str) -> User:
    username = str(gen_username(flag_id))
    password = str(hash_int(flag_id))
    user = User(
        username=username,
        password=password,
    )
    return user


def generate_abomination():
    abom_name = Names.names[random.randint(0, len(Names.names)-1)],
    abom_gender = Names.genders[random.randint(0, len(Names.genders)-1)],
    abom_head = random.randint(1, MAX_IMPLANTS),
    abom_eye = random.randint(1, MAX_IMPLANTS),
    abom_body = random.randint(1, MAX_IMPLANTS),
    abom_arm = random.randint(1, MAX_IMPLANTS),
    abom_leg = random.randint(1, MAX_IMPLANTS),
    return abom_name, abom_gender, abom_head, abom_eye, abom_body, abom_arm, abom_leg

