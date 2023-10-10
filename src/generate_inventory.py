import os
import re


def print_inventory(output_file):
    with open(output_file, "r") as infile:
        print(f"==========================================")
        for line in infile:
            line = line.strip()
            if line and not line.startswith("["):
                match = re.search(
                    r"(\w+)\s+ansible_host=([\d.]+).*ansible_user=(\w+)", line
                )
                if match:
                    hostname = match.group(1)
                    host = match.group(2)
                    user = match.group(3)
                    print(f"{hostname} = ssh {user}@{host}")
        print(f"==========================================/n")


def merge_inventories(project_name, base_dir, output_file):
    all_hosts = []
    redir_https_hosts = []
    c2_framework = []

    full_path = os.path.join(base_dir, project_name)
    # Create or overwrite the merged inventory file
    with open(output_file, "w") as outfile:
        # outfile.write("".join("localhost ansible_connection=local\n\n"))
        for segment_dir in sorted(os.listdir(full_path)):
            segment_path = os.path.join(full_path, segment_dir)

            if os.path.isdir(segment_path) and "segment" in segment_dir:
                for cloud_dir in os.listdir(segment_path):
                    cloud_path = os.path.join(segment_path, cloud_dir)

                    if os.path.isdir(cloud_path):
                        inventory_file = os.path.join(cloud_path, "inventory.ini")

                        # Check if inventory.ini exists
                        if os.path.isfile(inventory_file):
                            with open(inventory_file, "r") as infile:
                                lines = infile.readlines()
                                for line in lines:
                                    line = line.strip()
                                    if line.startswith("["):
                                        outfile.write(line + "\n")
                                    elif line and not line.startswith("["):
                                        host = line.split()[0]
                                        all_hosts.append(host)

                                        # Check for redir_https pattern
                                        if host.startswith("https"):
                                            redir_https_hosts.append(host)

                                        if host.startswith(
                                            "c2_server"
                                        ) or host.startswith("jumphost"):
                                            c2_framework.append(host)

                                        outfile.write(line + "\n")
                                outfile.write("\n")

        # Check for multiple redir_https hosts
        if len(redir_https_hosts) > 1:
            outfile.write("[group_redir_https]\n")
            for host in redir_https_hosts:
                outfile.write(host + "\n")
            outfile.write("\n")

        outfile.write("[c2_srvclient]\n")
        for host in c2_framework:
            outfile.write(host + "\n")
        outfile.write("\n")
