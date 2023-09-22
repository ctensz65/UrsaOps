import yaml
import re
import os
from jinja2 import Environment, FileSystemLoader

# ====================== DEFINE DEFAULT PARAMETERS ====================== #
general_defaults = {
    "project_name": "operation_spear",
    "ntp_timezone": "Asia/Jakarta",
    "vault_path": "",
    "region": "southeast asia",
    "provisioning_user": os.getenv("USER") or os.getenv("LOGNAME") or "default_user",
}

headscale_defaults = {
    "provider": "azure",
    "vm_username": "headscale",
    "vm_hostname": "headscale",
    "setup": {
        "dns_provider": "manual",
        "domain": "",
        "url": "https://controlplane.redteam.com",
        "acme_email": "noemail@redteam.com",
        "base_domain_local": "redteam.local",
        "jump_host": True,
        "exp_time_preauthkeys": "5m",
        "user_client": ["redirector", "c2_srv", "phish_srv", "jumphost"],
    },
}

c2_defaults = {
    "provider": "azure",
    "dns_provider": "manual",
    "redir_https": {
        "count": 1,
        "domain": "redteam.id",
        "vm_hostname": "redirhttps",
        "vm_username": "node2",
    },
    "framework": {
        "count": 1,
        "vm_hostname": "c2srv",
        "vm_username": "node3",
    },
}

phish_defaults = {
    "provider": "aws",
    "dns_provider": "manual",
    "domain": "mydomainphish.com",
    "server": {
        "vm_hostname": "phish_srv",
        "vm_username": "ops",
    },
    "redir": {
        "vm_hostname": "redir",
        "vm_username": "phredir",
    },
    "evilginx": {
        "redirect_url": "https://login.microsoftonline.com",
        "path_lures": "/redirect",
        "phishlets": "o365",
    },
}

# ====================== LOAD YAML ====================== #
with open("operator_input.yml", "r") as stream:
    data = yaml.safe_load(stream)

# ====================== CONDITION BEFORE MERGE ====================== #
defaults_mapping = {
    "general": general_defaults,
    "headscale": headscale_defaults,
    "segment_c2": c2_defaults,
    "segment_phish": phish_defaults,
}

# Validate cloud providers
valid_providers = ["aws", "azure", "digitalocean"]


def validate_provider(sections, key):
    provider = sections["provider"]
    if not provider:
        raise ValueError(f"No provider specified in the '{key}' section.")
    if provider not in valid_providers:
        raise ValueError(
            f"[+] '{provider}' in section '{key}' is not a valid provider. Valid providers are: {', '.join(valid_providers)}"
        )


for key in data.keys():
    if key.startswith(("segment_", "headscale")):
        validate_provider(data[key], key)

if "segment_c2" in data:
    # Validate chosen c2 frameworks
    frameworks = ["sliver", "cobaltstrike", "havoc"]
    chosen_frameworks = [
        fw for fw in frameworks if fw in data.get("segment_c2", {}).get("framework", {})
    ]
    if len(chosen_frameworks) > 1:
        raise ValueError(
            f"[+] Only one framework can be chosen. You've specified: {', '.join(chosen_frameworks)}"
        )

    # Add default parameters of choosen framework
    framework = data["segment_c2"]["framework"]
    if "sliver" in framework:
        sliver = {
            "version": "1.5.41",
            "user_agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.39 Safari/537.36 Brave/75",
            "uri_path": "__status/admin/metadata",
        }
        c2_defaults["framework"]["sliver"] = sliver
    elif "cobaltstrike" in framework:
        cobaltstrike = {
            "user_agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.39 Safari/537.36 Brave/75",
            "archieve_file_path": "/opt/cobaltstrike.tar.gz",
            "profile": "webbug_getonly.profile",
        }
        c2_defaults["framework"]["cobaltstrike"] = cobaltstrike
    elif "havoc" in framework:
        havoc = {
            "profile": "havoc.yaotl",
            "user_agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.39 Safari/537.36 Brave/75",
        }
        c2_defaults["framework"]["havoc"] = havoc

    # Extract details from segment_c2 section
    segment_c2 = data.get("segment_c2", {})
    count = segment_c2.get("redir_https", {}).get("count", 0)
    if count > 2:
        raise ValueError("[+] You can specify a maximum of 2 HTTPs Redirectors")

    domains = segment_c2.get("redir_https", {}).get("domain", "").split(", ")
    if len(domains) != count:
        raise ValueError(
            "[+] Define 2 different domains if you plan to build 2 HTTPs Redirectors"
        )

    if len(domains) != len(set(domains)):
        raise ValueError("[+] All domains must be unique!")

    # Check for redir_dns existence
    if "redir_dns" in data["segment_c2"]:
        redir_dns_default = {
            "count": 1,
            "subdomain": "backoffice.redteam.id",
            "vm_hostname": "redirdns",
            "vm_username": "node3",
        }
        c2_defaults["redir_dns"] = redir_dns_default

# Validate User Input
for section, default in defaults_mapping.items():
    if section in data:
        for key in data[section].keys():
            if key not in default:
                raise ValueError(
                    f"The key '{key}' in section '{section}' is not allowed!"
                )

# Validate exp_time_preauthkeys format
exp_time_preauthkeys = data["headscale"]["setup"]["exp_time_preauthkeys"]
if exp_time_preauthkeys and not re.match(r"^\d+[mh]$", exp_time_preauthkeys):
    raise ValueError("[+] Invalid exp_time_preauthkeys format.")

# ====================== MERGE PARAMETER ====================== #


