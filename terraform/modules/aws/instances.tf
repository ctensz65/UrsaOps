resource "aws_key_pair" "key" {
  key_name   = local.key_name_value
  public_key = file(local.resolved_public_key_path)
}

resource "aws_security_group" "secgroup" {
  name        = "${var.instance_name}_sg"
  description = "Allow inbound and outbound traffic"

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }

  dynamic "egress" {
    for_each = var.egress_rules
    content {
      from_port   = egress.value.from_port
      to_port     = egress.value.to_port
      protocol    = egress.value.protocol
      cidr_blocks = egress.value.cidr_blocks
    }
  }
}

resource "aws_instance" "main" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.key.key_name
  vpc_security_group_ids = [aws_security_group.secgroup.name]

  tags = {
    Name = var.tag_name
  }

  provisioner "remote-exec" {
    inline = [
      "sudo sed -i '/^127.0.0.1/c\\127.0.0.1 ${var.computer_name} localhost.localdomain localhost' /etc/hosts",
      "sudo hostnamectl set-hostname ${var.computer_name}",
      "sudo apt-get update -y",
      "sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y",
      "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y wget curl git jq tar openssl net-tools ntp docker.io docker-compose"
  ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file(local.resolved_private_key_path)
      host        = self.public_ip
    }
  }
}
