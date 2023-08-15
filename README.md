# Cloud-stack POC

This is a simple proof-of-concept for a cloud stack in AWS, that includes a containerized application running in a EC2 instance accessible through API Gateway and Network Load Balancer.

Additionally, a CI/CD script pushes changes to the backend when a change is pushed to the application repository.

## Summary

This solution includes bootstrap, provision and deployment for a simple AWS infrastructure that allows a webserver to run while being accessible via HTTP from the internet.

Although the webserver has public internet access, it's not directly accessible via HTTP from the internet, instead it uses API Gateway along with a Network Load Balancer as a proxy to route the requests targeting the `/hello` resource.

The webserver itself is a docker container with nginx that responds with "world" to the resource `/hello`. The repository for that application is located in the [`hello-webserver`](./hello-webserver) directory.

This solution includes a simple script representing a CI/CD pipeline, that checks for new changes in the [`hello-webserver`](./hello-webserver) repository and pushes the new changes to the backend if any.

## Prerequisites

- Install python and pip: https://www.python.org/downloads/

- Install python libraries:
    ```
    pip install -r requirements.txt
    ```

- Run [`generate_ssh_key.py`](./generate_ssh_key.py) script to generate SSH key pair and process [`cloudformation/hello-webserver-stack.yml.j2`](./cloudformation/hello-webserver-stack.yml.j2) template:

    ```
    python generate_ssh_key.py
    ```

- Copy AWS credentials template, rename to `aws_credentials.json` and replace placeholders with actual secrets:

    ```
    cp ./.credentials/aws_credentials.json.template ./.credentials/aws_credentials.json
    ```

## Bootstrapping

To bootstrap the AWS infrastructure, first add your credentials in the [`aws_credentials.json`](.credentials/aws_credentials.json) file located in the `.credentials` directory.

Saving keys in plain text is not the best practice, but as always, it's an inverse proportion relation between security and convenience. For this purpose, a plain-text json file will work fine.

Then, run the script [`aws_bootstrap.py`](./aws_bootstrap.py):

```bash
python aws_bootstrap.py --template-path cloudformation/hello-webserver-stack.yml --stack-name hello-webserver-stack-test
```
This script will create the cloudformation stack in the selected region.

Refer to the script's documentation for other use cases.

Once the script finished successfully, add manually the created instance's public IP into the ansible hosts inventory file: [`hosts/test.ini`](./hosts/test.ini).


## Provision

Provision the EC2 instance:

```bash
ansible-playbook hello-webserver-provision.yml -i hosts/test.ini -vv
```

This playbook will install required dependencies on the host.


## Deploy

Deploy the docker container to the instance:

```bash
ansible-playbook hello-webserver-deploy.yml -i hosts/test.ini --extra-vars "hello_webserver_root=$(pwd)/hello-webserver" -vv
```

This playbook will update the image's dockerfile, re-build it and run it on the host.

To deploy automatically after any change is pushed to the image's repository, run the script [`hello_webserver_deploy_changes.py`](./hello_webserver_deploy_changes.py):

```bash
python hello_webserver_deploy_changes.py --git-repo-root $(pwd)/hello-webserver --environment test
```

This script will pull changes every 30 seconds and execute the [`hello-webserver-deploy.yml`](`hello-webserver-deploy.yml) playbook if there are any new changes.
The best setup for this script is on a service that executes it on startup on a command-and-control machine.
