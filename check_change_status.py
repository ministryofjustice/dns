import json
import os

from providers.route53 import Route53Service
from services.cloudtrail_service import CloudTrailService

hosted_zone_changed_files = os.getenv("hosted_zone_changed_files")

def get_hosted_zone_names_from_changed_files(hosted_zone_changed_files: list) -> list:
    hosted_zone_names = [
        path[12:path.rfind(".")] for path in hosted_zone_changed_files.split(" ")
        ]
    return hosted_zone_names

def get_hosted_zone_ids_from_names(hosted_zone_names: list) -> list:
    service = Route53Service()
    aws_zones = service.get_aws_zones()
    hosted_zone_ids_and_names = [(t[0][12:], t[1]) for t in aws_zones if t[1] in hosted_zone_names]

    return hosted_zone_ids_and_names

def get_change_id_for_latest_change_to_hosted_zone(hosted_zone_id: str) -> str:
    service = CloudTrailService()
    response = service.get_latest_n_change_resource_record_sets(n=5)

    # Filter for octodns instigated ChangeResourceRecordSets events only
    # and non-empty Resources matching ResourceName
    matching_events = []
    for event in response["Events"]:
        if event["Username"] == "octodns-cicd-user" and event["Resources"] and event["Resources"][0]["ResourceName"] == hosted_zone_id:
            matching_events.append(event)

    # First matching event is the most recent
    # The CloudTrailEvent section is JSON
    first_matching_cloud_trail_event = json.loads(matching_events[0]["CloudTrailEvent"])
    change_id = first_matching_cloud_trail_event.get("responseElements").get("changeInfo").get("id")
    
    return change_id


def main():

    hosted_zone_names = get_hosted_zone_names_from_changed_files(
        hosted_zone_changed_files
    )

    hosted_zone_ids_and_names = get_hosted_zone_ids_from_names(
        hosted_zone_names
    )

    for hosted_zone_id_and_name in hosted_zone_ids_and_names:
        change_id = get_change_id_for_latest_change_to_hosted_zone(
            hosted_zone_id=hosted_zone_id_and_name[0]
        )

        service = Route53Service()
        change_status = service.get_change_status(change_id=change_id)
        print(f"\nCHANGE STATUS for HZ NAME: {hosted_zone_id_and_name[1]}, HZ ID: {hosted_zone_id_and_name[0]}, CHANGE ID: {change_id}")
        print(f"{change_status}")

if __name__ == "__main__":
    main()
