import os
import sys

import boto3


def get_aws_zones():
    route53 = boto3.client("route53")
    zones = []
    paginator = route53.get_paginator("list_hosted_zones")
    for page in paginator.paginate():
        for zone in page["HostedZones"]:
            zones.append(zone["Name"].rstrip("."))  # Remove trailing dot
    return set(zones)


def get_config_zones():
    zones_dir = "hostedzones"
    config_zones = []
    for filename in os.listdir(zones_dir):
        if filename.endswith(".yaml"):
            config_zones.append(filename[:-5])  # Remove .yaml extension
    return set(config_zones)


def main():
    aws_zones = get_aws_zones()
    config_zones = get_config_zones()

    unmanaged_zones = aws_zones - config_zones

    if unmanaged_zones:
        print("The following zones exist in AWS but are not managed by octoDNS:")
        for zone in sorted(unmanaged_zones):
            print(f"  - {zone}")
        sys.exit(1)
    else:
        print("All AWS Route53 zones are managed by octoDNS.")
        sys.exit(0)


if __name__ == "__main__":
    main()
