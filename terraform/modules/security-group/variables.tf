variable "vpc_id" {
  description = "VPC ID to create security groups in"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "CIDR block allowed SSH access to EC2 instances (e.g. office/VPN IP)"
  type        = string
  default     = "10.0.0.0/8"
}
