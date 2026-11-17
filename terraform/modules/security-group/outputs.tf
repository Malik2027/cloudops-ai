output "alb_sg_id" {
  value       = aws_security_group.alb.id
  description = "Security group ID for the ALB"
}

output "ec2_sg_id" {
  value       = aws_security_group.ec2.id
  description = "Security group ID for EC2 instances"
}
