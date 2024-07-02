import os
import subprocess
import sys

import yaml


def find_and_remove_sectigo_block(data, parent_key=None):
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if "sectigo" in str(value).lower():
                del data[key]
                return parent_key or key, True
            result, changed = find_and_remove_sectigo_block(value, key)
            if changed:
                if isinstance(value, dict) and len(value) == 0:
                    del data[key]
                return result, True
    elif isinstance(data, list):
        for i, item in enumerate(data):
            result, changed = find_and_remove_sectigo_block(item, parent_key)
            if changed:
                data.pop(i)
                return result, True
    return None, False


def process_yaml_file(file_path):
    with open(file_path, "r") as file:
        try:
            yaml_data = yaml.safe_load(file)
            result, changed = find_and_remove_sectigo_block(yaml_data)
            if changed:
                print(f"File: {file_path}")
                print(f"Removed block containing 'sectigo': {result}")
                with open(file_path, "w") as outfile:
                    yaml.dump(yaml_data, outfile, default_flow_style=False)
                return True
            return False
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {file_path}: {e}")
            return False


def run_command(command):
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    output, error = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(f"Error message: {error.decode('utf-8')}")
        sys.exit(1)
    return output.decode("utf-8").strip()


def create_pr():
    branch_name = "remove-sectigo-block"
    run_command(f"git checkout -b {branch_name}")
    run_command("git add .")
    run_command('git commit -m "Remove YAML blocks containing sectigo domain"')
    run_command(f"git push origin {branch_name}")

    # Create PR using GitHub CLI (gh)
    pr_output = run_command(
        f"gh pr create --title 'Remove sectigo blocks' --body 'This PR removes YAML blocks containing the sectigo domain.' --base main --head {branch_name}"
    )
    print(f"PR created: {pr_output}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    hostedzones_dir = os.path.join(script_dir, "hostedzones")

    if not os.path.exists(hostedzones_dir):
        print(f"Error: The 'hostedzones' directory does not exist in {script_dir}")
        sys.exit(1)

    yaml_files = [
        f
        for f in os.listdir(hostedzones_dir)
        if f.endswith(".yaml") or f.endswith(".yml")
    ]

    if not yaml_files:
        print("No YAML files found in the 'hostedzones' directory.")
        sys.exit(1)

    changes_made = False
    for yaml_file in yaml_files:
        file_path = os.path.join(hostedzones_dir, yaml_file)
        if process_yaml_file(file_path):
            changes_made = True

    if changes_made:
        create_pr()
    else:
        print("No blocks containing 'sectigo' found in any of the YAML files.")


if __name__ == "__main__":
    main()
