from datetime import datetime

import boto3
from botocore.exceptions import ClientError

class CloudTrailService:
    def __init__(self) -> None:
        self.client = boto3.client("cloudtrail", region_name="us-east-1")

    def get_latest_n_change_resource_record_sets(self, n:int) -> list:
        response = self.client.lookup_events(
            LookupAttributes=[
                {
                    "AttributeKey": "EventName",
                    "AttributeValue": "ChangeResourceRecordSets"
                },
            ],
            MaxResults=n,
        )

        return response
