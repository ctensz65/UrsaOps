
# UrsaOps

🚨 WARNING: URSAOPS REPOSITORY 🚨

This repository, UrsaOps, is currently in an active developmental phase. Its primary purpose is for academic and paper review [IDSECCONF 2023].

Please consider the following before exploring further:

📜 Academic Use: The content here is primarily intended for paper reviewers and academic scrutiny. It may not be complete or suitable for real-world application as of now.

🛠 Under Development: Features, tools, and documentation in this repository are subject to change. Some parts might not be fully functional or optimized.

⚠️ Not Production Ready: Given its developmental nature, it is not advisable to use UrsaOps for any production or real-world scenarios without thorough testing and validation.

🤝 Contribute with Caution: If you wish to contribute, please understand the risks and responsibilities. Ensure that your contributions adhere to ethical guidelines and best practices in security.

🔐 Security: While every effort is made to ensure the safety and effectiveness of UrsaOps, users and contributors are urged to validate and verify any code or tool independently before utilization.

By accessing this repository, you acknowledge the above warnings and use the contents at your own risk.

# Streamlined Red Team Infrastructure Automation

## Project Summary:

**UrsaOps** is a dedicated endeavor aimed at simplifying red teaming exercises. By leveraging Infrastructure as Code (IaC) principles, this project offers a systematic and automated approach to deploying and provisioning a cohesive red team infrastructure.

## Core Objectives:

**Automated Deployment**: Utilize the consistency and repeatability of IaC to efficiently set up the red team environments, reducing potential human errors and inconsistencies.

**Stealth Operations**: Operating with discretion, UrsaOps aims to conduct activities without drawing unnecessary attention.

**Scalability**: Suitable for various scopes, UrsaOps is designed to cater to both compact tasks and broader adversarial simulations.

**Flexibility**: With the ever-evolving threat landscape, our infrastructure is built to adapt and evolve as needed.

**Secure Communication**: UrsaOps emphasizes maintaining encrypted and secure channels, safeguarding the operations' integrity and confidentiality.

## Requirements:
- Terraform: Responsible for the automated provisioning of infrastructure. [Installation Guide](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- Ansible: Used for configuration management and application deployment. [Installation Guide](https://docs.ansible.com/ansible/latest/installation_guide/index.html)
- Python Libraries
```bash
  pip install -r requirements.txt
```








## Usage/Examples
Before executing any of the following steps, ensure you've installed all the Requirements.

- **Set Environment Variable**
  
  Set an environment variable URSAOPS_ROOT pointing to the root directory of your project.
```bash
  export URSAOPS_ROOT="/path/to/UrsaOps"
```
- **Generate Ansible Variables, Terraform Files, & Deploy**

  Generate necessary variables for Ansible configurations based on the given input and initiate the deployment process of the red team infrastructure. You will be prompted to confirm deployment. Enter "y" to continue.
```bash
  python3 main.py deploy operator_input.yml
```
- **Start Provisioning**

  Begin the provisioning process to set up the infrastructure based on the configurations provided.
```bash
  python3 main.py provisioning
```
- **Destroy**

  Clean up and remove the deployed infrastructure.
```bash
  python3 main.py destroy
```


## Features

- Phishing Segment: Tailored modules for crafting and delivering phishing campaigns with efficacy, while ensuring trackability and manageability.

- Command & Control (C2) Segment: A robust and discreet command and control infrastructure, facilitating covert operations and resilient communication with deployed agents.

- Network Segment: Leveraging the power of WireGuard, this segment focuses on establishing secure, flexible, and high-performance VPN tunnels, forming the backbone of operational connectivity.

- SIEM Segment: An integrated Security Information and Event Management solution, offering real-time monitoring, alerting, and analytical capabilities to keep a pulse on all operational activities.


## Acknowledgements

 - [Kuba Gretzky: Evilginx 3](https://github.com/kgretzky/evilginx2)
 - [Jordan Wright: Gophish](https://github.com/gophish/gophish)

