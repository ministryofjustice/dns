import os

import yaml

GITHUB_PAGES_IPS = [
    "185.199.108.153",
    "185.199.109.153",
    "185.199.110.153",
    "185.199.111.153",
]
GITHUB_PAGES_AAAA_IPS = [
    "2606:50c0:8000::153",
    "2606:50c0:8001::153",
    "2606:50c0:8002::153",
    "2606:50c0:8003::153",
]
GITHUB_PAGES_URL_PATTERNS = [
    ".github.io",
    ".githubusercontent.com",
]


def find_github_pages_records(directory):
    github_pages_records = []

    for filename in os.listdir(directory):
        if filename.endswith(".yaml"):
            hostedzone = filename[:-5]
            filepath = os.path.join(directory, filename)

            with open(filepath, "r") as file:
                try:
                    records = yaml.safe_load(file)
                    for record_name, record in records.items():
                        if isinstance(record, list):
                            for sub_record in record:
                                process_record(
                                    github_pages_records,
                                    hostedzone,
                                    record_name,
                                    sub_record,
                                )
                        elif isinstance(record, dict):
                            process_record(
                                github_pages_records, hostedzone, record_name, record
                            )

                except yaml.YAMLError as e:
                    print(f"Error parsing {filepath}: {e}")

    return github_pages_records


def process_record(github_pages_records, hostedzone, record_name, record):
    if record.get("type") == "CNAME" and any(
        url in record.get("value", "") for url in GITHUB_PAGES_URL_PATTERNS
    ):
        github_pages_records.append(format_output(record_name, hostedzone))
    elif record.get("type") == "A":
        record_values = record.get("values", [])
        for ip in GITHUB_PAGES_IPS:
            if ip in record_values:
                github_pages_records.append(format_output(record_name, hostedzone))
                break
    elif record.get("type") == "AAAA":
        record_values = record.get("values", [])
        for ip in GITHUB_PAGES_AAAA_IPS:
            if ip in record_values:
                github_pages_records.append(format_output(record_name, hostedzone))
                break
    elif record.get("type") in ["ALIAS", "ANAME"] and (
        record.get("value") in ["USERNAME.github.io", "ORGANIZATION.github.io"]
    ):
        github_pages_records.append(format_output(record_name, hostedzone))


def format_output(record_name, hostedzone):
    # Format the output based on whether the record name is empty
    if record_name.strip():
        return f"{record_name}.{hostedzone}"
    else:
        return hostedzone


def write_github_pages_records(records, output_file):
    with open(output_file, "w") as file:
        for record in records:
            file.write(f"{record}\n")


def main():
    hostedzones_directory = "./hostedzones"
    output_file = ".github_pages"

    github_pages_records = find_github_pages_records(hostedzones_directory)
    write_github_pages_records(github_pages_records, output_file)


if __name__ == "__main__":
    main()
