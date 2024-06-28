import os

import boto3


class Route53Facade:
    def __init__(self):
        self.client = boto3.client("route53")

    def get_aws_zones(self) -> set:
        paginator = self.client.get_paginator("list_hosted_zones")
        return set(
            {
                (zone["Id"], zone["Name"].rstrip("."))
                for page in paginator.paginate()
                for zone in page["HostedZones"]
            }
        )

    def is_zone_empty(self, zone_id: str) -> bool:
        paginator = self.client.get_paginator("list_resource_record_sets")
        for page in paginator.paginate(HostedZoneId=zone_id):
            for record_set in page["ResourceRecordSets"]:
                # Ignore NS and SOA records as they are default
                if record_set["Type"] not in ["NS", "SOA"]:
                    return False
        return True

    def get_config_zones(self) -> set:
        zones_dir = "hostedzones"
        return set(
            [
                filename[:-5]  # Remove .yaml extension
                for filename in os.listdir(zones_dir)
                if filename.endswith(".yaml")
            ]
        )
