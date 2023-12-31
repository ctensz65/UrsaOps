import ansible_runner
import sys
import os
from python_terraform import *
import yaml
import argparse
import logging

from generate_vars import ansibleVars
from generate_inventory import *

ursaops_root = os.environ.get("URSAOPS_ROOT")
if ursaops_root is None:
    raise EnvironmentError("The URSAOPS_ROOT environment variable is not set!")

BASE_DIR_ANSIBLE = os.path.join(ursaops_root, "ansible")
BASE_DIR_TERRAFORM = os.path.join(ursaops_root, "terraform")


class Color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


class wrapper:
    def __init__(self, project_name):
        self.project_name = project_name
        self.ansible_playbook_path = os.path.join(BASE_DIR_ANSIBLE, "playbooks")
        self.terraform_project_path = os.path.join(
            ursaops_root, "terraform", self.project_name
        )
        self.main_tf_files = []
        self.spin = False
        self.OUTPUT_INVENTORY = os.path.join(BASE_DIR_ANSIBLE, "inventory/hosts.ini")

        self.map_playbook = {
            "segment1_network": "setup_network.yml",
            "segment2_c2": "setup_c2.yml",
            "segment3_phish": "setup_phishing.yml",
            "segment4_siem": "setup_siem.yml",
        }

        self.map_groupvars = {
            "segment1_network": "all.yml",
            "segment2_c2": "c2_segment.yml",
            "segment3_phish": "phish_segment.yml",
            "segment4_siem": "siem_segment.yml",
        }

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
        matches = [
            re.search(r"segment\d+_(\w+)", file).group(1)
            for file in self.main_tf_files
            if re.search(r"segment\d+_(\w+)", file)
        ]
        return self.main_tf_files, matches

    def tform_init(self, tf, tf_directory):
        print(
            f"\n{Color.YELLOW}====================== Initializing Terraform in {tf_directory}{Color.END}\n"
        )

        return_code, stdout, stderr = tf.init()

        if return_code == 0:
            print(f"Succeeded to initialize Terraform in {tf_directory}\n")
        else:
            print(f"\nFailed to initialize Terraform in {tf_directory}\n")
            print(stderr)

    def tform_plan(self, tf, tf_directory, plan_out):
        print(
            f"{Color.YELLOW}====================== Planning Terraform in {tf_directory}{Color.END}\n"
        )
        return_code, stdout, stderr = tf.plan(no_color=IsFlagged, refresh=False)
        if return_code != 0:
            print(f"\nFailed to plan Terraform in {tf_directory}\n")
            print(stderr)

        print("Generated Terraform Plan:")
        print(stdout)

        user_input = input("Do you wish to apply this plan? (y/n): ")
        if user_input.lower() != "y":
            raise ValueError("Terraform apply aborted by user.")

    def tform_apply(self, tf, tf_directory):
        print(
            f"{Color.YELLOW}====================== Applying Terraform in {tf_directory}{Color.END}\n"
        )
        return_code, stdout, stderr = tf.apply(
            no_color=IsFlagged, refresh=False, skip_plan=True
        )
        if return_code == 0:
            print(f"Succeeded to apply Terraform in {tf_directory}\n")
        else:
            print(f"\nFailed to apply Terraform in {tf_directory}\n")
            print(stderr)

    def tform_destroy(self, tf, tf_directory):
        print(
            f"{Color.YELLOW}====================== Destroying Instances in {tf_directory}{Color.END}\n"
        )
        return_code, stdout, stderr = tf.destroy(force=True)

        if return_code == 0:
            print(f"Succeeded to destroy Terraform infrastructure in {tf_directory}\n")
        else:
            print(f"\nFailed to destroy Terraform infrastructure in {tf_directory}\n")
            print(stderr)

    def process(self, action):
        main_tf_files, segments = self.search_maintf()

        def choose_deployment_segment():
            input_message = "\nWhich segment would you like to deploy with terraform?\n"
            for index, item in enumerate(segments):
                input_message += f"{index + 1}) {item}\n"

            input_message += f"{len(segments) + 1}) all\n"
            input_message += f"{len(segments) + 2}) exclude certain segments\n"
            input_message += "\nYour choice: "

            while True:
                user_input = input(input_message)

                # Check if input is valid
                if user_input.isdigit() and 1 <= int(user_input) <= len(segments) + 2:
                    user_choice = int(user_input)

                    # User selected a specific segment.
                    if 1 <= user_choice <= len(segments):
                        to_be_deploy = [segments[user_choice - 1]]
                        break

                    # User selected all segments.
                    elif user_choice == len(segments) + 1:
                        to_be_deploy = segments
                        break

                    # User chose to exclude certain segments.
                    elif user_choice == len(segments) + 2:
                        excluded_segments = input(
                            "\nWhich segments would you like to exclude? (comma-separated): "
                        ).split(",")
                        to_be_deploy = [
                            segment
                            for segment in segments
                            if segment not in excluded_segments
                        ]
                        break

                print("Invalid choice. Please try again.")
            print("Deploying on segment(s): " + ", ".join(to_be_deploy))
            return to_be_deploy

        to_be_deploy = choose_deployment_segment()
        main_tf_files = [
            path
            for path in main_tf_files
            for segment in to_be_deploy
            if segment in path
        ]

        for tf_directory in main_tf_files:
            # plan_out_file = os.path.join(tf_directory, "terraform.tfplan")
            tf = Terraform(working_dir=tf_directory)

            self.tform_init(tf, tf_directory)

            if action == "deploy":
                self.tform_apply(tf, tf_directory)

            elif action == "destroy":
                self.tform_destroy(tf, tf_directory)

        if action == "deploy":
            os.makedirs(os.path.dirname(self.OUTPUT_INVENTORY), exist_ok=True)
            merge_inventories(
                self.project_name, BASE_DIR_TERRAFORM, self.OUTPUT_INVENTORY
            )
            print_inventory(self.OUTPUT_INVENTORY)

    def provision(self, segment, tags=None):
        if segment in self.map_groupvars:
            var = self.map_groupvars[segment]
            dns_provider = check_ansible_vars(var, "dns_provider")
            if dns_provider == "manual":
                print(
                    f"{Color.GREEN}====================== Remember, You choose to setup DNS Records manually{Color.END}\n"
                )

        if segment in self.map_playbook:
            print(
                f"{Color.YELLOW}====================== Perform Provisioning on {segment}{Color.END}\n"
            )
            playbook_path = f"playbooks/{self.map_playbook[segment]}"

            r = ansible_runner.run(
                private_data_dir=BASE_DIR_ANSIBLE,
                playbook=playbook_path,
                inventory=self.OUTPUT_INVENTORY,
                tags=tags,
            )
            print(r.stats)
        else:
            print(f"No playbook mapped for segment: {segment}")


