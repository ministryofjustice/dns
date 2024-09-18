import unittest
from unittest.mock import MagicMock, Mock, patch

# from providers.route53 import Route53Service

from check_change_status import (
    is_hosted_zone_filepath,
    get_hosted_zone_names_from_changed_files,
    get_hosted_zone_ids_from_names,
    get_change_id_for_latest_change_to_hosted_zone,
    main
  )


class TestIsHostedZoneFilepath(unittest.TestCase):

    def test_true_hosted_zone_yaml_filepath(self):
        result = is_hosted_zone_filepath("hostedzones/good.name.yaml")
        self.assertTrue(result)

    def test_true_hosted_zone_yml_filepath(self):
        result = is_hosted_zone_filepath("hostedzones/good.name.yml")
        self.assertTrue(result)

    def test_false_hosted_zone_non_yaml_filepath(self):
        result = is_hosted_zone_filepath("hostedzones/bad.file.path.txt")
        self.assertFalse(result)

    def test_false_hosted_zone_filepath_wrong_directory(self):
        result = is_hosted_zone_filepath("baddirectory/bad.directory.name.yaml")
        self.assertFalse(result)

    def test_false_hosted_zone_filepath_sub_directory(self):
        result = is_hosted_zone_filepath("hostedzones/subdir/bad.subdir.yaml")
        self.assertFalse(result)


class TestGetHostedZoneNamesFromChangedFiles(unittest.TestCase):

    def test_valid_hosted_zone_paths(self):
        result = get_hosted_zone_names_from_changed_files(
            "hostedzones/good.name.com.yaml hostedzones/good.name.uk.yml"
        )
        self.assertEqual(result, ["good.name.com", "good.name.uk"])

    def test_invalid_directory(self):
        result = get_hosted_zone_names_from_changed_files(
            "hostedzones/subdir/bad.subdir.com.yaml wrongdirectory/bad.dir.uk.yml"
        )
        self.assertEqual(result, [])

    def test_invalid_file_extension(self):
        result = get_hosted_zone_names_from_changed_files(
            "hostedzones/bad.file.ext.txt"
        )
        self.assertEqual(result, [])

class TestGetHostedZoneIdsFromNames(unittest.TestCase):
    @patch("check_change_status.Route53Service")
    def test_get_ids_from_names_successfully(self, mock_route53):
        mock_route53.return_value.get_aws_zones.return_value = {
            ("/hostedzone/Z1GDM6HEODZI69", "example1.com"),
            ("/hostedzone/Z1GDM6HEODZI70", "example2.com"),
            ("/hostedzone/Z1GDM6HEODZI71", "example3.com")
        }
        result = get_hosted_zone_ids_from_names(
            hosted_zone_names=["example1.com", "example2.com"]
        )
        self.assertEqual(
            set(result),
            set([
                ("Z1GDM6HEODZI69", "example1.com"),
                ("Z1GDM6HEODZI70", "example2.com")
            ])
        )

class TestGetChangeIdForLatestChangeToHostedZone(unittest.TestCase):
    @patch("check_change_status.CloudTrailService")
    def test_get_change_id_successfully(self, mock_cloud_trail):
        mock_cloud_trail.return_value.get_latest_n_change_resource_record_sets.return_value = {
            "Events": [
                {
                    "EventId": "event1-id",
                    "EventName": "ChangeResourceRecordSets",
                    "Username": "octodns-cicd-user",
                    "Resources": [
                        {
                            "ResourceType": "AWS::Route53::HostedZone",
                            "ResourceName": "Z1QLRMQEXOI5G4"                            
                        }
                    ],
                    "CloudTrailEvent": '{\"eventVersion\":\"1.10\",\"userIdentity\":{\"type\":\"IAMUser\",\"principalId\":\"AIDA42CZXXJSJFQ3QSI6G\",\"arn\":\"arn:aws:iam::880656497252:user/octodns-cicd-user\",\"accountId\":\"880656497252\",\"accessKeyId\":\"A
KIA42CZXXJSLENF66FF\",\"userName\":\"octodns-cicd-user\"},\"eventTime\":\"2024-09-17T13:57:28Z\",\"eventSource\":\"route53.amazonaws.com\",\"eventName\":\"ChangeResourceRecordSets\",\"awsRegion\":\"us-east-1\",\"sourceIPAddress\":\"20.172.46.70\",\"us
erAgent\":\"Boto3/1.34.99 md/Botocore#1.34.162 ua/2.0 os/linux#6.5.0-1025-azure md/arch#x86_64 lang/python#3.11.9 md/pyimpl#CPython cfg/retry-mode#legacy Botocore/1.34.162\",\"requestParameters\":{\"hostedZoneId\":\"Z2BAIDDV5DBDJR\",\"changeBatch\":{\
"comment\":\"Change: edb7df9afc8a47e49a21e929c0c203ac\",\"changes\":[{\"action\":\"UPSERT\",\"resourceRecordSet\":{\"name\":\"jaama._domainkey.justice.gov.uk.\",\"type\":\"TXT\",\"tTL\":300,\"resourceRecords\":[{\"value\":\"\\\"v=DKIM1; k=rsa; p=MIGfM
A0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCtZJY6Zx60GV9lIDjdeeu6qGU6/MhFSu2gvAyXo0LUzFiVMG0y1E1S1HCQh0exXOwzqh+G4IyjZieeeGWdVcgITAsMRGDfc+kQM8Mmw6USAiNzfHEf4vjUYkzg+a5AI3BzUPpzNgHDwvM1j2jtUO76NwEKgtP0Wg4bRCNZBzqtfQIDAQAB\\\"\"}]}}]}},\"responseElements\":{\"ch
angeInfo\":{\"id\":\"/change/C01161813QZNEIGXF3I2C\",\"status\":\"PENDING\",\"submittedAt\":\"Sep 17, 2024 1:57:28 PM\",\"comment\":\"Change: edb7df9afc8a47e49a21e929c0c203ac\"}},\"additionalEventData\":{\"Note\":\"Do not use to reconstruct hosted zon
e\"},\"requestID\":\"ee5520ea-c959-4c6a-b93a-bf4b63c8d3d3\",\"eventID\":\"b7b54dda-9e08-43bf-81e9-495ec79b2391\",\"readOnly\":false,\"eventType\":\"AwsApiCall\",\"apiVersion\":\"2013-04-01\",\"managementEvent\":true,\"recipientAccountId\":\"8806564972
52\",\"eventCategory\":\"Management\",\"tlsDetails\":{\"tlsVersion\":\"TLSv1.3\",\"cipherSuite\":\"TLS_AES_128_GCM_SHA256\",\"clientProvidedHostHeader\":\"route53.amazonaws.com\"}}'
                },
                {

                },
                {

                }
            ]
        }
