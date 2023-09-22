import ansible_runner


def deploy_infrastructure():
    playbook_path = "./ansible/playbooks/infra.yml"
    private_data_dir = "./ansible" 

    result = ansible_runner.run(
        private_data_dir=private_data_dir,
        playbook=playbook_path,
        cmdline="--tags terraform_apply",
    )

    if result.status == "successful":
        print("Deployment was successful!")
    else:
        print("Deployment encountered an error!")
        print("Reason:", result.stderr)


def destroy_segments():
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


if __name__ == "__main__":
    action = input("Enter action (deploy/destroy): ").strip().lower()
    if action == "destroy":
        destroy_segments()
    elif action == "deploy":
        pass
    else:
        print("No valid action selected")
