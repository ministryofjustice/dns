import os
import sys
import uuid

from providers.route53 import Route53Service


def set_output(name, value):
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            print(f"{name}={value}", file=fh)


def set_multiline_output(name, value):
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            delimiter = uuid.uuid1()
            print(f"{name}<<{delimiter}", file=fh)
            print(value, file=fh)
            print(delimiter, file=fh)


def github_actions_output(output, exit_code):
    set_multiline_output("result", output)
    set_output("exit_code", str(exit_code))

    print(output)
    sys.exit(exit_code)


def main():
    client = Route53Service()
    zones = client.get_aws_zones()

    empty_zones = [
        zone.rstrip(".") for zone_id, zone in zones if client.is_zone_empty(zone_id)
    ]

    if empty_zones:
        output = "The following zones are empty:\n"
        output += "\n".join(f"  - {zone}" for zone in empty_zones)
        return output, 1
    else:
        output = "No empty zones found."
        return output, 0


if __name__ == "__main__":
    output, exit_code = main()
    github_actions_output(output, exit_code)
