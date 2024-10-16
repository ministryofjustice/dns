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
    found_any = False

    if isinstance(data, dict):
        keys_to_remove = []
        for key, value in data.items():
            if "sectigo" in str(value).lower():
                keys_to_remove.append(key)
                found_any = True
            else:
                _, changed = find_and_remove_sectigo_block(value, key)
                found_any = found_any or changed
        for key in keys_to_remove:
            del data[key]

    elif isinstance(data, list):
        items_to_remove = []
        for i, item in enumerate(data):
            _, changed = find_and_remove_sectigo_block(item, parent_key)
            if changed:
                items_to_remove.append(i)
                found_any = True
        for i in reversed(items_to_remove):
            data.pop(i)

    return parent_key, found_any


def process_yaml_file(file_path):
    """Process the given YAML file, removing 'sectigo' blocks if present."""
    with open(file_path, "r") as file:
        try:
            yaml_data = yaml.load(file)
            _, changed = find_and_remove_sectigo_block(yaml_data)
            if changed:
                print(f"File: {file_path}")
                print("Removed one or more blocks containing 'sectigo'.")
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
