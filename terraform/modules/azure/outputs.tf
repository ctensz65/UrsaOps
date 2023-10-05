data "azurerm_public_ip" "pip" {
  name                = azurerm_public_ip.pip.name
  resource_group_name = var.resource_group_name
  depends_on          = [azurerm_linux_virtual_machine.main]
}

output "instance_details" {
  value = {
    ip       = azurerm_public_ip.pip.ip_address
    user     = var.username_vm
    hostname = var.computer_name
    pass     = azurerm_linux_virtual_machine.main.admin_password
  }
}
