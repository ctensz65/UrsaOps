resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

locals {
  resolved_private_key_path = var.private_key_path != "" ? var.private_key_path : "/home/${var.local_user}/.ssh/id_rsa"
  resolved_public_key_path  = var.public_key != "" ? var.public_key : "/home/${var.local_user}/.ssh/id_rsa.pub"
}

resource "azurerm_linux_virtual_machine" "main" {
  name                  = var.instance_name
  location              = azurerm_resource_group.rg.location
  resource_group_name   = azurerm_resource_group.rg.name
  network_interface_ids = [ azurerm_network_interface.ni.id ]
  size                  = var.vm_size
  computer_name         = var.computer_name
  admin_username        = var.username_vm
  admin_password        = var.admin_pass
  disable_password_authentication = true

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "20.04.202307140"
  }

  os_disk {
    caching               = "ReadWrite"
    storage_account_type  = "Standard_LRS"
  }
  
  admin_ssh_key {
    username   = var.username_vm
    public_key = file(local.resolved_public_key_path)
  }

  tags = {
    environment = "redteam"
    segment     = var.tags_segment
  }
  
  connection {
    type        = "ssh"
    host        = azurerm_public_ip.pip.ip_address
    user        = var.username_vm
    private_key = file(local.resolved_private_key_path)        
    agent       = false
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get upgrade -y"
    ]
  }
}