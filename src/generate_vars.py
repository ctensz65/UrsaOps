import yaml
import re
import os
from jinja2 import Environment, FileSystemLoader
import shutil


class ansibleVars:
    def __init__(self, filepath, ursaops_root):
        self.filepath = filepath
        self.data = self.load_yaml()

        self.project_path = ursaops_root
        self.template_path = os.path.join(
            ursaops_root, "templates/terraform/inventory.tftpl"
        )
        self.path_terraform = os.path.join(ursaops_root, "terraform")
        self.path_ansible = os.path.join(ursaops_root, "ansible")

        self.valid_providers = ["aws", "azure", "digitalocean"]
        self.frameworks = ["sliver", "cobaltstrike", "havoc"]

        if "headscale" not in self.data:
            raise ValueError("[+] Headscale segment does not exist")

        self.exp_time_preauthkeys = self.data["headscale"]["setup"][
            "exp_time_preauthkeys"
        ]

        self.region = self.data["general"]["region"]

        self.general_defaults = {
            "project_name": "operation_spear",
            "ntp_timezone": "Asia/Jakarta",
            "vault_path": "",
            "region": "southeast asia",
            "provisioning_user": os.getenv("USER")
            or os.getenv("LOGNAME")
            or "default_user",
        }

        self.headscale_defaults = {
            "provider": "azure",
            "vm_username": "node",
            "vm_hostname": "headscale",
            "setup": {
                "dns_provider": "manual",
                "domain": "",
                "url": "https://controlplane.redteam.com",
                "acme_email": "noemail@redteam.com",
                "base_domain_local": "redteam.local",
                "jump_host": True,
                "exp_time_preauthkeys": "1m",
                "user_client": ["jumphost"],
            },
        }

        self.c2_defaults = {
            "provider": "azure",
            "dns_provider": "manual",
            "redir_https": {
                "count": 1,
                "domain": "redteam.id",
                "instance_name": "redirector_https",
                "vm_hostname": "redirhttps",
                "vm_username": "node",
            },
            "framework": {
                "count": 1,
                "instance_name": "c2_backend",
                "vm_hostname": "c2srv",
                "vm_username": "node",
            },
        }

        self.phish_defaults = {
            "provider": "aws",
            "dns_provider": "manual",
            "domain": "mydomainphish.com",
            "server": {
                "instance_name": "phish_backend",
                "vm_hostname": "phishsrv",
                "vm_username": "node",
            },
            "redir": {
                "instance_name": "redirector_phish",
                "vm_hostname": "redirphish",
                "vm_username": "node",
            },
            "evilginx": {
                "redirect_url": "https://login.microsoftonline.com",
                "path_lures": "/redirect",
                "phishlets": "o365",
            },
        }

        self.siem_defaults = {
            "provider": "aws",
            "vm_size": "",
            "dns_provider": "manual",
            "instance_name": "redelk",
            "vm_hostname": "redelk",
            "vm_username": "node",
        }

        self.defaults_mapping = {
            "general": self.general_defaults,
            "headscale": self.headscale_defaults,
            "segment_c2": self.c2_defaults,
            "segment_phish": self.phish_defaults,
            "segment_siem": self.siem_defaults,
        }

        # Map the region
        self.REGION_MAPPING = {
            "southeast-asia": {
                "aws": "ap-southeast-1",
                "digitalocean": "sgp1",
                "azure": "Southeast Asia",
            },
            "east-us": {"aws": "us-east-1", "digitalocean": "nyc1", "azure": "East US"},
            "west-us": {"aws": "us-west-1", "digitalocean": "sfo2", "azure": "West US"},
            "west-eu": {
                "aws": "eu-west-1",
                "digitalocean": "ams3",
                "azure": "West Europe",
            },
        }

        self.general_data = None
        self.headscale_data = None
        self.setup_data = None
        self.c2_data = None
        self.c2_framework = None
        self.phish_data = None
        self.siem_data = None

    def ansible_configs(self):
        path_dest = os.path.join(self.path_ansible, "inventory", "group_vars")
        configs = [
            {
                "output_type": "all",
                "data": {
                    "general_data": self.general_data,
                    "setup_data": self.setup_data,
                    "headscale_data": self.headscale_data,
                    "c2_data": self.c2_data,
                    "phish_data": self.phish_data,
                    "ansible_dir": self.path_ansible,
                    "siem_data": self.siem_data,
                },
                "filename": "all.yml",
            },
            {
                "output_type": "network",
                "data": {
                    "general_data": self.general_data,
                    "setup_data": self.setup_data,
                    "headscale_data": self.headscale_data,
                    "c2_data": self.c2_data,
                    "phish_data": self.phish_data,
                    "ansible_dir": self.path_ansible,
                },
                "filename": "network.yml",
            },
            {
                "output_type": "extravars",
                "data": {
                    "general_data": self.general_data,
                    "setup_data": self.setup_data,
                    "headscale_data": self.headscale_data,
                    "c2_data": self.c2_data,
                    "phish_data": self.phish_data,
                    "ansible_dir": self.path_ansible,
                    "siem_data": self.siem_data,
                },
                "filename": "extravars",
            },
        ]
        if self.c2_data and self.c2_framework:
            configs.append(
                {
                    "output_type": "c2_segment",
                    "data": {
                        "c2_data": self.c2_data,
                        "c2_framework": self.c2_framework,
                    },
                    "filename": "c2_segment.yml",
                }
            )
        else:
            print("[+] How can you bring your beacon?, You don't define C2 Segment")
        if self.phish_data:
            configs.append(
                {
                    "output_type": "segment_phish",
                    "data": {
                        "general_data": self.general_data,
                        "phish_data": self.phish_data,
                    },
                    "filename": "phish_segment.yml",
                }
            )
        else:
            print("[+] Nevermind, You don't define Phishing Segment")

        return configs, path_dest

    def print_config(self):
        path = os.path.join(self.project_path, "templates", "terraform")
        config = {
            "data": {
                "headscale_data": self.headscale_data,
                "setup_data": self.setup_data,
                "c2_data": self.c2_data,
                "c2_framework": self.c2_framework,
                "phish_data": self.phish_data,
                "siem_data": self.siem_data,
            },
        }

        return config, path

    def terraform_configs(self):
        path_dest = os.path.join(self.path_terraform, self.general_data["project_name"])
        configs = [
            {
                "output_type": "headscale",
                "data": {"headscale_data": self.headscale_data},
                "dir": os.path.join(
                    "segment1_network", self.headscale_data["provider"]
                ),
                "filename": "main.tf",
            },
        ]
        if self.c2_data and self.c2_framework:
            configs.append(
                {
                    "output_type": "c2",
                    "data": {
                        "c2_data": self.c2_data,
                        "c2_framework": self.c2_framework,
                    },
                    "dir": os.path.join("segment2_c2", self.c2_data["provider"]),
                    "filename": "main.tf",
                }
            )
        if self.phish_data:
            configs.append(
                {
                    "output_type": "phish",
                    "data": {"phish_data": self.phish_data},
                    "dir": os.path.join("segment3_phish", self.phish_data["provider"]),
                    "filename": "main.tf",
                }
            )
        if self.siem_data:
            configs.append(
                {
                    "output_type": "siem",
                    "data": {"siem_data": self.siem_data},
                    "dir": os.path.join("segment4_siem", self.siem_data["provider"]),
                    "filename": "main.tf",
                }
            )
        return configs, path_dest

    def update_attributes(self):
        self.general_data = self.data["general"]
        self.headscale_data = self.data["headscale"]
        self.setup_data = self.headscale_data["setup"]

        self.c2_data = self.data.get("segment_c2")
        self.c2_framework = self.c2_data["framework"] if self.c2_data else None
        self.phish_data = self.data.get("segment_phish")
        self.siem_data = self.data.get("segment_siem")

    def load_yaml(self):
        with open(self.filepath, "r") as stream:
            return yaml.safe_load(stream)

    def validate_provider(self, sections, key):
        provider = sections["provider"]
        if not provider:
            raise ValueError(f"No provider specified in the '{key}' section.")
        if provider not in self.valid_providers:
            raise ValueError(
                f"[+] '{provider}' in section '{key}' is not a valid provider. Valid providers are: {', '.join(self.valid_providers)}"
            )

    def c2_checks(self):
        segment_c2 = self.data.get("segment_c2", {})
        count = segment_c2.get("redir_https", {}).get("count", 0)
        framework = self.data["segment_c2"]["framework"]

        # update headscale users
        item = ["redir", "c2srv"]
        for i in item:
            if i not in self.headscale_defaults["setup"]["user_client"]:
                self.headscale_defaults["setup"]["user_client"].append(i)

        # validate c2 framework
        chosen_frameworks = [
            fw
            for fw in self.frameworks
            if fw in self.data.get("segment_c2", {}).get("framework", {})
        ]
        domains = segment_c2.get("redir_https", {}).get("domain", "").split(", ")

        if len(chosen_frameworks) > 1:
            raise ValueError(
                f"[+] Only one framework can be chosen. You've specified: {', '.join(chosen_frameworks)}"
            )
        elif count > 2:
            raise ValueError("[+] You can specify a maximum of 2 HTTPs Redirectors")
        elif len(domains) != count:
            raise ValueError(
                "[+] Define 2 different domains if you plan to build 2 HTTPs Redirectors"
            )
        elif len(domains) != len(set(domains)):
            raise ValueError("[+] All domains must be unique!")

        # Define default value for C2 frameworks
        if "sliver" in framework:
            sliver = {
                "version": "1.5.41",
                "user_agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.39 Safari/537.36 Brave/75",
                "uri_path": "__status/admin/metadata",
            }
            self.c2_defaults["framework"]["sliver"] = sliver
        elif "cobaltstrike" in framework:
            cobaltstrike = {
                "user_agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.39 Safari/537.36 Brave/75",
                "archieve_filename": "cobaltstrike.tar.gz",
                "profile": "webbug_getonly.profile",
            }
            self.c2_defaults["framework"]["cobaltstrike"] = cobaltstrike
        elif "havoc" in framework:
            havoc = {
                "profile": "havoc.yaotl",
                "user_agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.39 Safari/537.36 Brave/75",
            }
            self.c2_defaults["framework"]["havoc"] = havoc

        # Check for redir_dns existence
        if "redir_dns" in self.data["segment_c2"]:
            redir_dns_default = {
                "count": 1,
                "subdomain": "backoffice.redteam.id",
                "instance_name": "redir_dns",
                "vm_hostname": "redirdns",
                "vm_username": "node",
            }
            self.c2_defaults["redir_dns"] = redir_dns_default

    def merge_dicts(self, default, user_input):
        merged = user_input.copy()
        for key, value in default.items():
            if key in merged:
                if value is None:
                    merged[key] = value
                elif isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = self.merge_dicts(value, merged[key])
                elif merged[key] is None:
                    merged[key] = value
            else:
                merged[key] = value
        return merged

    def map_region_for_section(self, data, region, section_name):
        region_lower = region.lower()
        provider = data[section_name]["provider"]

        if region_lower in [k.lower() for k in self.REGION_MAPPING.keys()]:
            correct_region_key = next(
                k for k in self.REGION_MAPPING.keys() if k.lower() == region_lower
            )

            mapped_region = self.REGION_MAPPING[correct_region_key].get(provider, None)
            if not mapped_region:
                raise ValueError(
                    f"Provider {provider} not supported for region {region}"
                )
            else:
                data[section_name]["region"] = mapped_region
        else:
            raise ValueError(
                f"[+] Region {region} not defined in REGION_MAPPING [southeast-asia, east-us, west-us, west-eu]"
            )

    def ensure_dir(self, directory):
        os.makedirs(directory, exist_ok=True)

    def write_output_to_file(self, output, filename):
        if output:
            with open(filename, "w") as f:
                f.write(output)

    def process_configs(self, template_env_path, template_name, configs, path_prefix):
        env = Environment(
            loader=FileSystemLoader(template_env_path),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template(template_name)

        paths = {
            "TEMPLATE_PATH": self.template_path,
            "TERRAFORM_PATH": self.path_terraform,
        }

        for config in configs:
            if template_name == "headscale.j2":
                dir_path = os.path.join(path_prefix, config["dir"])
            else:
                dir_path = path_prefix
            self.ensure_dir(dir_path)

            output = template.render(
                output_type=config["output_type"], **config["data"], **paths
            )
            full_file_path = os.path.join(dir_path, config["filename"])
            self.write_output_to_file(output, full_file_path)

    def process_template_configs(self, kind, template_name):
        template_env_path = os.path.join(self.project_path, "templates", f"{kind}")
        configs, path_prefix = getattr(self, f"{kind}_configs")()

        self.process_configs(template_env_path, template_name, configs, path_prefix)

    def generate_ansible_vars(self):
        def print_output(template_env_path, template_name, configs):
            env = Environment(
                loader=FileSystemLoader(template_env_path),
                trim_blocks=True,
                lstrip_blocks=True,
            )
            template = env.get_template(template_name)
            return template.render(configs)

        # Validate headscale existence
        for key in self.data.keys():
            if key.startswith(("segment_", "headscale")):
                self.validate_provider(self.data[key], key)

        # Update headscale users
        if "segment_c2" in self.data:
            self.c2_checks()
        if "segment_phish" in self.data:
            self.headscale_defaults["setup"]["user_client"].append("phishsrv")
        if "segment_siem" in self.data:
            self.headscale_defaults["setup"]["user_client"].append("siem")
            provider_value = self.data["segment_siem"]["provider"]

            if provider_value == "aws":
                self.siem_defaults["vm_size"] = "t3.large"
            elif provider_value == "azure":
                self.siem_defaults["vm_size"] = "Standard_D2s_v3"
            elif provider_value == "digitalocean":
                self.siem_defaults["vm_size"] = "Standard Droplet"

        # Validate user file input
        for section, default in self.defaults_mapping.items():
            if section in self.data:
                for key in self.data[section].keys():
                    if key not in default:
                        raise ValueError(
                            f"The key '{key}' in section '{section}' is not allowed!"
                        )

        # Validate exp_time_preauthkeys format
        if self.exp_time_preauthkeys and not re.match(
            r"^\d+[mh]$", self.exp_time_preauthkeys
        ):
            raise ValueError("[+] Invalid exp_time_preauthkeys format.")

        # Merge between default parameter and client input
        for section, default in self.defaults_mapping.items():
            if section in self.data:
                self.data[section] = self.merge_dicts(default, self.data[section])

        # Mapping region for cloud provider
        for key in self.data:
            if key.startswith("segment_") or key == "headscale":
                self.map_region_for_section(self.data, self.region, key)

        # Update data
        self.update_attributes()

        # Render the template
        self.process_template_configs("ansible", "all.j2")
        self.process_template_configs("terraform", "headscale.j2")

        # Move extravars file
        src_path = f"{self.path_ansible}/inventory/group_vars/extravars"
        dst_dir = f"{self.path_ansible}/env"
        dst_path = f"{dst_dir}/extravars"

        self.ensure_dir(dst_dir)
        if os.path.exists(src_path):
            shutil.move(src_path, dst_path)
        else:
            print(f"Source file '{src_path}' does not exist!")

        # Print output
        data, path_template = self.print_config()
        output = print_output(path_template, "output.j2", data["data"])

        return self.general_data["project_name"], output
