from pydantic import BaseModel
from typing import Any, Optional


class HealthResponse(BaseModel):
    status: str
    env: str
    region: str


class EC2Instance(BaseModel):
    instance_id: str
    name: Optional[str]
    state: str
    instance_type: str
    private_ip: Optional[str]
    public_ip: Optional[str]
    launch_time: Optional[str]


class EC2ActionRequest(BaseModel):
    instance_id: str
    action: str  # start | stop | reboot


class EC2ActionResponse(BaseModel):
    instance_id: str
    action: str
    previous_state: str
    current_state: str


class S3Bucket(BaseModel):
    name: str
    creation_date: Optional[str]


class S3Object(BaseModel):
    key: str
    size: int
    last_modified: str
    storage_class: str


class AlarmSummary(BaseModel):
    name: str
    state: str
    metric: str
    namespace: str
    threshold: float
    description: Optional[str]


class MetricDataPoint(BaseModel):
    timestamp: str
    value: float
    unit: str


class ChatRequest(BaseModel):
    message: str
    context: Optional[dict[str, Any]] = None


class ChatResponse(BaseModel):
    reply: str
    tokens_used: Optional[int] = None


class ErrorResponse(BaseModel):
    detail: str
