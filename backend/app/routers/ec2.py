from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.dependencies import verify_api_key
from app.models.schemas import EC2Instance, EC2ActionRequest, EC2ActionResponse
from app.services import ec2_service

router = APIRouter(prefix="/ec2", tags=["EC2"], dependencies=[Depends(verify_api_key)])


@router.get("/instances", response_model=list[EC2Instance])
def list_instances(env: Optional[str] = Query(None, description="Filter by Environment tag")):
    return ec2_service.list_instances(env_filter=env)


@router.get("/instances/{instance_id}", response_model=EC2Instance)
def get_instance(instance_id: str):
    instance = ec2_service.get_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    return instance


@router.post("/instances/action", response_model=EC2ActionResponse)
def instance_action(req: EC2ActionRequest):
    if req.action not in ("start", "stop", "reboot"):
        raise HTTPException(status_code=400, detail="Action must be start, stop, or reboot")
    try:
        return ec2_service.perform_action(req.instance_id, req.action)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
