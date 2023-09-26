import ansible_runner
import sys
import os
from tqdm import tqdm
import time
import threading
from python_terraform import *

from generate_vars import ansibleVars
from generate_inventory import merge_inventories

ursaops_root = os.environ.get("URSAOPS_ROOT")
if ursaops_root is None:
    raise EnvironmentError("The URSAOPS_ROOT environment variable is not set!")

BASE_DIR_ANSIBLE = os.path.join(ursaops_root, "ansible")


class wrapper:
    def __init__(self, project_name):
        self.project_name = project_name
        self.ansible_playbook_path = os.path.join(ursaops_root, "ansible", "playbooks")
        self.terraform_project_path = os.path.join(
            ursaops_root, "terraform", self.project_name
        )
        self.main_tf_files = []
        self.spin = False

    def spinner(self):
        symbols = ["|", "/", "-", "\\"]
        idx = 0
        while self.spin:
            sys.stdout.write("\r" + symbols[idx % len(symbols)])
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)
        sys.stdout.write("\rDone!\n")

    def search_maintf(self):
        """
        Find all main.tf files under the project directory
        """
        for segment in os.listdir(self.terraform_project_path):
            segment_path = os.path.join(self.terraform_project_path, segment)
            if os.path.isdir(segment_path):
                for cloud_provider in os.listdir(segment_path):
                    cloud_provider_path = os.path.join(segment_path, cloud_provider)
                    main_tf_path = os.path.join(cloud_provider_path, "main.tf")
                    if os.path.isfile(main_tf_path):
                        self.main_tf_files.append(cloud_provider_path)
        print(self.main_tf_files)
        return self.main_tf_files

    def terraform(self, action):
        main_tf_files = self.search_maintf()

        for tf_directory in main_tf_files:
            tf = Terraform(working_dir=tf_directory)

            #'''
            # Run Terraform init
            print(f"Initializing Terraform in {tf_directory}")
            return_code, stdout, stderr = tf.init(capture_output=False)
            if return_code != 0:
                print(f"Failed to initialize Terraform in {tf_directory}")
                print(stderr)
                continue  # Skip to the next iteration if initialization fails
            #'''

            # Run Terraform plan
            print(f"Planning Terraform in {tf_directory}")
            return_code, stdout, stderr = tf.plan(capture_output=False)
            if return_code != 0:
                print(f"Failed to plan Terraform in {tf_directory}")
                print(stderr)
                continue  # Skip to the next iteration if planning fails

            # if action == "deploy":
            #     # Run Terraform apply
            #     print(f"Applying Terraform in {tf_directory}")
            #     return_code, stdout, stderr = tf.apply(
            #         capture_output=False, skip_plan=True, auto_approve=True
            #     )
            #     if return_code != 0:
            #         print(f"Failed to apply Terraform in {tf_directory}")
            #         print(stderr)
            # elif action == "destroy":
            #     # Run Terraform Destoy
            #     print(f"Destroying Instances in {tf_directory}")
            #     return_code, stdout, stderr = tf.destroy(
            #         capture_output=False, skip_plan=True, auto_approve=True
            #     )
            #     if return_code != 0:
            #         print(f"Failed to destroy Terraform in {tf_directory}")
            #         print(stderr)

        # os.makedirs(os.path.dirname(self.OUTPUT_INVENTORY), exist_ok=True)
        # merge_inventories(self.project_name, BASE_DIR_TERRAFORM, self.OUTPUT_INVENTORY)


def usage():
    print("----------------")
    print("Deploy: python main.py deploy input_file.yaml")
    print("Provisioning: python main.py provisioning")
    print("Destroy: python main.py destroy")
    print("----------------")


if __name__ == "__main__":
    try:
        arg_command = sys.argv[1].strip().lower()
    except IndexError:
        usage()
        sys.exit(1)

    if arg_command == "deploy":
        try:
            input_yaml = sys.argv[2].strip().lower()
            ansible_vars_instance = ansibleVars(input_yaml, ursaops_root)

            project_name, output = ansible_vars_instance.generate_ansible_vars()

            print("\nEngagement Name:", project_name)
            print(output)

            confirmation = (
                input("Does everything look okay? Type 'yes' to continue deploying: ")
                .strip()
                .lower()
            )
            if confirmation == "yes":
                instance = wrapper(project_name)
                instance.terraform(arg_command)
            else:
                print("Aborting the process.")
        except IndexError:
            print("Input file yaml required!")
    elif arg_command == "destroy":
        # instance = wrapper(project_name)
        # instance.terraform(arg_command)
        print("Aborting the process.")
    else:
        usage()
        sys.exit(1)
