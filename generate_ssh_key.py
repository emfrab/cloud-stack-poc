"""
Script to generate ssh key pair and process template in ./cloudformation/hello-webserver-stack.yml.j2

Examples running this script:
  python generate_ssh_key.py
  python3 generate_ssh_key.py --force
"""
import argparse
import subprocess

from pathlib import Path
from jinja2 import Template

SSH_GEN_DIR = "~/.ssh"
SCRIPT_DIR = Path(__file__).parent.as_posix()


def generate_ssh_key(key_name: str, force: bool = False) -> (Path, Path):
    """
    Generate new SSH key pair of ed25519 format

    params:
        key_name (str): identificator for the generated key
        force (bool): override key if it already exists. Default: False

    returns: tuple (str, str): private and public generated key paths
    """
    Path(SSH_GEN_DIR).expanduser().mkdir(parents=True, exist_ok=True, mode=0o700)

    key_path = Path(SSH_GEN_DIR, key_name).expanduser()
    pub_key_path = Path(SSH_GEN_DIR, key_name + ".pub").expanduser()

    check_key_exists(key_path, delete=force)
    check_key_exists(pub_key_path, delete=force)

    command = f"ssh-keygen -q -t ed25519 -f {key_path} -N '' -C '{key_name}'"
    subprocess.run(command.split(), stderr=subprocess.STDOUT, check=True)

    key_path.chmod(0o600)
    pub_key_path.chmod(0o600)

    print(f"Generated key pair {key_path}, {pub_key_path}")

    return key_path, pub_key_path


def check_key_exists(path: Path, delete: bool = False):
    """
    Check if a key already exists

    params:
        path (pathlib.Path): Path object for the key
        delete (bool): delete the key if exists. Default: False

    raises FileExistsError
    """
    if path.exists():
        if delete:
            path.unlink()
            return

        raise FileExistsError(f"Attempted to generate already existing key: {path}")


def process_jinja_template(path: str, output: str = None, **kwargs) -> str:
    """
    Process a Jinja template replacing variables with keyword arguments provided

    params:
        path (str): path to template
        output (str): Optional - file path to output to
        **kwargs: keyword arguments to replace jinja variables with

    returns: str - processed template
    """
    with open(path, "r", encoding="utf-8") as in_file:
        template = Template(in_file.read())
        processed_template = template.render(**kwargs)

    if output:
        with open(output, "w", encoding="utf-8") as out_file:
            out_file.write(processed_template)

    return processed_template


def main(force: bool = False):
    ssh_key_name = "hello-webserver-key"

    _, public_key_path = generate_ssh_key(ssh_key_name, force)

    template_path = Path(SCRIPT_DIR, "cloudformation", "hello-webserver-stack.yml.j2").as_posix()
    output_path = template_path.removesuffix(".j2")

    with open(public_key_path, "r") as pub_key:
        process_jinja_template(path=template_path, output=output_path, pub_key=pub_key.read().strip())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Override key and processed template if they already exist.")

    args = parser.parse_args()

    main(args.force)
