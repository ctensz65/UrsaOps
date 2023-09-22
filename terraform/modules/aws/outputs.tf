output "instance_details" {
  value = {
    ip       = aws_instance.main.public_ip
    user     = var.username_vm
    hostname = var.instance_name
  }
}
