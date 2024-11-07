"""
This script processes DNS records to identify and update records related to GitHub Pages.
It scans the configured DNS records and checks for necessary GitHub Pages delegations,
such as CNAME and A records, to ensure that they are correctly configured.

For more information on managing custom domain delegations in GitHub Pages,
refer to the official documentation:
https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site#dns-records-for-your-custom-domain
"""

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
    """Scans a directory for YAML files and yields GitHub Pages DNS records."""
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.endswith(".yaml"):
            hostedzone = os.path.splitext(entry.name)[0]
            filepath = entry.path

            try:
                with open(filepath, "r") as file:
                    records = yaml.safe_load(file) or {}
                    # Process records if they exist
                    yield from process_hostedzone_records(hostedzone, records)
            except yaml.YAMLError as e:
                print(f"Error parsing {filepath}: {e}")


def process_hostedzone_records(hostedzone, records):
    for record_name, record in records.items():
        if isinstance(record, list):
            for sub_record in record:
                yield from process_record_generator(hostedzone, record_name, sub_record)
        elif isinstance(record, dict):
            yield from process_record_generator(hostedzone, record_name, record)


def process_record_generator(hostedzone, record_name, record):
    record_type = record.get("type")
    record_values = record.get("values", [])
    record_value = record.get("value", "")

    if record_type == "CNAME" and any(
        url in record_value for url in GITHUB_PAGES_URL_PATTERNS
    ):
        yield format_output(record_name, hostedzone)
    elif record_type == "A" and any(ip in record_values for ip in GITHUB_PAGES_IPS):
        yield format_output(record_name, hostedzone)
    elif record_type == "AAAA" and any(
        ip in record_values for ip in GITHUB_PAGES_AAAA_IPS
    ):
        yield format_output(record_name, hostedzone)
    elif (
        record_type in ["ALIAS", "ANAME"]
        and record_value == "ministryofjustice.github.io"
    ):
        yield format_output(record_name, hostedzone)


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
