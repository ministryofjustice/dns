import os
import sys

from providers.route53 import Route53Service

hosted_zone_changed_files = os.getenv("hosted_zone_changed_files")

def get_hosted_zone_names_from_changed_files(hosted_zone_changed_files: list) -> list:
    hosted_zone_names = [
        path[12:path.rfind(".")] for path in hosted_zone_changed_files.split(" ")
        ]
    return hosted_zone_names

def get_hosted_zone_ids_from_names(hosted_zone_names: list) -> list:
    service = Route53Service()
    aws_zones = service.get_aws_zones()
    hosted_zone_ids = [t[0][12:] for t in aws_zones if t[1] in hosted_zone_names]
    return hosted_zone_ids

def main():

    print(hosted_zone_changed_files)
    hosted_zone_names = get_hosted_zone_names_from_changed_files(
        hosted_zone_changed_files
    )
    print(hosted_zone_names)

    hosted_zone_ids = get_hosted_zone_ids_from_names(
        hosted_zone_names
    )
    print(hosted_zone_ids)
if __name__ == "__main__":
    main()

# sifocc.org.uk
# govfsl.com
# yjb.gov.uk

# hosted_zone_changed_files='hostedzones/sifocc.org.uk.yaml hostedzones/govfsl.com.yml hostedzones/yjb.gov.uk.yaml'