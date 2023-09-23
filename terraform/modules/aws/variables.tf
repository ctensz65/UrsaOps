variable "region" {
  default = "ap-southeast-1"
}

variable "instance_name" {
  description = "The name of the redirector instance"
  type        = string
}

variable "instance_type" {
  default = "t2.micro"
}

variable "computer_name" {
  description = "Hostname VM"
  type        = string
}

variable "username_vm" {
  description = "Username VM"
  type        = string
  default     = "ubuntu"
}

variable "ingress_rules" {
  description = "List of ingress rules"
  type = list(object({
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
  }))
  default = []
}

variable "egress_rules" {
  description = "List of egress rules"
  type = list(object({
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
  }))
  default = []
}

variable "tag_name" {
  type        = string
  default     = ""
}

# Local

variable "public_key" {
  default = ""
}

variable "private_key_path" {
  description = "Path to the private key file"
  default     = ""
}

variable "local_user" {
  description = "The local username, change to your localuser"
  type        = string
  default     = "ubuntu" 
}



