module "vpc" {
  source                   = "./modules/vpc"
  vpc_cidr                 = "10.0.0.0/16"
  environment              = "dev"
  availability_zone_a      = "ap-south-1a"
  availability_zone_b      = "ap-south-1b"
  public_subnet_cidr       = "10.0.1.0/24"
  private_subnet_ec2_cidr  = "10.0.2.0/24"
  private_subnet_alb_cidr  = "10.0.3.0/24"
}

module "ec2" {
  source        = "./modules/ec2"
  count         = 2
  ami_id        = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  key_name      = "HRMS"
  environment   = "dev"
}
