import os
import sys

from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True  # Preserve quotes around values if present
yaml.width = 4096  # Set the line width to 4096 to avoid line wrapping
yaml.indent(
    mapping=2, sequence=4, offset=2
)  # Set the indentation for mapping and sequence
yaml.explicit_start = True  # Always start the YAML document with '---'


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
            yaml_data = yaml.load(file)
            result, changed = find_and_remove_sectigo_block(yaml_data)
            if changed:
                print(f"File: {file_path}")
                print(f"Removed block containing 'sectigo': {result}")
                with open(file_path, "w") as outfile:
                    yaml.dump(yaml_data, outfile)
                return True
            return False
        except Exception as e:
            print(f"Error processing YAML file {file_path}: {e}")
            return False


def main():
    hostedzones_dir = "hostedzones"

    if not os.path.exists(hostedzones_dir):
        print("Error: The 'hostedzones' directory does not exist")
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
        print("Changes were made. GitHub Action will handle creating/updating PR.")
    else:
        print("No blocks containing 'sectigo' found in any of the YAML files.")


if __name__ == "__main__":
    main()
