from typing import Optional
from app.services.aws_client import get_client
from app.models.schemas import EC2Instance, EC2ActionResponse


def _tag_name(tags: Optional[list]) -> Optional[str]:
    if not tags:
        return None
    return next((t["Value"] for t in tags if t["Key"] == "Name"), None)


def list_instances(env_filter: Optional[str] = None) -> list[EC2Instance]:
    ec2 = get_client("ec2")
    filters = []
    if env_filter:
        filters.append({"Name": "tag:Environment", "Values": [env_filter]})

    resp = ec2.describe_instances(Filters=filters)
    instances = []
    for reservation in resp["Reservations"]:
        for i in reservation["Instances"]:
            instances.append(EC2Instance(
                instance_id=i["InstanceId"],
                name=_tag_name(i.get("Tags")),
                state=i["State"]["Name"],
                instance_type=i["InstanceType"],
                private_ip=i.get("PrivateIpAddress"),
                public_ip=i.get("PublicIpAddress"),
                launch_time=i["LaunchTime"].isoformat() if i.get("LaunchTime") else None,
            ))
    return instances


def get_instance(instance_id: str) -> Optional[EC2Instance]:
    ec2 = get_client("ec2")
    resp = ec2.describe_instances(InstanceIds=[instance_id])
    reservations = resp.get("Reservations", [])
    if not reservations:
        return None
    i = reservations[0]["Instances"][0]
    return EC2Instance(
        instance_id=i["InstanceId"],
        name=_tag_name(i.get("Tags")),
        state=i["State"]["Name"],
        instance_type=i["InstanceType"],
        private_ip=i.get("PrivateIpAddress"),
        public_ip=i.get("PublicIpAddress"),
        launch_time=i["LaunchTime"].isoformat() if i.get("LaunchTime") else None,
    )


def perform_action(instance_id: str, action: str) -> EC2ActionResponse:
    ec2 = get_client("ec2")

    current = get_instance(instance_id)
    previous_state = current.state if current else "unknown"

    if action == "start":
        resp = ec2.start_instances(InstanceIds=[instance_id])
        new_state = resp["StartingInstances"][0]["CurrentState"]["Name"]
    elif action == "stop":
        resp = ec2.stop_instances(InstanceIds=[instance_id])
        new_state = resp["StoppingInstances"][0]["CurrentState"]["Name"]
    elif action == "reboot":
        ec2.reboot_instances(InstanceIds=[instance_id])
        new_state = "rebooting"
    else:
        raise ValueError(f"Unsupported action: {action}")

    return EC2ActionResponse(
        instance_id=instance_id,
        action=action,
        previous_state=previous_state,
        current_state=new_state,
    )
