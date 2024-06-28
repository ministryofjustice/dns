import sys

from providers.route53 import Route53Facade


def main():
    client = Route53Facade()
    zones = client.get_aws_zones()

    empty_zones = []
    for zone_id, zone in zones:
        if client.is_zone_empty(zone_id):
            empty_zones.append(zone.rstrip("."))

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
