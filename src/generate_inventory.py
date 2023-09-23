import os

def merge_inventories(project_name, base_dir, output_file):
    all_hosts = []
    redir_https_hosts = []
    c2_framework = []

    full_path = os.path.join(base_dir, project_name)
    # Create or overwrite the merged inventory file
    with open(output_file, 'w') as outfile:
        outfile.write("".join("localhost ansible_connection=local\n\n"))
        for segment_dir in sorted(os.listdir(full_path)):
            segment_path = os.path.join(full_path, segment_dir)

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

                                        if host.startswith("c2_srv") or host.startswith("jumphost"):
                                            c2_framework.append(host)

                                outfile.write("".join(lines))
                                outfile.write("\n\n")

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

        #outfile.write("localhost\n")