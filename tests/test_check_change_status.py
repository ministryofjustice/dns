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
    def test_get_latest_change_id_for_hz_id_successfully(self, mock_cloud_trail):
        mock_cloud_trail.return_value.get_latest_n_change_resource_record_sets.return_value = {
            "Events": [
                {
                    "EventId": "event-id-1",
                    "EventName": "ChangeResourceRecordSets",
                    "Username": "octodns-cicd-user",
                    "Resources": [
                        {
                            "ResourceType": "AWS::Route53::HostedZone",
                            "ResourceName": "hosted-zone-id-123"                            
                        }
                    ],
                        "CloudTrailEvent": "{\"responseElements\":{\"changeInfo\":{\"id\":\"/change/change-id-1\"}}}"
                },
                {
                    "EventId": "event-id-2",
                    "EventName": "ChangeResourceRecordSets",
                    "Username": "octodns-cicd-user",
                    "Resources": [
                        {
                            "ResourceType": "AWS::Route53::HostedZone",
                            "ResourceName": "hosted-zone-id-123"                            
                        }
                    ],
                        "CloudTrailEvent": "{\"responseElements\":{\"changeInfo\":{\"id\":\"/change/change-id-2\"}}}"
                }
            ]
        }
        result = get_change_id_for_latest_change_to_hosted_zone("hosted-zone-id-123")
        self.assertEqual(result, "/change/change-id-1")

    @patch("check_change_status.CloudTrailService")
    def test_event_with_empty_resources_ignored(self, mock_cloud_trail):
        mock_cloud_trail.return_value.get_latest_n_change_resource_record_sets.return_value = {
            "Events": [
                {
                    "EventId": "event-id-1",
                    "EventName": "ChangeResourceRecordSets",
                    "Username": "octodns-cicd-user",
                    "Resources": [],
                        "CloudTrailEvent": "{\"responseElements\":{\"changeInfo\":{\"id\":\"/change/change-id-1\"}}}"
                },
                {
                    "EventId": "event-id-2",
                    "EventName": "ChangeResourceRecordSets",
                    "Username": "octodns-cicd-user",
                    "Resources": [
                        {
                            "ResourceType": "AWS::Route53::HostedZone",
                            "ResourceName": "hosted-zone-id-123"                            
                        }
                    ],
                        "CloudTrailEvent": "{\"responseElements\":{\"changeInfo\":{\"id\":\"/change/change-id-2\"}}}"
                }
            ]
        }
        result = get_change_id_for_latest_change_to_hosted_zone("hosted-zone-id-123")
        self.assertEqual(result, "/change/change-id-2")

    @patch("check_change_status.CloudTrailService")
    def test_event_with_non_matching_hz_id_ignored(self, mock_cloud_trail):
        mock_cloud_trail.return_value.get_latest_n_change_resource_record_sets.return_value = {
            "Events": [
                {
                    "EventId": "event-id-1",
                    "EventName": "ChangeResourceRecordSets",
                    "Username": "octodns-cicd-user",
                    "Resources": [
                        {
                            "ResourceType": "AWS::Route53::HostedZone",
                            "ResourceName": "hosted-zone-id-123"                            
                        }
                    ],
                        "CloudTrailEvent": "{\"responseElements\":{\"changeInfo\":{\"id\":\"/change/change-id-1\"}}}"
                },
                {
                    "EventId": "event-id-2",
                    "EventName": "ChangeResourceRecordSets",
                    "Username": "octodns-cicd-user",
                    "Resources": [
                        {
                            "ResourceType": "AWS::Route53::HostedZone",
                            "ResourceName": "hosted-zone-id-456"                            
                        }
                    ],
                        "CloudTrailEvent": "{\"responseElements\":{\"changeInfo\":{\"id\":\"/change/change-id-2\"}}}"
                }
            ]
        }
        result = get_change_id_for_latest_change_to_hosted_zone("hosted-zone-id-456")
        self.assertEqual(result, "/change/change-id-2")


class TestMainFunction(unittest.TestCase):
    @patch("check_change_status.get_hosted_zone_names_from_changed_files")
    @patch("check_change_status.Route53Service")
    @patch("check_change_status.CloudTrailService")
    def test_main_returns_expected_summary(
        self,
        mock_get_hosted_zone_names_from_changed_files,
        mock_route53,
        mock_cloud_trail
    ):
        mock_get_hosted_zone_names_from_changed_files.return_value = [
            "example1.com",
            "example3.com"
        ]
        mock_route53.return_value.get_aws_zones.return_value = {
            ("/hostedzone/Z1GDM6HEODZI69", "example1.com"),
            ("/hostedzone/Z1GDM6HEODZI70", "example2.com"),
            ("/hostedzone/Z1GDM6HEODZI71", "example3.com")
        }
        mock_cloud_trail.return_value.get_latest_n_change_resource_record_sets.return_value = {
            "Events": [
                {
                    "EventId": "event-id-1",
                    "EventName": "ChangeResourceRecordSets",
                    "Username": "octodns-cicd-user",
                    "Resources": [
                        {
                            "ResourceType": "AWS::Route53::HostedZone",
                            "ResourceName": "Z1GDM6HEODZI69"                            
                        }
                    ],
                        "CloudTrailEvent": "{\"responseElements\":{\"changeInfo\":{\"id\":\"/change/change-id-69\"}}}"
                },
                {
                    "EventId": "event-id-2",
                    "EventName": "ChangeResourceRecordSets",
                    "Username": "octodns-cicd-user",
                    "Resources": [
                        {
                            "ResourceType": "AWS::Route53::HostedZone",
                            "ResourceName": "Z1GDM6HEODZI71"                            
                        }
                    ],
                        "CloudTrailEvent": "{\"responseElements\":{\"changeInfo\":{\"id\":\"/change/change-id-71\"}}}"
                }
            ]
        }
        result = main()
        expected = ["some stuff"]
        self.assertEqual(result, expected)


