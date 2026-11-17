output "vpc_id" {
  value       = aws_vpc.main.id
  description = "The ID of the VPC"
}

output "public_subnet_id" {
  value       = aws_subnet.public_1.id
  description = "The ID of the public subnet"
}

output "private_subnet_ids" {
  value       = [aws_subnet.private_1.id, aws_subnet.private_2.id]
  description = "List of IDs for the private subnets"
}

output "public_subnet_2_id" {
  value       = aws_subnet.public_2.id
  description = "The ID of the second public subnet (AZ-b)"
}

output "security_group_id" {
  value       = aws_security_group.nsg.id
  description = "The ID of the security group (NSG)"
}