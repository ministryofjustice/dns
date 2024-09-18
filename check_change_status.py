import json
import os
import re

from providers.route53 import Route53Service
from services.cloudtrail_service import CloudTrailService

hosted_zone_changed_files = os.getenv("hosted_zone_changed_files")

def is_hosted_zone_filepath(filepath: str) -> bool:
    pattern = re.compile(r"^hostedzones\/[a-zA-Z0-9_\.]*(\.yml|\.yaml)$")
    if pattern.match(filepath):
        return True

def get_hosted_zone_names_from_changed_files(hosted_zone_changed_files: str) -> list:
    """
        Input
            hosted_zone_changed_files: String of one or more file names from the 
            hostedzones directory, expects the form hostedzones/*.yaml. Converts 
            to a list then strips the first twelve characters and the file extension
            and dot, leaving just the hosted zone name.
        Output
            hosted_zone_names: List of one or more hosted zone names.
    """
    hosted_zone_filepaths = [path for path in hosted_zone_changed_files.split(" ")]

    hosted_zone_names = []
    for path in hosted_zone_filepaths:
        if is_hosted_zone_filepath(filepath=path):
            hosted_zone_names.append(path[12:path.rfind(".")])

    return hosted_zone_names

def get_hosted_zone_ids_from_names(hosted_zone_names: list) -> list:
    """
    Input
        hosted_zone_names: List of hosted zone names.
    Output
        hosted_zone_ids_and_names: List of tuples with format (hz_id, hz_name)
        where the hosted zone ID is just the ID, eg Z1GDM6HEODZI69 with 
        the prefix /hostedzone/Z1GDM6HEODZI69 stripped.
    """
    service = Route53Service()
    aws_zones = service.get_aws_zones()
    hosted_zone_ids_and_names = [
        (t[0][12:], t[1]) for t in aws_zones if t[1] in hosted_zone_names
    ]
    # Does not handle the hosted zone name being absent
    return hosted_zone_ids_and_names

def get_change_id_for_latest_change_to_hosted_zone(hosted_zone_id: str) -> str:
    """
        Input
            hosted_zone_id: String
        Output
            change_id: String; the Change ID of the most recent CloudTrail 
            Change Resource Record Sets event implemented by the octodns-cicd-user
            bot account, with valid Resources, for the given Hosted Zone ID.
    """
    service = CloudTrailService()
    response = service.get_latest_n_change_resource_record_sets(n=5)

    matching_events = []
    for event in response["Events"]:
        if event["Username"] == "octodns-cicd-user" and event["Resources"] and event["Resources"][0]["ResourceName"] == hosted_zone_id:
            matching_events.append(event)

    # First matching event is the most recent
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

    change_status_summaries = ""
    for hosted_zone_id_and_name in hosted_zone_ids_and_names:
        change_id = get_change_id_for_latest_change_to_hosted_zone(
            hosted_zone_id=hosted_zone_id_and_name[0]
        )

        service = Route53Service()
        change_status = service.get_change_status(change_id=change_id)

        summary = (
            f"\nCHANGE STATUS for HZ NAME: {hosted_zone_id_and_name[1]}" +
            f"\nHZ ID: {hosted_zone_id_and_name[0]}" +
            f"\nCHANGE ID: {change_id}" +
            f"\nCHANGE STATUS: {change_status.get('ChangeInfo').get('Status')}"
        )
        change_status_summaries += summary

    return [change_status_summaries]

if __name__ == "__main__":
    output = main()
    env_file = os.getenv("GITHUB_ENV")
    with open(env_file, "a", encoding="utf8") as f:
        f.write(f"CHANGE_STATUS_OUTPUT={output}\n")
    main()
