import os
import sys

import yaml


def find_sectigo_block(data, parent_key=None):
    if isinstance(data, dict):
        for key, value in data.items():
            if "sectigo" in str(value).lower():
                return parent_key or key
            result = find_sectigo_block(value, key)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_sectigo_block(item, parent_key)
            if result:
                return result
    return None


def process_yaml_file(file_path):
    with open(file_path, "r") as file:
        try:
            yaml_data = yaml.safe_load(file)
            result = find_sectigo_block(yaml_data)
            if result:
                print(f"File: {file_path}")
                print(f"The block containing 'sectigo' is: {result}")
                print("Content of the block:")
                print(yaml.dump(yaml_data[result], default_flow_style=False))
                print("-" * 50)
            return result is not None
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {file_path}: {e}")
            return False


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

    sectigo_found = False
    for yaml_file in yaml_files:
        file_path = os.path.join(hostedzones_dir, yaml_file)
        if process_yaml_file(file_path):
            sectigo_found = True

    if not sectigo_found:
        print("No blocks containing 'sectigo' found in any of the YAML files.")


if __name__ == "__main__":
    main()
