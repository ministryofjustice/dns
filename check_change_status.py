import json
import os

from providers.route53 import Route53Service
from services.cloudtrail_service import CloudTrailService

hosted_zone_changed_files = os.getenv("hosted_zone_changed_files")
slack_token = os.environ.get("ADMIN_SLACK_TOKEN")

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

    # hosted_zone_names = get_hosted_zone_names_from_changed_files(
    #     hosted_zone_changed_files
    # )

    # hosted_zone_ids_and_names = get_hosted_zone_ids_from_names(
    #     hosted_zone_names
    # )

    # change_status_summaries = []
    # for hosted_zone_id_and_name in hosted_zone_ids_and_names:
    #     change_id = get_change_id_for_latest_change_to_hosted_zone(
    #         hosted_zone_id=hosted_zone_id_and_name[0]
    #     )

    #     service = Route53Service()
    #     change_status = service.get_change_status(change_id=change_id)

    #     summary = (
    #         f"\nCHANGE STATUS for HZ NAME: {hosted_zone_id_and_name[1]}" +
    #         f"\nHZ ID: {hosted_zone_id_and_name[0]}" +
    #         f"\nCHANGE ID: {change_id}" +
    #         f"\nCHANGE STATUS: {change_status.get('ChangeInfo').get('Status')}"
    #     )
    #     change_status_summaries.append(summary)
        # print(f"{change_status}")
    # change_status_summaries = "Big cat dog"

    # try list of multiline vars
    change_status_summaries = [
        (
            "\nSummary 1 Line 1" +
            "\nSummary 1 Line 2"
        ),
        (
            "\nSummary 2 Line 1" +
            "\nSummary 2 Line 2"
        )

    ]
    res_list = [
        {"hz_name": "name1", "hz_id": "id1", "change_status": "pending"},
        {"hz_name": "name2", "hz_id": "id2", "change_status": "insync"}

    ]
    change_status_summaries = ""
    for res in res_list:
        summary = f"\nChange Status for HZ: {res.get("hz_name")}\nHZ ID: {res.get("hz_id")}\nCHANGE STATUS: {res.get("change_status")}\n"
        change_status_summaries += summary

    return change_status_summaries

if __name__ == "__main__":
    output = main()
    env_file = os.getenv("GITHUB_ENV")
    with open(env_file, "a", encoding="utf8") as f:
        f.write(f"CHANGE_STATUS_OUTPUT={output}\n")
    main()
