import subprocess

from pathlib import Path
from jinja2 import Template

SSH_GEN_DIR = "~/.ssh"
SCRIPT_DIR = Path(__file__).parent.as_posix()

def generate_ssh_key(key_name: str) -> (Path, Path):
    """
    Generate new SSH key pair of ed25519 format

    params:
        key_name (str): identificator for the generated key

    returns: touple (str, str): private and public generated key paths
    """
    Path(SSH_GEN_DIR).expanduser().mkdir(parents=True, exist_ok=True, mode=0o700)

    key_path = Path(SSH_GEN_DIR, key_name)
    pub_key_path = Path(SSH_GEN_DIR, key_name + ".pub")

    if key_path.exists():
        raise FileExistsError(f"Attempted to generate already existing key: {key_path}")

    command = f"ssh-keygen -q -t ed25519 -f {key_path} -N '' -C '{key_name}'"

    subprocess.run(command, check=True)
    print(f"Generated key pair {key_path}, {pub_key_path}")

    return key_path, pub_key_path


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


if __name__ == "__main__":
    key_name = "hello-webserver-key"

    _, pub_key_path = generate_ssh_key(key_name)

    template_path = Path(SCRIPT_DIR, "cloudformation", "hello-webserver-stack.yml.j2").as_posix()
    output_path = template_path.removesuffix(".j2")

    with open(pub_key_path, "r") as pub_key:
        process_jinja_template(path=template_path, output=output_path, pub_key=pub_key.read())
