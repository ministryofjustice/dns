import os
import sys

from providers.route53 import Route53Facade


def get_config_zones() -> list:
    zones_dir = "hostedzones"
    config_zones = []
    for filename in os.listdir(zones_dir):
        if filename.endswith(".yaml"):
            config_zones.append(filename[:-5])  # Remove .yaml extension
    return config_zones


def github_actions_output(output, exit_code):
    print(output)
    os.environ["GITHUB_OUTPUT"] = output
    sys.exit(exit_code)


def main():
    client = Route53Facade()
    aws_zones = [zone[1] for zone in client.get_aws_zones()]
    config_zones = get_config_zones()

    unmanaged_zones = set(aws_zones) - set(config_zones)
    if unmanaged_zones:
        output = "The following zones exist in AWS but are not managed by octoDNS:\n"
        output += "\n".join(f"  - {zone}" for zone in sorted(unmanaged_zones))
        return output, 1
    else:
        output = "All AWS Route53 zones are managed by octoDNS."
        return output, 0


if __name__ == "__main__":
    output, exit_code = main()
    github_actions_output(output, exit_code)
