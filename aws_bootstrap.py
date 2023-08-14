"""
Script to bootstrap resources on AWS using Cloudformation. It creates a stack on the targeted region and waits for its success status.

Prerequisites:
    * pip install boto3

Examples executing this script:
    python aws_bootstrap.py --template-path cloudformation/my-template.yml
    python3 aws_bootstrap.py --region us-east-2 --template-path cloudformation/my-template.yml --stack-name my-stack
"""
import json
import boto3
import argparse

from pathlib import Path

from botocore.exceptions import WaiterError


SCRIPT_ROOT = Path(__file__).parent.as_posix()


def create_stack(session: boto3.Session, template_path: str, stack_name: str = None):
    """
    Create cloudformation stack in region eu-central-1

    params:
        session (boto3.Session): AWS Session
        template_path (str): Path to the cloudflormation template
        stack_name (str): Optional - Name for the cloudformation stack

    returns: str - the created stack's ID
    """
    if stack_name is None:
        stack_name = Path(template_path).name.split(".")[0]

    # Read the CloudFormation template from file
    with open(template_path, "r") as f:
        template_body = f.read()

    # Create a CloudFormation client with the session
    cf_client = session.client("cloudformation")

    # Create the CloudFormation stack
    response = cf_client.create_stack(StackName=stack_name,
                                      TemplateBody=template_body,
                                      Capabilities=["CAPABILITY_IAM"])

    print(f"Created stack with ID: {response['StackId']}")

    return response


def wait_for_stack_completion(session: boto3.Session, stack_id: str):
    """
    Wait for stack completion. Raises error if stack is not completed successfully.

    params:
        session (boto3.Session): AWS Session
        stack_id (str): Stack ID to wait for

    Raises botocore.exceptions.WaiterError
    """
    cf = session.client("cloudformation")
    print("Wait for stack creation to complete...")
    try:
        waiter = cf.get_waiter("stack_create_complete")
        waiter.wait(StackName=stack_id)
        print("Stack creation completed successfully!")
    except WaiterError:
        print("Stack creation failed")
        raise


def bootstrap(region: str, cfn_template_path: str, stack_name: str = None):
    """
    Script's main function

    params:
        region (str): AWS region to create a session for
        cfn_template_path (str): Relative or absolute path for Cloudformation template
        stack_name (str): Optional - name for the cloudformation stack
    """
    # Create a boto3 session
    with open(Path(SCRIPT_ROOT, ".credentials/aws_credentials.json"), "r") as credentials_file:
        credentials = json.load(credentials_file)
        session = boto3.Session(region_name=region, **credentials)

    response = create_stack(session=session, template_path=cfn_template_path, stack_name=stack_name)
    wait_for_stack_completion(session=session, stack_id=response["StackId"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", type=str,
                        help="AWS Region to target. Default: eu-central-1",
                        default="eu-central-1")
    parser.add_argument("--template-path", type=str,
                        help="Path to cloudformation template to bootstrap",
                        required=True)
    parser.add_argument("--stack-name", type=str,
                        help="Stack name to allocate in AWS. Default: template's filename (without extensions)",
                        required=False)

    args = parser.parse_args()

    bootstrap(region=args.region, cfn_template_path=args.template_path, stack_name=args.stack_name)
