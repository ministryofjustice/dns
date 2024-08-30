import os
import sys

from providers.route53 import Route53Service

env_file = os.getenv("GITHUB_ENV")

def main():
    # service = Route53Service()
    # print(service.get_aws_zones())
    with open(env_file, "a", encoding="utf-8") as f:
        lines = [line.rstrip() for line in file]
    
    print(lines)

if __name__ == "__main__":
    main()
