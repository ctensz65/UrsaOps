variable "do_token" {
  description = "The DigitalOcean API token"
  sensitive   = true
}

variable "ssh_fingerprint" {
  description = "The fingerprint of the SSH key to use for the Droplet"
}

variable "do_name" {
  type      = string
  default   = "Droplet_dev"
}

variable "do_size" {
  description = "Size VM"
  type        = string
  default     = "s-1vcpu-1gb"
}

variable "do_region" {
  type        = string
  default     = "nyc3"
}