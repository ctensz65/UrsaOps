locals {
  key_name_value = "privkey_${var.instance_name}"
  resolved_public_key_path  = var.public_key != "" ? var.public_key : "/home/${var.local_user}/.ssh/id_rsa.pub"
  resolved_private_key_path  = var.private_key_path != "" ? var.private_key_path : "/home/${var.local_user}/.ssh/id_rsa"
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}