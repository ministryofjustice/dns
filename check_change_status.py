import os
import sys

from providers.route53 import Route53Service

def main():
    service = Route53Service()
    print(service.get_aws_zones())


if __name__ == "__main__":
    main()
