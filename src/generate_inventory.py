import os

BASE_DIR = os.path.abspath('terraform')
OUTPUT_FILE = "ansible/inventory/hosts.ini"


def merge_inventories(base_dir, output_file):
    all_hosts = []
    redir_https_hosts = []

    # Create or overwrite the merged inventory file
    with open(output_file, 'w') as outfile:
        for segment_dir in sorted(os.listdir(base_dir)):
            segment_path = os.path.join(base_dir, segment_dir)

            # Ensure it's a directory and has 'segment' in its name
            if os.path.isdir(segment_path) and 'segment' in segment_dir:
                for cloud_dir in os.listdir(segment_path):
                    cloud_path = os.path.join(segment_path, cloud_dir)

                    if os.path.isdir(cloud_path):
                        inventory_file = os.path.join(
                            cloud_path, "inventory.ini")

                        # Check if inventory.ini exists in the directory
                        if os.path.isfile(inventory_file):
                            with open(inventory_file, 'r') as infile:
                                lines = infile.readlines()
                                for line in lines:
                                    line = line.strip()
                                    if line and not line.startswith("["):
                                        host = line.split()[0]
                                        all_hosts.append(host)

                                        # Check for redir_https pattern
                                        if host.startswith("redir_https"):
                                            redir_https_hosts.append(host)

                                outfile.write("".join(lines))
                                outfile.write("\n")

        # Check for multiple redir_https hosts
        if len(redir_https_hosts) > 1:
            outfile.write("[group_redir_https]\n")
            for host in redir_https_hosts:
                outfile.write(host + "\n")
            outfile.write("\n")

        # Writing the [all] group at the end
        outfile.write("[all]\n")
        for host in all_hosts:
            outfile.write(host + "\n")
        outfile.write("localhost\n")


if __name__ == "__main__":
    merge_inventories(BASE_DIR, OUTPUT_FILE)
