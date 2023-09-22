data "azurerm_public_ip" "pip" {
  name                = azurerm_public_ip.pip.name
  resource_group_name = azurerm_resource_group.rg.name
  depends_on          = [azurerm_linux_virtual_machine.main]
}

output "instance_details" {
  value = {
    ip       = azurerm_public_ip.pip.ip_address
    user     = var.username_vm
    hostname = var.instance_name
  }
}
