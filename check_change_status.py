import os
import sys

from providers.route53 import Route53Service

hosted_zone_changed_files = os.getenv("hosted_zone_changed_files")

# Strip hostedzones/ from prefix and .yaml from suffix
# hosted_zone_names = [path[12:-5] for path in hosted_zone_changed_files.split(" ")]

hosted_zone_names = []
for path in hosted_zone_changed_files:
    if path[-5:] == ".yaml":
        hosted_zone_names.append(path[12:-5])
    elif path[-4:] == ".yml":
        hosted_zone_names.append(path[12:-4])
    else:
        print("not a yml or a yaml!!!")


def main():
    # # service = Route53Service()
    # # print(service.get_aws_zones())

    print(hosted_zone_changed_files)
    print(hosted_zone_names)

if __name__ == "__main__":
    main()
