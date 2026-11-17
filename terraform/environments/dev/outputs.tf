output "alb_dns_name" {
  value       = module.alb.alb_dns_name
  description = "DNS name of the ALB — point your domain here"
}

output "vpc_id" {
  value       = module.vpc.vpc_id
  description = "VPC ID"
}

output "instance_ids" {
  value       = [for i in range(2) : module.ec2[i].instance_id]
  description = "IDs of the EC2 instances"
}

output "instance_private_ips" {
  value       = [for i in range(2) : module.ec2[i].private_ip]
  description = "Private IPs of the EC2 instances (use for Ansible inventory)"
}

output "assets_bucket" {
  value       = module.s3.assets_bucket_id
  description = "Name of the app assets S3 bucket"
}

output "sns_alerts_arn" {
  value       = module.monitoring.sns_topic_arn
  description = "SNS topic ARN for CloudWatch alerts"
}
