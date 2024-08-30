import os
import sys

from providers.route53 import Route53Service

hosted_zone_changed_files = os.getenv("hosted_zone_changed_files")

hosted_zone_names = [name[12:-5] for name in hosted_zone_changed_files.split(" ")]

def main():
    # # service = Route53Service()
    # # print(service.get_aws_zones())
    # with open(env_file, "r", encoding="utf-8") as f:
    #     content = f.readlines()

    print(hosted_zone_changed_files)
    print(hosted_zone_names)

if __name__ == "__main__":
    main()