def is_yaml_file(filename):
    """
    Check if the given filename has a .yaml or .yml extension.
    """
    allowed_extensions = [".yaml", ".yml"]
    _, extension = os.path.splitext(filename)
    return extension.lower() in allowed_extensions


def check_ansible_vars(var: str, key: str):
    try:
        vars_file = f"{BASE_DIR_ANSIBLE}/inventory/group_vars/{var}"

        with open(vars_file, "r") as file:
            data = yaml.safe_load(file)

        return data[key]
    except FileNotFoundError:
        logging.error(f"Ansible Vars File not Found")
    except yaml.YAMLError as exc:
        logging.error(f"Error parsing YAML file: {exc}")


def main():
    parser = argparse.ArgumentParser(description="Manage Terraform deployments.")
    subparsers = parser.add_subparsers(dest="command")

    deploy_parser = subparsers.add_parser("deploy", help="Deploy infrastructure.")
    deploy_parser.add_argument(
        "input_file", type=str, help="Path to the input YAML file."
    )

    provisioning_parser = subparsers.add_parser(
        "provisioning", help="Provision infrastructure."
    )

    destroy_parser = subparsers.add_parser("destroy", help="Destroy infrastructure.")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    if args.command == "deploy":
        input_file = sys.argv[2].strip().lower()

        if not is_yaml_file(input_file):
            raise ValueError(
                "Invalid input file. Only .yaml or .yml files are allowed."
            )

        ansible_vars_instance = ansibleVars(input_file, ursaops_root)
        project_name, output = ansible_vars_instance.generate_ansible_vars()

        print("\nProject Name:", project_name, "\n")
        print(output)

        confirmation = (
            input("\nDoes everything look okay? Type 'yes' to continue deploying: ")
            .strip()
            .lower()
        )
        if confirmation == "yes":
            instance = wrapper(project_name)
            instance.process(args.command)
        else:
            logging.info("Aborting the process")

    elif args.command == "provisioning":
        project_name = check_ansible_vars("all.yml", "project_name")
        project_path = f"{BASE_DIR_TERRAFORM}/{project_name}"

        instance = wrapper(project_name)
        segments, _ = instance.search_maintf()
        segments = [
            re.search(r"/segment[^/]+", path).group(0)[1:]
            if re.search(r"/segment[^/]+", path)
            else path
            for path in segments
        ]

        if project_path:
            print(f"Found the currect project !\n{project_name}")
            for segment in segments:
                print(" - " + segment)
            user_input = input(f"Start the provisioning? [y/N] > ")
            if user_input.lower() == "y":
                logging.info("OK")
                # for segment in segments:
                #     instance.provision(segment)
                instance.provision(segments[1])
            else:
                logging.info("Operation cancelled by the user.")

    elif args.command == "destroy":
        project_path, project_name = check_ansible_vars("all.yml", "project_name")

        if os.path.isdir(project_path):
            user_input = input(
                f"Are you sure you want to destroy the resources in {project_path}? [y/N] "
            )
            if user_input.lower() == "y":
                logging.info("OK")
                instance = wrapper(project_name)
                instance.process(args.command)
            else:
                logging.info("Operation cancelled by the user.")
        else:
            logging.error("Can't find project folder !!")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
