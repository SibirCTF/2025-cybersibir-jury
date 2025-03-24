from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ServiceHealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ServiceHealthCheckResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class AddPrescriptionRequest(_message.Message):
    __slots__ = ("patient_id", "patient_name", "doctor_name", "modifications", "features", "od_spf", "od_cyl", "od_ax", "os_spf", "os_cyl", "os_ax")
    PATIENT_ID_FIELD_NUMBER: _ClassVar[int]
    PATIENT_NAME_FIELD_NUMBER: _ClassVar[int]
    DOCTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    MODIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    OD_SPF_FIELD_NUMBER: _ClassVar[int]
    OD_CYL_FIELD_NUMBER: _ClassVar[int]
    OD_AX_FIELD_NUMBER: _ClassVar[int]
    OS_SPF_FIELD_NUMBER: _ClassVar[int]
    OS_CYL_FIELD_NUMBER: _ClassVar[int]
    OS_AX_FIELD_NUMBER: _ClassVar[int]
    patient_id: str
    patient_name: str
    doctor_name: str
    modifications: _containers.RepeatedScalarFieldContainer[str]
    features: _containers.RepeatedScalarFieldContainer[str]
    od_spf: float
    od_cyl: float
    od_ax: float
    os_spf: float
    os_cyl: float
    os_ax: float
    def __init__(self, patient_id: _Optional[str] = ..., patient_name: _Optional[str] = ..., doctor_name: _Optional[str] = ..., modifications: _Optional[_Iterable[str]] = ..., features: _Optional[_Iterable[str]] = ..., od_spf: _Optional[float] = ..., od_cyl: _Optional[float] = ..., od_ax: _Optional[float] = ..., os_spf: _Optional[float] = ..., os_cyl: _Optional[float] = ..., os_ax: _Optional[float] = ...) -> None: ...

class GetPrescriptionIDsRequest(_message.Message):
    __slots__ = ("patient_id",)
    PATIENT_ID_FIELD_NUMBER: _ClassVar[int]
    patient_id: str
    def __init__(self, patient_id: _Optional[str] = ...) -> None: ...

class GetPrescriptionIDsResponse(_message.Message):
    __slots__ = ("ids",)
    IDS_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, ids: _Optional[_Iterable[str]] = ...) -> None: ...

class AddPrescriptionResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class CheckPrescriptionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class CheckPrescriptionResponse(_message.Message):
    __slots__ = ("patient_id", "patient_name", "doctor_name", "modifications", "features", "od_spf", "od_cyl", "od_ax", "os_spf", "os_cyl", "os_ax")
    PATIENT_ID_FIELD_NUMBER: _ClassVar[int]
    PATIENT_NAME_FIELD_NUMBER: _ClassVar[int]
    DOCTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    MODIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    OD_SPF_FIELD_NUMBER: _ClassVar[int]
    OD_CYL_FIELD_NUMBER: _ClassVar[int]
    OD_AX_FIELD_NUMBER: _ClassVar[int]
    OS_SPF_FIELD_NUMBER: _ClassVar[int]
    OS_CYL_FIELD_NUMBER: _ClassVar[int]
    OS_AX_FIELD_NUMBER: _ClassVar[int]
    patient_id: str
    patient_name: str
    doctor_name: str
    modifications: _containers.RepeatedScalarFieldContainer[str]
    features: _containers.RepeatedScalarFieldContainer[str]
    od_spf: float
    od_cyl: float
    od_ax: float
    os_spf: float
    os_cyl: float
    os_ax: float
    def __init__(self, patient_id: _Optional[str] = ..., patient_name: _Optional[str] = ..., doctor_name: _Optional[str] = ..., modifications: _Optional[_Iterable[str]] = ..., features: _Optional[_Iterable[str]] = ..., od_spf: _Optional[float] = ..., od_cyl: _Optional[float] = ..., od_ax: _Optional[float] = ..., os_spf: _Optional[float] = ..., os_cyl: _Optional[float] = ..., os_ax: _Optional[float] = ...) -> None: ...
