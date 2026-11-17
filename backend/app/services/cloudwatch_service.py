from datetime import datetime, timezone, timedelta
from app.services.aws_client import get_client
from app.models.schemas import AlarmSummary, MetricDataPoint


def list_alarms(state: str = None) -> list[AlarmSummary]:
    cw = get_client("cloudwatch")
    kwargs = {}
    if state:
        kwargs["StateValue"] = state.upper()

    resp = cw.describe_alarms(**kwargs)
    alarms = []
    for a in resp.get("MetricAlarms", []):
        alarms.append(AlarmSummary(
            name=a["AlarmName"],
            state=a["StateValue"],
            metric=a["MetricName"],
            namespace=a["Namespace"],
            threshold=a["Threshold"],
            description=a.get("AlarmDescription"),
        ))
    return alarms


def get_ec2_cpu(instance_id: str, hours: int = 1) -> list[MetricDataPoint]:
    cw = get_client("cloudwatch")
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)

    resp = cw.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start,
        EndTime=end,
        Period=300,
        Statistics=["Average"],
        Unit="Percent",
    )
    return [
        MetricDataPoint(
            timestamp=dp["Timestamp"].isoformat(),
            value=round(dp["Average"], 2),
            unit=dp["Unit"],
        )
        for dp in sorted(resp["Datapoints"], key=lambda x: x["Timestamp"])
    ]
