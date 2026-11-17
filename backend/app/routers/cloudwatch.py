from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.dependencies import verify_api_key
from app.models.schemas import AlarmSummary, MetricDataPoint
from app.services import cloudwatch_service

router = APIRouter(prefix="/cloudwatch", tags=["CloudWatch"], dependencies=[Depends(verify_api_key)])


@router.get("/alarms", response_model=list[AlarmSummary])
def list_alarms(state: Optional[str] = Query(None, description="ALARM | OK | INSUFFICIENT_DATA")):
    return cloudwatch_service.list_alarms(state=state)


@router.get("/metrics/ec2/{instance_id}/cpu", response_model=list[MetricDataPoint])
def ec2_cpu_metrics(
    instance_id: str,
    hours: int = Query(1, ge=1, le=24, description="Lookback window in hours"),
):
    return cloudwatch_service.get_ec2_cpu(instance_id, hours=hours)
