#!/usr/bin/env python3

import logging
import requests
from user import *
from exceptions import FlagProblem

logger = logging.getLogger("UNPLEASANT Checker")


class Session:
    base_url = str
    port = 5000
    timeout = 2
    session = requests.Session
    current_user = User

    def __init__(self, host: str, user: User):
        self.session = requests.session()
        self.base_url = f"http://{host}:{self.port}"
        self.user = user
        r = self.session.get(f"{self.base_url}", timeout=self.timeout)
        r.raise_for_status()
        self.logger = logger.getChild(host)

    def register_user(self):
        """ nuff said """

        body = {
            "username": self.user.username,
            "password": self.user.password,
        }
        r = requests.post(f"{self.base_url}/register", data=body, timeout=self.timeout)

        class_logger = logger.getChild(self.base_url)

        # don't raise on existed user
        if r.status_code != 400:
            r.raise_for_status()
            class_logger.info("%s is registered", self.user.username)
        else:
            class_logger.info("%s is already exists", self.user.username)

    def login_user(self):
        """ nuff said """
        body = {
            "username": self.user.username,
            "password": self.user.password,
        }
        r = self.session.post(f"{self.base_url}/login", data=body, timeout=self.timeout)
        r.raise_for_status()

        if r.status_code == 400:
            r.raise_for_status()
        else:
            pass

    def create_abomination(self, flag=None):
        """ checks privacy paramether """
        a_name, a_gender, a_head, a_eye, a_body, a_arm, a_leg = generate_abomination()
        body = {
            "name": a_name,
            "gender": a_gender,
            "head": a_head,
            "eye": a_eye,
            "body": a_body,
            "arm": a_arm,
            "leg": a_leg
        }
        if flag is not None:
            body.update({"is_private": True,
                         "gender": flag})
        else:
            body.update({"gender": a_gender})

        r = self.session.post(f"{self.base_url}/create_abomination", data=body, timeout=self.timeout)
        r.raise_for_status()
        # self.logger.info(
        #     "'%s' post was published by %s",
        #     title,
        #     self.current_user.username,
        # )

    def check_abomination(self, abom_id: int, flag=None):
        """ checks private post for accessibility and FLAG if provided """
        r = self.session.get(f"{self.base_url}/api/abomination/{abom_id}", timeout=self.timeout)
        r.raise_for_status()
        # print(r.json())
        if flag is not None:  # sorry
            if flag != r.json()[1]:
                raise FlagProblem("Flag is not found in post profile")

    def check_my_abominations(self, flag):
        """ gets'n'checks created posts """
        r = self.session.get(f"{self.base_url}/api/my_abominations", timeout=self.timeout)
        r.raise_for_status()
        abom_ids = [abom[0] for abom in r.json()]  # Consider there are 2 ids: 1. public; 2. private
        self.check_abomination(abom_ids[0])
        self.check_abomination(abom_ids[1], flag)

    def logout(self):
        """logout"""
        r = self.session.get(f"{self.base_url}/logout", timeout=self.timeout)
        r.raise_for_status()

