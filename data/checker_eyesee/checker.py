#!/usr/bin/env python3

import logging
import argparse
import random
from enum import IntEnum

import grpc
import faker

from utils import ping, get_uuid
from exceptions import DataIsCorrupt, FlagNotFoundException
from proto.service_pb2_grpc import EyeSeeServiceStub
from proto.service_pb2 import (
    ServiceHealthCheckRequest,
    AddPrescriptionRequest,
    GetPrescriptionIDsRequest,
    CheckPrescriptionRequest,
)

LOG_LEVEL = logging.INFO
logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", level=LOG_LEVEL
)
logger = logging.getLogger("EyeSee Checker")

PUT_COMMAND = "put"
CHECK_COMMAND = "check"

PORT = 25910
GRPC_TIMEOUT = 2

FAKE = faker.Faker()
MAX_CHECKING_PRESCRIPTIONS = 10


class StatusCode(IntEnum):
    OK = 101
    CORRUPT = 102
    MUMBLE = 103
    DOWN = 104


def put(stub: EyeSeeServiceStub, flag_id: str, flag: str) -> StatusCode:
    response = stub.ServiceHealthCheck(ServiceHealthCheckRequest(), timeout=GRPC_TIMEOUT)
    local_logger.info('Service status: %s', response.status)
    response = stub.AddPrescription(
        AddPrescriptionRequest(
            patient_id=get_uuid(flag_id),
            patient_name=FAKE.name(),
            doctor_name=FAKE.name(),
            modifications=[flag],
            features=[flag_id],
            od_spf=random.randint(-40, 40) / 10,
            od_cyl=random.randint(0, 40) / 10,
            od_ax=random.randint(-40, 40),
            os_spf=random.randint(-40, 40) / 10,
            os_cyl=random.randint(0, 40) / 10,
            os_ax=random.randint(-40, 40),
        ),
        timeout=GRPC_TIMEOUT,
    )
    local_logger.info("Flag was successfully put with prescription id %s", response.id)
    return StatusCode.OK


def check(stub: EyeSeeServiceStub, flag_id: str, flag: str) -> StatusCode:
    response = stub.ServiceHealthCheck(ServiceHealthCheckRequest(), timeout=GRPC_TIMEOUT)
    local_logger.info('Service status: %s', response.status)
    response = stub.GetPrescriptionIDs(
        GetPrescriptionIDsRequest(patient_id=get_uuid(flag_id)),
        timeout=GRPC_TIMEOUT,
    )
    local_logger.info('Got %d prescriptions for specified patient_id', len(response.ids))
    for prescription_id in response.ids[:MAX_CHECKING_PRESCRIPTIONS]:
        response = stub.CheckPrescription(
            CheckPrescriptionRequest(id=prescription_id),
            timeout=GRPC_TIMEOUT,
        )
        if flag in response.modifications:
            local_logger.info("Flag was successfully checked")
            return StatusCode.OK
    raise FlagNotFoundException()


def handler(host: str, command, flag_id: str, flag: str):
    local_logger.info("Checker started")

    if not ping(host):
        local_logger.info("host is not answering")
        exit(StatusCode.DOWN)

    with grpc.insecure_channel(f'{host}:{PORT}') as channel:
        stub = EyeSeeServiceStub(channel)

        if command == PUT_COMMAND:
            status_code = put(stub, flag_id, flag)
            local_logger.info("put command has ended with %d status code", status_code)
            exit(status_code)

        if command == CHECK_COMMAND:
            status_code = check(stub, flag_id, flag)
            local_logger.info("check command has ended with %d status code", status_code)
            exit(status_code)

    # It's unreal to be there, but ...
    exit(StatusCode.MUMBLE)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="EyeSee Checker")
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

    except grpc.RpcError as exc:
        local_logger.error("Service returned an error: %s", exc.details())  # type: ignore
        if exc.code() == grpc.StatusCode.DEADLINE_EXCEEDED:  # type: ignore
            exit(StatusCode.MUMBLE)
        exit(StatusCode.CORRUPT)

    except FlagNotFoundException as exc:
        local_logger.error("Flag is not found! %r", exc)
        exit(StatusCode.CORRUPT)

    except DataIsCorrupt as exc:
        local_logger.error(
            "Some required data that put before is not found now! %r", exc
        )
        exit(StatusCode.CORRUPT)

    except Exception as exc:
        local_logger.error("Everything is bad :c %r", exc, exc_info=True)
        exit(StatusCode.CORRUPT)
