output "instance_profile_name" {
  value       = aws_iam_instance_profile.ec2.name
  description = "Name of the EC2 instance profile"
}

output "instance_profile_arn" {
  value       = aws_iam_instance_profile.ec2.arn
  description = "ARN of the EC2 instance profile"
}

output "role_arn" {
  value       = aws_iam_role.ec2.arn
  description = "ARN of the EC2 IAM role"
}
