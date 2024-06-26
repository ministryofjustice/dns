import sys

import boto3


def get_aws_zones():
    route53 = boto3.client("route53")
    zones = []
    paginator = route53.get_paginator("list_hosted_zones")
    for page in paginator.paginate():
        for zone in page["HostedZones"]:
            zones.append((zone["Id"], zone["Name"]))
    return zones


def is_zone_empty(zone_id):
    route53 = boto3.client("route53")
    paginator = route53.get_paginator("list_resource_record_sets")
    for page in paginator.paginate(HostedZoneId=zone_id):
        for record_set in page["ResourceRecordSets"]:
            # Ignore NS and SOA records as they are default
            if record_set["Type"] not in ["NS", "SOA"]:
                return False
    return True


def main():
    print("Checking for empty hosted zones...")
    empty_zones = []
    for zone_id, zone_name in get_aws_zones():
        if is_zone_empty(zone_id):
            # Remove trailing dot from zone name
            empty_zones.append(zone_name.rstrip("."))

    if empty_zones:
        print("The following hosted zones are empty:")
        for zone in empty_zones:
            print(f"  - {zone}")
        sys.exit(1)
    else:
        print("No empty hosted zones found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
