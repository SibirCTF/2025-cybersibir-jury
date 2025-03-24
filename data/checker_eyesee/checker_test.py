import os
import logging
import random
import uuid
import string
import asyncio
from multiprocessing import Process
import subprocess


HOST = '127.0.0.1'

REQUESTS_COUNT = 2000  # Count of 'put' requests
REQUESTS_INTERVAL = 0  # Interval between two 'put' requests
CHECK_INTERVAL = 0  # Interval between 'put' and 'check' requests
LOG_LEVEL = logging.WARN

LOG_ITER_STEP = 10

SEED_SIZE = 32

FLAG_ID_LEN = 10
FLAG_ID_ALPH = string.ascii_uppercase + string.ascii_lowercase + string.digits
PUT_COMMAND = "put"
CHECK_COMMAND = "check"
PORT = 25910

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", level=LOG_LEVEL
)
logger = logging.getLogger("EyeSee Checker Tester")

_SEED = os.urandom(SEED_SIZE)
logging.info('Randomizer seed: %r', _SEED)
random.seed(_SEED)


async def put_checker(host, flag_id: str, flag: str):
    logger.info('put_checker starts with host=%r flag_id=%r flag=%r', host, flag_id, flag)

    res = subprocess.call(['./checker.py', host, 'put', flag_id, flag])
    assert res == 101, res

    await asyncio.sleep(CHECK_INTERVAL)
    asyncio.ensure_future(check_checker(host=host, flag_id=flag_id, flag=flag))


async def check_checker(host, flag_id: str, flag: str):
    logger.info('check_checker starts with host=%r flag_id=%r flag=%r', host, flag_id, flag)
    res = subprocess.call(['./checker.py', host, 'check', flag_id, flag])
    assert res == 101, res


async def handler(proc_no: int):
    for i in range(1, REQUESTS_COUNT+1):
        flag_id = ''.join(random.choices(FLAG_ID_ALPH, k=FLAG_ID_LEN))
        flag = 'c01d' + str(uuid.UUID(int=random.randint(0, (2<<127)-1)))[4:]

        asyncio.ensure_future(put_checker(HOST, flag_id, flag))
        await asyncio.sleep(REQUESTS_INTERVAL)
        if i % LOG_ITER_STEP == 0:
            logger.warning('(proc_no=%d) completed %d/%d', proc_no, i, REQUESTS_COUNT)
    await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})


def run(proc_no: int):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(handler(proc_no))


def main(proc_count=16):
    processes_list = []
    for k in range(proc_count):
        processes_list.append(Process(target=run, args=(k,)))
    for proc in processes_list:
        proc.start()
    for proc in processes_list:
        proc.join()


if __name__ == '__main__':
    main(proc_count=1)
