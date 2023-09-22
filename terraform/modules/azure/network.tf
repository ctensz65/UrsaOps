resource "azurerm_virtual_network" "vnet" {
  name                = "${var.instance_name}-network"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "subnet" {
  name                 = "${var.instance_name}-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "pip" {
  name                = "${var.instance_name}-pip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
}

resource "azurerm_network_security_group" "nsg" {
  name                = "${var.instance_name}-nsg"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  dynamic "security_rule" {
    for_each = var.inbound_rules
    content {
      name                        = "inbound_rule_${security_rule.value.port}_${security_rule.value.protocol}"
      priority                    = 100 + security_rule.key
      direction                   = "Inbound"
      access                      = "Allow"
      protocol                    = security_rule.value.protocol
      source_port_range           = "*"
      destination_port_range      = security_rule.value.port
      source_address_prefix       = "*"
      destination_address_prefix  = "*"
    }
  }
}

resource "azurerm_network_interface_security_group_association" "as" {
  network_interface_id      = azurerm_network_interface.ni.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

resource "azurerm_network_interface" "ni" {
  name                      = "${var.instance_name}-nic"
  location                  = azurerm_resource_group.rg.location
  resource_group_name       = azurerm_resource_group.rg.name
  
  ip_configuration {
    name                          = "${var.instance_name}_nic_config"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.pip.id
  }
}