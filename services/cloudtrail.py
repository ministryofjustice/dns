import boto3

class CloudTrailService:
    def __init__(self):
        self.client = boto3.client("cloudtrail")