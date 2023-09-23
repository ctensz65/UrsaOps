import ansible_runner
import sys
import os
from tqdm import tqdm
import time
import threading
import re


from generate_vars import ansibleVars
from generate_inventory import merge_inventories

BASE_DIR_TERRAFORM = os.path.abspath('../terraform')
BASE_DIR_ANSIBLE = os.path.abspath('../ansible')

class wrapper:
    def __init__(self, project_name):
        self.OUTPUT_INVENTORY = os.path.join(BASE_DIR_ANSIBLE, "inventory/hosts.ini")
        self.project_name = project_name

    def deploy_infrastructure(self):
        playbook_path = "playbooks/infra.yml"

        result = ansible_runner.run(
            private_data_dir=BASE_DIR_ANSIBLE,
            playbook=playbook_path,
            cmdline="--tags terraform_apply",
            extravars = {
                'project_name': self.project_name
            }
        )

        if result.status == "successful":
            print("Deployment was successful!")

            os.makedirs(os.path.dirname(self.OUTPUT_INVENTORY), exist_ok=True)
            merge_inventories(self.project_name, BASE_DIR_TERRAFORM, self.OUTPUT_INVENTORY)
        else:
            print("Deployment encountered an error!")
            error_message = result.stdout

            if isinstance(error_message, str):
                stripped_message = re.sub(r'\x1b\[.*?m', '', error_message)

                print(stripped_message)
            else:
                print("Unexpected type for error_message:", type(error_message))
        
    def destroy_segments(self):
        playbook_path = "./ansible/playbooks/infra.yml"
        private_data_dir = "./" 

        # Run the Ansible playbook
        result = ansible_runner.run(
            private_data_dir=private_data_dir,
            playbook=playbook_path,
            cmdline="--tags terraform_destroy",
        )

        if result.status == "successful":
            print("Segments were successfully destroyed!")
        else:
            print("Destruction process encountered an error!")
            print("Reason:", result.stderr)

def usage():
    print('----------------')
    print('Deploy: python main.py deploy input_file.yaml')
    print('Provisioning: python main.py provisioning')
    print('Destroy: python main.py destroy')
    print('----------------')

def spinner():
    symbols = ['|', '/', '-', '\\']
    idx = 0
    while spin:
        sys.stdout.write('\r' + symbols[idx % len(symbols)])
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.write('\rDone!\n')


if __name__ == "__main__":
    try:
        arg_command = sys.argv[1].strip().lower()
    except IndexError:
        usage()
        sys.exit(1)

    if arg_command == "deploy":
        try:
            input_yaml = sys.argv[2].strip().lower()
            ansible_vars_instance = ansibleVars(input_yaml)

            spin = True
            # spinner_thread = threading.Thread(target=spinner)
            # spinner_thread.start()

            project_name, output = ansible_vars_instance.generate_ansible_vars()

            # spin = False
            # spinner_thread.join()

            print('\nEngagement Name:', project_name)
            print(output)

            # confirmation = input("Does everything look okay? Type 'yes' to continue deploying: ").strip().lower()
            # if confirmation == 'yes':
            #     instance = wrapper(project_name)
            #     instance.deploy_infrastructure()
            # else:
            #     print("Aborting the process.")
        except IndexError:
            print('Input file yaml required!')
    elif arg_command == "destroy":
        wrapper.destroy_segments()
    else:
        usage()
        sys.exit(1)