def merge_dicts(default, user_input):
    merged = user_input.copy()
    for key, value in default.items():
        if key in merged:
            if value is None:
                merged[key] = value
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key] = merge_dicts(value, merged[key])
            elif merged[key] is None:
                merged[key] = value
        else:
            merged[key] = value
    return merged


for section, default in defaults_mapping.items():
    if section in data:
        data[section] = merge_dicts(default, data[section])

# ====================== CONDITION AFTER ====================== #
# Map the region
REGION_MAPPING = {
    "southeast-asia": {
        "aws": "ap-southeast-1",
        "digitalocean": "sgp1",
        "azure": "Southeast Asia",
    },
    "east-us": {"aws": "us-east-1", "digitalocean": "nyc1", "azure": "East US"},
    "west-us": {"aws": "us-west-1", "digitalocean": "sfo2", "azure": "West US"},
    "west-eu": {"aws": "eu-west-1", "digitalocean": "ams3", "azure": "West Europe"},
}


def map_region_for_section(data, region, section_name):
    region_lower = region.lower()
    provider = data[section_name]["provider"]

    if region_lower in [k.lower() for k in REGION_MAPPING.keys()]:
        correct_region_key = next(
            k for k in REGION_MAPPING.keys() if k.lower() == region_lower
        )

        mapped_region = REGION_MAPPING[correct_region_key].get(provider, None)
        if not mapped_region:
            raise ValueError(f"Provider {provider} not supported for region {region}")
        else:
            data[section_name]["region"] = mapped_region
    else:
        raise ValueError(
            f"[+] Region {region} not defined in REGION_MAPPING [southeast-asia, east-us, west-us, west-eu]"
        )


region = data["general"]["region"]

# Dynamically check for segments
for key in data:
    if key.startswith("segment_") or key == "headscale":
        map_region_for_section(data, region, key)

# ====================== Accessing the merged data ====================== #
general_data = data["general"]
headscale_data = data["headscale"]
setup_data = headscale_data["setup"]

c2_data = data.get("segment_c2")
c2_framework = c2_data["framework"] if c2_data else None
phish_data = data.get("segment_phish")


# Ensure a directory exists; if it doesn't, create it.
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# Check if a file exists in a directory
def file_exists(directory, filename):
    return os.path.isfile(os.path.join(directory, filename))


# Define a function to write output to a file
def write_output_to_file(output, filename):
    if output:
        with open(filename, "w") as f:
            f.write(output)


# Load Jinja2 templates
env_ansible = Environment(loader=FileSystemLoader("./templates/ansible_vars"))
template_ansible = env_ansible.get_template("all.j2")

env_tf = Environment(
    loader=FileSystemLoader("./templates/terraform_main"),
    trim_blocks=True,
    lstrip_blocks=True,
)
template_terraform = env_tf.get_template("headscale.j2")

# Configuration for template rendering and corresponding messages
configs = [
    {
        "condition": True,
        "output_type": "all",
        "data": {
            "general_data": general_data,
            "setup_data": setup_data,
            "headscale_data": headscale_data,
            "c2_data": c2_data,
            "phish_data": phish_data,
        },
        "dir": "./ansible2/group_vars/",
        "filename": "all.yml",
        "error_msg": "Warning! You don't define Network Segment",
    },
    {
        "condition": c2_data and c2_framework,
        "output_type": "c2_segment",
        "data": {"c2_data": c2_data, "c2_framework": c2_framework},
        "dir": "./ansible2/group_vars/",
        "filename": "c2_segment.yml",
        "error_msg": "[+] How can you bring your beacon?, You don't define C2 Segment",
    },
    {
        "condition": phish_data,
        "output_type": "segment_phish",
        "data": {"general_data": general_data, "phish_data": phish_data},
        "dir": "./ansible2/group_vars/",
        "filename": "phish_segment.yml",
        "error_msg": "[+] Nevermind, You don't define Phishing Segment",
    },
]

path_ansible_vars = "./ansible2/group_vars/"
# Process based on configuration
for config in configs:
    ensure_dir(path_ansible_vars)

    # if file_exists(path_ansible_vars, config["filename"]):
    #     raise FileExistsError(
    #         f"File {config['filename']} already exists in '{path_ansible_vars}'"
    #     )

    if config.get("condition", True):
        output = template_ansible.render(
            output_type=config["output_type"], **config["data"]
        )
        full_file_path = os.path.join(path_ansible_vars, config["filename"])
        write_output_to_file(output, full_file_path)
    else:
        print(config["error_msg"])

print(general_data["project_name"])
# For the Terraform templates
terraform_configs = [
    {
        "output_type": "headscale",
        "data": {"headscale_data": headscale_data},
        "dir": "/segment1_network/" + headscale_data["provider"],
        "filename": "main.tf",
    },
    {
        "output_type": "c2",
        "data": {"c2_data": c2_data, "c2_framework": c2_framework},
        "dir": "/segment2_c2/" + c2_data["provider"],
        "filename": "main.tf",
        "condition": c2_data and c2_framework,
    },
    {
        "output_type": "phish",
        "data": {"phish_data": phish_data},
        "dir": "/segment3_phish/" + phish_data["provider"],
        "filename": "main.tf",
        "condition": phish_data,
    },
]

# Process based on configuration
for config in terraform_configs:
    dir = "./terraform2/" + general_data["project_name"] + config["dir"]
    ensure_dir(dir)

    if file_exists(dir, config["filename"]):
        raise FileExistsError(
            f"File {config['filename']} already exists in '{config['dir']}'"
        )

    if config.get("condition", True):
        output = template_terraform.render(
            output_type=config["output_type"], **config["data"]
        )
        full_file_path = os.path.join(dir, config["filename"])
        write_output_to_file(output, full_file_path)
