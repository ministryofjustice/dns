import os

import yaml

github_pages_ips = [
    "185.199.108.153",
    "185.199.109.153",
    "185.199.110.153",
    "185.199.111.153",
]
github_pages_aaaa_ips = [
    "2606:50c0:8000::153",
    "2606:50c0:8001::153",
    "2606:50c0:8002::153",
    "2606:50c0:8003::153",
]
github_pages_url_patterns = [
    ".github.io",
    ".githubusercontent.com",
]


def find_github_pages_records(directory):
    github_pages_records = []

    # Iterate over all YAML files in the given directory
    for filename in os.listdir(directory):
        if filename.endswith(".yaml"):
            hostedzone = filename[
                :-5
            ]  # Remove the .yaml extension to get the hosted zone name
            filepath = os.path.join(directory, filename)

            # Load the YAML file
            with open(filepath, "r") as file:
                try:
                    records = yaml.safe_load(file)
                    # Iterate over records
                    for record_name, record in records.items():
                        # Handle record list
                        if isinstance(record, list):
                            for sub_record in record:
                                process_record(
                                    github_pages_records,
                                    hostedzone,
                                    record_name,
                                    sub_record,
                                )
                        elif isinstance(record, dict):  # If it's a single record
                            process_record(
                                github_pages_records, hostedzone, record_name, record
                            )

                except yaml.YAMLError as e:
                    print(f"Error parsing {filepath}: {e}")

    return github_pages_records


def process_record(github_pages_records, hostedzone, record_name, record):
    # Check for GitHub Pages CNAME record
    if record.get("type") == "CNAME" and any(
        url in record.get("value", "") for url in github_pages_url_patterns
    ):
        github_pages_records.append(format_output(record_name, hostedzone))
    # Check for A records
    elif record.get("type") == "A":
        # Ensure the value is a list for comparison
        record_values = record.get("values", [])
        for ip in github_pages_ips:
            if ip in record_values:
                github_pages_records.append(format_output(record_name, hostedzone))
                break  # No need to continue checking once a match is found
    # Check for AAAA records
    elif record.get("type") == "AAAA":
        # Ensure the value is a list for comparison
        record_values = record.get("values", [])
        for ip in github_pages_aaaa_ips:
            if ip in record_values:
                github_pages_records.append(format_output(record_name, hostedzone))
                break  # No need to continue checking once a match is found
    # Check for ALIAS or ANAME records
    elif record.get("type") in ["ALIAS", "ANAME"] and (
        record.get("value") in ["USERNAME.github.io", "ORGANIZATION.github.io"]
    ):
        github_pages_records.append(format_output(record_name, hostedzone))


def format_output(record_name, hostedzone):
    # Format the output based on whether the record name is empty
    if record_name.strip():  # Check if record_name is not empty or whitespace
        return f"{record_name}.{hostedzone}"
    else:
        return (
            hostedzone  # Return only the hosted zone name if the record name is empty
        )


def write_github_pages_records(records, output_file):
    with open(output_file, "w") as file:
        for record in records:
            file.write(f"{record}\n")


def main():
    hostedzones_directory = "./hostedzones"  # Adjust the path as necessary
    output_file = ".github_pages"

    # Find GitHub Pages records
    github_pages_records = find_github_pages_records(hostedzones_directory)

    # Write results to the output file
    write_github_pages_records(github_pages_records, output_file)

    print(
        f"Found {len(github_pages_records)} GitHub Pages records. Results saved to {output_file}."
    )


if __name__ == "__main__":
    main()
