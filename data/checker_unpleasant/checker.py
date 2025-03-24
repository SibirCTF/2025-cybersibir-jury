#!/usr/bin/env python3

import logging
import os
import argparse
from enum import IntEnum
from session import *
from user import *


logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", level=logging.INFO
)
logger = logging.getLogger("UNPLEASANT Checker")

PUT_COMMAND = "put"
CHECK_COMMAND = "check"


class StatusCode(IntEnum):
    OK = 101
    CORRUPT = 102
    MUMBLE = 103
    DOWN = 104
    SHIT = 105


def put(host: str, flag_id: str, flag: str):
    user1 = generate_user(flag_id)
    ses = Session(host, user1)
    ses.register_user()
    ses.login_user()
    ses.create_abomination()
    ses.create_abomination(flag)
    ses.logout()

    return StatusCode.OK


def check(host: str, flag_id: str, flag: str):
    user1 = generate_user(flag_id)
    ses = Session(host, user1)
    ses.login_user()
    ses.check_my_abominations(flag)
    ses.logout()

    return StatusCode.OK


def handler(host: str, command, flag_id: str, flag: str):
    local_logger.info("checker started")

    if command == PUT_COMMAND:
        status_code = put(host, flag_id, flag)
        local_logger.info("put command has ended with %d status code", status_code)
        exit(status_code)

    if command == CHECK_COMMAND:
        status_code = check(host, flag_id, flag)
        local_logger.info("check command has ended with %d status code", status_code)
        exit(status_code)

    exit(StatusCode.SHIT)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="unpleasant checker")
    parser.add_argument("host")
    parser.add_argument("command", choices=(PUT_COMMAND, CHECK_COMMAND))
    parser.add_argument("flag_id")
    parser.add_argument("flag")
    args = parser.parse_args()

    local_logger = logger.getChild(args.host)

    try:
        handler(
                host=args.host,
                command=args.command,
                flag_id=args.flag_id,
                flag=args.flag,
            )

    except requests.exceptions.Timeout:
        local_logger.error("TIMEOUT TIMEOUT")
        exit(StatusCode.DOWN)

    except requests.exceptions.ConnectionError:
        local_logger.error("CONNECTION ERROR CONNECTION ERROR")
        exit(StatusCode.DOWN)

    except requests.exceptions.HTTPError as exc:
        local_logger.error("HTTP ERROR: %r", exc)
        exit(StatusCode.CORRUPT)

    except FlagProblem as exc:
        local_logger.error("FLAG PROBLEM: %r", exc)
        exit(StatusCode.CORRUPT)

    except Exception as exc:
        local_logger.error("BAD HAPPENED BAD HAPPENED: %r", exc, exc_info=True)
        exit(StatusCode.CORRUPT)
