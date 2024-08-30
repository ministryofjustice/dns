import os
import sys

from providers.route53 import Route53Service

hosted_zone_changed_files = os.getenv("hosted_zone_changed_files")

def main():
    # # service = Route53Service()
    # # print(service.get_aws_zones())
    # with open(env_file, "r", encoding="utf-8") as f:
    #     content = f.readlines()

    print(hosted_zone_changed_files)

if __name__ == "__main__":
    main()
