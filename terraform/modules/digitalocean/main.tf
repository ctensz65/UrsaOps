provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "main" {
  image  = "ubuntu-20-04-x64"
  name   = var.do_name
  region = var.do_region
  size   = var.do_size
  ssh_keys = [
    var.ssh_fingerprint
  ]
  connection {
    host = self.ipv4_address
    user = "root"
    type = "ssh"
    private_key = file(var.pvt_key)
    timeout = "2m"
  }
  provisioner "remote-exec" {
    inline = [
      "export PATH=$PATH:/usr/bin",
      "sudo apt-get update",
      "sudo apt-get upgrade -y"
    ]
  }
}

