import os
import sys

from providers.route53 import Route53Service

hosted_zone_changed_files = os.getenv("hosted_zone_changed_files")

# Strip prefix (12 characters of hostedzones/) and suffix (everythng from the last "." inclusive)
hosted_zone_names = [path[12:path.rfind(".")] for path in hosted_zone_changed_files.split(" ")]

def main():
    # # service = Route53Service()
    # # print(service.get_aws_zones())

    print(hosted_zone_changed_files)
    print(hosted_zone_names)

if __name__ == "__main__":
    main()
