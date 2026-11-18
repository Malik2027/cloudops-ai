import json
import boto3
from app.config import settings

SYSTEM_PROMPT = """You are CloudOps AI, an intelligent assistant for AWS cloud operations.
You help engineers monitor, manage, and troubleshoot AWS infrastructure for the HRMS application
running in ap-south-1 (Mumbai). Answer concisely and always recommend AWS best practices.
If asked to perform an action, describe what you would do and suggest the API endpoint to call."""


def chat(message: str, context: dict = None) -> tuple[str, int]:
    messages = []
    if context:
        messages.append({
            "role": "user",
            "content": f"Context about current infrastructure: {json.dumps(context)}"
        })
        messages.append({
            "role": "assistant",
            "content": "Understood. I have the infrastructure context. How can I help?"
        })
    messages.append({"role": "user", "content": message})

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT,
        "messages": messages,
    }

    client = boto3.client("bedrock-runtime", region_name=settings.AWS_REGION)
    resp = client.invoke_model(
        modelId=settings.BEDROCK_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body),
    )

    result = json.loads(resp["body"].read())
    reply = result["content"][0]["text"]
    tokens = result.get("usage", {}).get("output_tokens")
    return reply, tokens
