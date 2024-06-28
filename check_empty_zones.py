import os
import sys

from providers.route53 import Route53Facade


def github_actions_output(output, exit_code):
    print(output)
    os.environ["GITHUB_OUTPUT"] = output
    sys.exit(exit_code)


def main():
    client = Route53Facade()
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
