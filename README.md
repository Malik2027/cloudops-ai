# CloudOps AI — AWS HRMS Infrastructure Platform

An AI-powered cloud operations platform for the HRMS application running on AWS ap-south-1 (Mumbai). Engineers manage AWS infrastructure through natural language in Microsoft Teams — no console access required.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Phase 1 — Security & Foundations](#phase-1--security--foundations)
- [Phase 2 — Terraform Infrastructure](#phase-2--terraform-infrastructure)
- [Phase 3 — Ansible Configuration](#phase-3--ansible-configuration)
- [Phase 4 — FastAPI Backend](#phase-4--fastapi-backend)
- [Phase 5 — Microsoft Teams Bot](#phase-5--microsoft-teams-bot)
- [API Reference](#api-reference)
- [Day-to-Day Operations](#day-to-day-operations)
- [Troubleshooting](#troubleshooting)

---

## Overview

| Item | Detail |
|---|---|
| **Cloud Provider** | AWS ap-south-1 (Mumbai) |
| **AWS Resources** | 45 (VPC, EC2 ×2, ALB, IAM, S3, SNS, CloudWatch alarms ×6) |
| **Backend** | FastAPI + Python 3.12 + boto3 |
| **AI Model** | Amazon Bedrock — Claude 3 Haiku |
| **IaC** | Terraform (S3 remote state backend) |
| **Config Mgmt** | Ansible (SSH via SSM Session Manager proxy) |
| **Frontend** | Microsoft Teams via Copilot Studio + Power Automate |
| **Auth** | EC2 IAM instance profile (no hardcoded AWS keys) |

---

## Architecture

```
MS Teams  ──►  Copilot Studio  ──►  Power Automate  ──►  ALB  ──►  FastAPI (EC2 ×2)
                 (NLP routing)       (HTTP flows ×3)              ├── boto3 EC2
                                                                   ├── boto3 CloudWatch
                                                                   └── Bedrock (Claude 3 Haiku)
```

**Network layout:**

```
VPC 10.0.0.0/16
├── public-subnet-1  10.0.1.0/24  (ap-south-1a)  ← ALB
├── public-subnet-2  10.0.4.0/24  (ap-south-1b)  ← ALB redundancy
├── private-subnet-1 10.0.2.0/24  (ap-south-1a)  ← EC2 web01
└── private-subnet-2 10.0.3.0/24  (ap-south-1b)  ← EC2 web02
```

EC2 instances have no public IPs. All SSH access is via AWS SSM Session Manager.

---

## Project Structure

```
cloudops-ai/
├── terraform/
│   ├── environments/
│   │   └── dev/                    # Active environment (run apply from here)
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       ├── outputs.tf
│   │       ├── backend.tf          # S3 remote state
│   │       └── terraform.tfvars
│   └── modules/
│       ├── vpc/                    # VPC, subnets, IGW, NAT, route tables
│       ├── security-group/         # ALB SG + EC2 SG
│       ├── ec2/                    # EC2 instance (count=2)
│       ├── alb/                    # Application Load Balancer
│       ├── iam/                    # EC2 role + instance profile + policies
│       ├── s3/                     # Assets bucket + ALB logs bucket
│       └── monitoring/             # CloudWatch alarms + SNS topic
├── ansible/
│   ├── site.yml                    # Main playbook
│   ├── inventory/
│   │   ├── dev.ini                 # EC2 instance IDs (update after terraform apply)
│   │   └── group_vars/
│   │       └── all/
│   │           ├── main.yml        # Non-secret vars
│   │           └── vault.yml       # ENCRYPTED — vault_api_key (gitignored)
│   └── roles/
│       ├── common/                 # fail2ban, UFW, SSH hardening
│       ├── webserver/              # nginx reverse proxy
│       └── app/                    # git clone, venv, systemd, .env
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── dependencies.py         # API key auth middleware
│   │   ├── routers/
│   │   │   ├── ai.py               # POST /api/v1/ai/chat
│   │   │   ├── ec2.py              # GET  /api/v1/ec2/instances
│   │   │   ├── cloudwatch.py       # GET  /api/v1/cloudwatch/alarms
│   │   │   ├── s3.py               # GET  /api/v1/s3/buckets
│   │   │   └── health.py           # GET  /health
│   │   └── services/
│   │       ├── bedrock_service.py  # Claude 3 Haiku via boto3
│   │       ├── ec2_service.py
│   │       ├── cloudwatch_service.py
│   │       └── s3_service.py
│   ├── requirements.txt
│   └── .env.example
├── power-automate/                 # Flow export files (optional)
├── copilot-studio/                 # Bot config notes
└── .gitignore
```

---

## Prerequisites

### Local machine

- AWS CLI v2 configured (`aws configure`)
- Terraform >= 1.5.0
- Ansible >= 2.15
- Python 3.12 (for local testing only)
- `aws-ssm-session-manager-plugin` installed (for SSM SSH proxy)

### AWS account

- IAM user with `AdministratorAccess`
- Amazon Bedrock — model access granted for **Claude 3 Haiku** in `ap-south-1`
- EC2 key pair **HRMS** created → `HRMS.pem` downloaded to `~/Pictures/HRMS.pem`
- S3 bucket `devcloudops-ai-terraform-state` created in `us-east-1` (Terraform state backend)

### Microsoft 365 (Phase 5)

- Microsoft 365 Business Standard or higher
- Power Automate Per User plan (required for Premium HTTP connector)
- Microsoft Copilot Studio license

---

## Phase 1 — Security & Foundations

### 1.1 Configure AWS CLI

```bash
aws configure
# AWS Access Key ID:     <your key>
# AWS Secret Access Key: <your secret>
# Default region:        ap-south-1
# Default output format: json
```

### 1.2 Create Terraform state bucket

```bash
aws s3 mb s3://devcloudops-ai-terraform-state --region us-east-1
aws s3api put-bucket-versioning \
  --bucket devcloudops-ai-terraform-state \
  --versioning-configuration Status=Enabled
```

### 1.3 Create EC2 key pair

In AWS Console → EC2 → Key Pairs → Create key pair:
- Name: `HRMS`
- Format: `.pem`

Download and secure it:

```bash
mv ~/Downloads/HRMS.pem ~/Pictures/HRMS.pem
chmod 400 ~/Pictures/HRMS.pem
```

### 1.4 Enable Bedrock model access

AWS Console → Amazon Bedrock → Model access → Request access:
- **Anthropic Claude 3 Haiku** in `ap-south-1`

Access is granted instantly or within a few minutes.

### 1.5 Create Ansible Vault

```bash
# Create vault password file (never commit this)
echo "your-strong-vault-password" > ~/.vault_pass
chmod 600 ~/.vault_pass

# Create the encrypted vault file
ansible-vault create ansible/inventory/group_vars/all/vault.yml \
  --vault-password-file ~/.vault_pass
```

Add this content to the vault file:

```yaml
vault_api_key: "your-api-key-here"
```

### 1.6 Configure SSM SSH proxy

Add to `~/.ssh/config`:

```
Host i-* mi-*
  ProxyCommand sh -c "aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p' --region ap-south-1"
  User ubuntu
  IdentityFile ~/Pictures/HRMS.pem
  StrictHostKeyChecking no
```

---

## Phase 2 — Terraform Infrastructure

All infrastructure is managed from `terraform/environments/dev/`.

### 2.1 Terraform modules

| Module | Resources created |
|---|---|
| `vpc` | VPC, 4 subnets, IGW, NAT gateway, route tables |
| `security-group` | ALB SG (port 80 public), EC2 SG (port 8000 from ALB only) |
| `ec2` | 2× t3.micro Ubuntu 22.04 in private subnets |
| `alb` | Application Load Balancer, target group, HTTP listener |
| `iam` | EC2 IAM role, instance profile, 6 policy attachments |
| `s3` | Assets bucket + ALB access logs bucket |
| `monitoring` | 6 CloudWatch alarms, SNS topic, email subscription |

### 2.2 IAM policies on EC2 role

| Policy | Purpose |
|---|---|
| `AmazonSSMManagedInstanceCore` | SSH via SSM (no public IP needed) |
| `CloudWatchAgentServerPolicy` | Send metrics/logs to CloudWatch |
| `AmazonS3ReadOnlyAccess` | Read from S3 assets bucket |
| `AmazonEC2FullAccess` | Describe instances for `/api/v1/ec2/instances` |
| `CloudWatchReadOnlyAccess` | Describe alarms for `/api/v1/cloudwatch/alarms` |
| `AmazonBedrockFullAccess` | Invoke Claude 3 Haiku for AI chat |

### 2.3 Apply infrastructure

```bash
cd terraform/environments/dev

# First time only
terraform init

# Preview changes
terraform plan

# Apply (creates ~45 resources, takes ~8 minutes)
terraform apply
```

After apply, note the outputs:
- `alb_dns_name` — your API base URL
- EC2 instance IDs — update `ansible/inventory/dev.ini`

### 2.4 Update Ansible inventory

After every `terraform apply`, update instance IDs in `ansible/inventory/dev.ini`:

```ini
[webservers]
web01 ansible_host=i-<new-instance-id-1>
web02 ansible_host=i-<new-instance-id-2>

[webservers:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=~/Pictures/HRMS.pem
```

### 2.5 Destroy infrastructure (saves AWS costs)

```bash
# Empty S3 buckets first (required before destroy)
aws s3 rm s3://cloudops-ai-dev-alb-logs --recursive --region ap-south-1
aws s3 rm s3://cloudops-ai-dev-assets --recursive --region ap-south-1

cd terraform/environments/dev
terraform destroy
```

---

## Phase 3 — Ansible Configuration

Ansible connects to EC2 instances via SSM Session Manager proxy (no public IPs needed).

### 3.1 Ansible roles

| Role | What it does |
|---|---|
| `common` | Updates packages, installs fail2ban, configures UFW firewall, hardens SSH |
| `webserver` | Installs nginx, deploys reverse proxy config (port 80 → 8000) |
| `app` | Clones repo, creates Python venv, installs deps, deploys `.env`, creates systemd service |

### 3.2 group_vars structure

```
ansible/inventory/group_vars/all/
├── main.yml       # non-secret: region, ports, app settings
└── vault.yml      # ENCRYPTED: vault_api_key (gitignored)
```

> **Important:** The vault file must be inside `all/` subdirectory, not at `group_vars/vault.yml`.
> Ansible only auto-loads `group_vars/all/*.yml` for all hosts. A file at `group_vars/vault.yml`
> only loads for a group literally named "vault".

### 3.3 Run the playbook

```bash
cd ansible

# Full deploy to both servers
ansible-playbook -i inventory/dev.ini site.yml \
  --vault-password-file ~/.vault_pass

# Single server
ansible-playbook -i inventory/dev.ini site.yml \
  --vault-password-file ~/.vault_pass \
  --limit web01

# Check connectivity first
ansible webservers -i inventory/dev.ini -m ping \
  --vault-password-file ~/.vault_pass
```

### 3.4 Manual nginx reload (if needed)

```bash
ansible webservers -i inventory/dev.ini \
  -m service -a "name=nginx state=reloaded" \
  --vault-password-file ~/.vault_pass
```

---

## Phase 4 — FastAPI Backend

### 4.1 Application stack

```
nginx (port 80) → uvicorn (port 8000) → FastAPI → boto3 → AWS
```

- **nginx** — reverse proxy, handles HTTP, forwards to uvicorn
- **uvicorn** — ASGI server running FastAPI app
- **boto3** — AWS SDK, authenticates via EC2 IAM instance profile (no keys in code)
- **systemd** — manages uvicorn process, auto-restarts on crash

### 4.2 Environment variables

Copy `.env.example` to `.env` and fill in:

```bash
cp backend/.env.example backend/.env
```

```env
ENV=dev
AWS_REGION=ap-south-1
API_KEY=<your-api-key>
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
# No BEDROCK_API_KEY — authentication is via EC2 IAM instance profile
```

### 4.3 Local development

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4.4 Test all endpoints

```bash
ALB="http://dev-alb-<your-id>.ap-south-1.elb.amazonaws.com"
KEY="your-api-key"

curl $ALB/health
curl -H "X-API-Key: $KEY" $ALB/api/v1/ec2/instances
curl -H "X-API-Key: $KEY" $ALB/api/v1/cloudwatch/alarms
curl -H "X-API-Key: $KEY" $ALB/api/v1/s3/buckets
curl -X POST $ALB/api/v1/ai/chat \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "How many EC2 instances are running?"}'
```

---

## Phase 5 — Microsoft Teams Bot

Three Power Automate flows bridge Copilot Studio to the FastAPI backend.

### 5.1 Power Automate flows

Create at [make.powerautomate.com](https://make.powerautomate.com):

| Flow name | Trigger | HTTP action | Output |
|---|---|---|---|
| `CloudOps-AI-Chat` | Copilot Studio (input: `userMessage`) | `POST /api/v1/ai/chat` | `aiReply` |
| `CloudOps-EC2-Status` | Copilot Studio (no inputs) | `GET /api/v1/ec2/instances` | `ec2Summary` |
| `CloudOps-Alarms` | Copilot Studio (no inputs) | `GET /api/v1/cloudwatch/alarms` | `alarmSummary` |

Each HTTP action needs these headers:

```
Content-Type: application/json        (POST only)
X-API-Key:    <your-api-key>
```

### 5.2 Copilot Studio bot

Create at [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com):

- Agent name: **CloudOps AI**
- Mode: **Classic** (not Generative)

| Topic | Trigger phrases | Calls flow |
|---|---|---|
| `Ask CloudOps AI` | ask AI, explain, why is, troubleshoot, how do I… | `CloudOps-AI-Chat` |
| `EC2 Status` | EC2 status, show instances, server status, are servers running… | `CloudOps-EC2-Status` |
| `Alarms Status` | alarms, alerts, check alarms, any issues, is anything alerting… | `CloudOps-Alarms` |

### 5.3 Publish to Teams

1. Copilot Studio → **Publish**
2. **Channels** → **Microsoft Teams** → **Turn on Teams**
3. **Open in Teams** (personal) or **Submit to admin** (org-wide)

### 5.4 Test in Teams

Send these messages to the CloudOps AI bot in Teams:

```
EC2 status           → lists running instances
check alarms         → shows all CloudWatch alarm states
ask AI               → prompts for a question → AI answers via Bedrock
```

---

## API Reference

Base URL: `http://<alb-dns-name>.ap-south-1.elb.amazonaws.com`

All endpoints except `/health` require the `X-API-Key` header.

### GET /health

No authentication required.

```json
{ "status": "healthy", "service": "cloudops-ai" }
```

### GET /api/v1/ec2/instances

Returns all EC2 instances in ap-south-1.

```bash
curl -H "X-API-Key: <key>" <base-url>/api/v1/ec2/instances
```

```json
[
  {
    "instance_id": "i-0cb0478776612b0df",
    "state": "running",
    "instance_type": "t3.micro",
    "private_ip": "10.0.2.100"
  }
]
```

### GET /api/v1/cloudwatch/alarms

Returns all CloudWatch metric alarms and their states.

```json
[
  {
    "alarm_name": "dev-ec2-cpu-high-0",
    "state": "OK",
    "metric": "CPUUtilization"
  }
]
```

### GET /api/v1/s3/buckets

Returns all S3 buckets in the account.

### POST /api/v1/ai/chat

Send a natural-language question. Answered by Claude 3 Haiku via Amazon Bedrock.

```bash
curl -X POST <base-url>/api/v1/ai/chat \
  -H "X-API-Key: <key>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Why would CPU spike on a t3.micro?"}'
```

```json
{
  "reply": "CPU spikes on a t3.micro can be caused by...",
  "tokens_used": 142
}
```

---

## Day-to-Day Operations

### Bring infrastructure back up

```bash
cd terraform/environments/dev
terraform apply

# Update instance IDs in ansible inventory
nano ansible/inventory/dev.ini

# Re-deploy application
cd ansible
ansible-playbook -i inventory/dev.ini site.yml --vault-password-file ~/.vault_pass
```

### Deploy a code change

```bash
cd ansible
ansible-playbook -i inventory/dev.ini site.yml --vault-password-file ~/.vault_pass
```

### Restart the FastAPI service on EC2s

```bash
ansible webservers -i inventory/dev.ini \
  -m service -a "name=cloudops state=restarted" \
  --vault-password-file ~/.vault_pass
```

### View application logs on EC2

```bash
# SSM session into web01
aws ssm start-session --target i-<instance-id> --region ap-south-1

# Then inside the session:
sudo journalctl -u cloudops -f
sudo tail -f /opt/cloudops/shared/logs/app.log
```

### Shut down (save costs)

```bash
# Empty S3 buckets first
aws s3 rm s3://cloudops-ai-dev-alb-logs --recursive --region ap-south-1
aws s3 rm s3://cloudops-ai-dev-assets --recursive --region ap-south-1

# Destroy all infrastructure
cd terraform/environments/dev
terraform destroy
```

---

## Troubleshooting

### Ansible: `vault_api_key is undefined`

The vault file is in the wrong location. It must be at:

```
ansible/inventory/group_vars/all/vault.yml   ✓ correct
ansible/inventory/group_vars/vault.yml        ✗ wrong — only loads for group named "vault"
```

### Ansible: `restart sshd` handler fails on Ubuntu

Ubuntu's systemd service is named `ssh`, not `sshd`. In `roles/common/handlers/main.yml`:

```yaml
- name: restart sshd
  service:
    name: ssh        # NOT sshd
    state: restarted
```

### nginx returns 404 on /health after first deploy

The nginx handler didn't fire because the playbook failed before the handler could run. Force a reload:

```bash
ansible webservers -i inventory/dev.ini \
  -m service -a "name=nginx state=reloaded" \
  --vault-password-file ~/.vault_pass
```

### EC2 endpoint returns 500

The IAM role is missing the `AmazonEC2FullAccess` policy. Check the IAM role in the AWS console and confirm all 6 policies are attached. They are defined in `terraform/modules/iam/main.tf`.

### Bedrock returns `AccessDeniedException`

Either:
1. Model access for Claude 3 Haiku has not been granted in ap-south-1 — check AWS Console → Bedrock → Model access
2. The `AmazonBedrockFullAccess` policy is not attached to the EC2 role

### SSM connection times out during Ansible run

Transient SSM connection drops are common. Re-run with `--limit` on the affected host:

```bash
ansible-playbook -i inventory/dev.ini site.yml \
  --vault-password-file ~/.vault_pass \
  --limit web01
```

### terraform destroy fails: BucketNotEmpty

Empty the S3 buckets before destroying:

```bash
aws s3 rm s3://cloudops-ai-dev-alb-logs --recursive --region ap-south-1
aws s3 rm s3://cloudops-ai-dev-assets --recursive --region ap-south-1
```

---

## Security Notes

- EC2 instances have **no public IPs** — all access via SSM Session Manager
- Bedrock auth uses **IAM instance profile** — no API keys in code or environment
- API key is stored in **Ansible Vault** (AES-256 encrypted) — never committed to git
- The vault password file `~/.vault_pass` is local only — never committed
- All EBS volumes are encrypted at rest

## Files Never Committed to Git

```
*.pem
.env
.env.*
ansible/inventory/group_vars/all/vault.yml
ansible/inventory/group_vars/vault.yml
~/.vault_pass
terraform.tfvars
*.tfstate
*.tfstate.backup
```

---

## License

Internal project — HRMS CloudOps Platform.
