variable "instance_name" {
  description = "The name of the redirector instance"
  type        = string
}

variable "location" {
  description = "Azure region/location for the instance"
  type        = string
  default     = "Southeast Asia"
}

variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
}

variable "computer_name" {
  description = "Hostname VM"
  type        = string
}

variable "username_vm" {
  description = "Username VM"
  type        = string
  default     = "Ubuntu"
}

variable "vm_size" {
  description = "Size VM"
  type        = string
  default     = "Standard_B2s"
}

variable "tags_segment" {
  type        = string
  default     = "redirector"
}

variable "admin_pass" {
  type        = string
  default     = "P@ssw0rd123"
}

variable "local_user" {
  description = "The local username, can be overridden by setting the TF_VAR_local_user"
  type        = string
  default     = "leroy"
}

variable "private_key_path" {
  description = "Path to the private SSH key"
  type        = string
  default     = "" 
}

variable "public_key" {
  description = "Path to the public SSH key"
  type        = string
  default     = "" 
}

variable "inbound_rules" {
  description = "List of inbound port and protocol maps. e.g. [{'port': '443', 'protocol': 'Tcp'}, {'port': '53', 'protocol': 'Udp'}]"
  type        = list(object({
    port     = string
    protocol = string
  }))
  default     = []
}

