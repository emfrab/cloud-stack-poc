"""
This script pulls new changes from origin in hello-webserver.git repository, and if there's a new commit it runs
the hello-webserver-deploy.yml playbook.

That process is repeated every 30 seconds.

Prerequisites:
    * pip install GitPython

Examples executing this script:
    python hello_webserver_deploy_changes.py
    python3 hello_webserver_deploy_changes.py --git-repo-root /path/to/hello-webserver --environment test
"""
import git
import time
import argparse
import subprocess

from pathlib import Path


PLAYBOOK_NAME = "hello-webserver-deploy.yml"
SCRIPT_ROOT = Path(__file__).parent.as_posix()


def pull_changes(git_dir: str) -> git.Commit:
    """
    Pull changes from repository

    params:
        git_dir (str): path to the git repository

    returns: git.Commit - latest commit
    """
    repo = git.Repo(git_dir)
    repo.remote("origin").pull()
    return next(repo.iter_commits())


def push_changes_to_backend(git_dir: str, environment: str):
    """
    Run ansible playbook to push changes to backend

    params:
        git_dir (str): path to the git repository
        environment (str): identifier for the ansible host inventory file
    """
    command = f'ansible-playbook {PLAYBOOK_NAME} -i hosts/{environment}.ini -e "hello_webserver_root={git_dir}" -vv'
    subprocess.run(command, check=True, shell=True)


def deploy(git_dir: str, environment: str):
    """
    Main function. Goes over an infinite loop looking for new commits every 30 seconds

    params:
        git_dir (str): path to the git repository
        environment (str): identifier for the ansible host inventory file
    """
    latest_commit_epoch = 0

    while True:
        last_commit = pull_changes(git_dir)

        if last_commit.committed_date > latest_commit_epoch:
            latest_commit_epoch = last_commit.committed_date
            push_changes_to_backend(git_dir, environment)
        else:
            print("No new commits")

        time.sleep(30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--git-repo-root", type=str,
                        help="Path for git repository. Default: <script_dir>/hello-webserver",
                        default=Path(SCRIPT_ROOT, "hello-webserver").as_posix())
    parser.add_argument("--environment", type=str,
                        help="Targeting environment (test, prod)",
                        default="test")
    args = parser.parse_args()

    deploy(args.git_repo_root, args.environment)
