import json
import math
import os
import re
import time
from operator import itemgetter

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
            hosted_zone_names: List of hosted zone names.
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
    return sorted(hosted_zone_ids_and_names, key=itemgetter(1))

def get_change_id_for_latest_change_to_hosted_zone(hosted_zone_id: str) -> str:
    """
        Input
            hosted_zone_id: String
        Output
            change_id: String; the Change ID of the most recent CloudTrail 
            ChangeResourceRecordSets event implemented by the octodns-cicd-user
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

def get_change_status_summary(
        hosted_zone_name: str,
        hosted_zone_id: str,
        change_id: str
    ) -> str:
    service = Route53Service()
    change_info = service.get_change_status(change_id=change_id)
    summary = (
        f"\nCHANGE STATUS for HZ NAME: {hosted_zone_name}" +
        f"\nHZ ID: {hosted_zone_id}" +
        f"\nCHANGE ID: {change_id}" +
        f"\nCHANGE STATUS: {change_info.get('ChangeInfo').get('Status')}"
    )
    return summary

def is_change_insync(change_id: str) -> bool:
    service = Route53Service()
    change_info = service.get_change_status(change_id=change_id)
    change_status = change_info.get('ChangeInfo').get('Status')
    if change_status == "INSYNC":
        return True

def main(
        hosted_zone_changed_files: str,
        wait_time_seconds: int,
        max_time_seconds: int
    ) -> list:
    """
        Input
            hosted_zone_changed_files: String of hosted zone files changed in the
            PR, deliminated by space.
            wait_time_seconds: Interval of time to wait in seconds between checking
            if the change is insync
            max_time_seconds: Maximum total seconds to keep checking for the change
            to be insync.
        Output
            List of change status summaries to be passed to Slack notification action
            to post in channel.
    """
    assert (max_time_seconds <= 120), \
        f"The max_time_seconds ({max_time_seconds}) is not less than or equal to 120."

    assert (wait_time_seconds <= max_time_seconds), \
        f"The wait_time_seconds ({wait_time_seconds}) is not less than or equal \
    to the max_time_seconds ({max_time_seconds})."

    wait_time_max_iterations = int(math.ceil(max_time_seconds / wait_time_seconds))
    hosted_zone_names = get_hosted_zone_names_from_changed_files(
        hosted_zone_changed_files
    )
    hosted_zone_ids_and_names = get_hosted_zone_ids_from_names(
        hosted_zone_names
    )

    change_status_summaries = ""
    for hosted_zone_id_and_name in hosted_zone_ids_and_names:
        hosted_zone_id, hosted_zone_name = hosted_zone_id_and_name
        change_id = get_change_id_for_latest_change_to_hosted_zone(
            hosted_zone_id=hosted_zone_id
        )
        count = 0
        change_insync = is_change_insync(change_id=change_id)
        while not change_insync and count < wait_time_max_iterations:
            time.sleep(wait_time_seconds)
            count += 1
            change_insync = is_change_insync(change_id=change_id)

        summary = get_change_status_summary(
            hosted_zone_name=hosted_zone_name,
            hosted_zone_id=hosted_zone_id,
            change_id=change_id
        )

        change_status_summaries += summary

    return [change_status_summaries]

if __name__ == "__main__":
    output = main(
        hosted_zone_changed_files=hosted_zone_changed_files,
        wait_time_seconds=15,
        max_time_seconds=60
    )
    env_file = os.getenv("GITHUB_ENV")
    with open(env_file, "a", encoding="utf8") as f:
        f.write(f"CHANGE_STATUS_OUTPUT={output}\n")
