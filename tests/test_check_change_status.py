import unittest
from unittest.mock import patch

from bin.check_change_status import (
    get_change_id_for_latest_change_resource_record_sets_for_hosted_zone,
    get_change_status_summary,
    get_hosted_zone_ids_from_names,
    get_hosted_zone_names_from_changed_files,
    is_change_insync,
    is_hosted_zone_filepath,
    main,
)


class TestIsHostedZoneFilepath(unittest.TestCase):

    def test_true_hosted_zone_yaml_filepath(self):
        result = is_hosted_zone_filepath("hostedzones/GOOD-name.123.yaml")
        self.assertTrue(result)

    def test_true_hosted_zone_yml_filepath(self):
        result = is_hosted_zone_filepath("hostedzones/GOOD-name.123.yml")
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
            ("/hostedzone/hostedzone-id-69", "example1.com"),
            ("/hostedzone/hostedzone-id-70", "example2.com"),
            ("/hostedzone/hostedzone-id-71", "example3.com"),
        }
        result = get_hosted_zone_ids_from_names(
            hosted_zone_names=["example1.com", "example2.com"]
        )
        self.assertEqual(
            set(result),
            set(
                [
                    ("hostedzone-id-69", "example1.com"),
                    ("hostedzone-id-70", "example2.com"),
                ]
            ),
        )


class TestGetChangeIdForLatestChangeResourceRecordSetsForHostedZone(unittest.TestCase):
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
                            "ResourceName": "hosted-zone-id-123",
                        }
                    ],
                    "CloudTrailEvent": '{"responseElements":{"changeInfo":{"id":"/change/change-id-1"}}}',
                },
                {
                    "EventId": "event-id-2",
                    "EventName": "ChangeResourceRecordSets",
                    "Username": "octodns-cicd-user",
                    "Resources": [
                        {
                            "ResourceType": "AWS::Route53::HostedZone",
                            "ResourceName": "hosted-zone-id-123",
                        }
                    ],
                    "CloudTrailEvent": '{"responseElements":{"changeInfo":{"id":"/change/change-id-2"}}}',
                },
            ]
        }
        result = get_change_id_for_latest_change_resource_record_sets_for_hosted_zone(
            hosted_zone_id="hosted-zone-id-123", username="octodns-cicd-user"
        )
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
                    "CloudTrailEvent": '{"responseElements":{"changeInfo":{"id":"/change/change-id-1"}}}',
                },
                {
                    "EventId": "event-id-2",
                    "EventName": "ChangeResourceRecordSets",
                    "Username": "octodns-cicd-user",
                    "Resources": [
                        {
                            "ResourceType": "AWS::Route53::HostedZone",
                            "ResourceName": "hosted-zone-id-123",
                        }
                    ],
                    "CloudTrailEvent": '{"responseElements":{"changeInfo":{"id":"/change/change-id-2"}}}',
                },
            ]
        }
        result = get_change_id_for_latest_change_resource_record_sets_for_hosted_zone(
            hosted_zone_id="hosted-zone-id-123", username="octodns-cicd-user"
        )
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
                            "ResourceName": "hosted-zone-id-123",
                        }
                    ],
                    "CloudTrailEvent": '{"responseElements":{"changeInfo":{"id":"/change/change-id-1"}}}',
                },
                {
                    "EventId": "event-id-2",
                    "EventName": "ChangeResourceRecordSets",
                    "Username": "octodns-cicd-user",
                    "Resources": [
                        {
                            "ResourceType": "AWS::Route53::HostedZone",
                            "ResourceName": "hosted-zone-id-456",
                        }
                    ],
                    "CloudTrailEvent": '{"responseElements":{"changeInfo":{"id":"/change/change-id-2"}}}',
                },
            ]
        }
        result = get_change_id_for_latest_change_resource_record_sets_for_hosted_zone(
            hosted_zone_id="hosted-zone-id-456", username="octodns-cicd-user"
        )
        self.assertEqual(result, "/change/change-id-2")


class TestGetChangeStatusSummary(unittest.TestCase):
    @patch("check_change_status.Route53Service")
    def test_get_change_status_summary_successfully(self, mock_route53):

        mock_route53.return_value.get_change_status.return_value = {
            "ChangeInfo": {
                "Id": "/change/change-id-69",
                "Status": "INSYNC",
                "SubmittedAt": "2024-09-17T13:57:28.692000+00:00",
                "Comment": "Change: edbac",
            }
        }

        result = get_change_status_summary(
            hosted_zone_name="example1.com",
            hosted_zone_id="example1-hz-id",
            change_id="/change/change-id-69",
        )
        expected = (
            "\nCHANGE STATUS for HZ NAME: example1.com"
            + "\nHZ ID: example1-hz-id"
            + "\nCHANGE ID: /change/change-id-69"
            + "\nCHANGE STATUS: INSYNC\n"
        )
        self.assertEqual(result, expected)


class TestIsChangeInsync(unittest.TestCase):
    @patch("check_change_status.Route53Service")
    def test_change_insync(self, mock_route53):
        mock_route53.return_value.get_change_status.return_value = {
            "ChangeInfo": {
                "Id": "/change/change-id-69",
                "Status": "INSYNC",
                "SubmittedAt": "2024-09-17T13:57:28.692000+00:00",
                "Comment": "Change: edbac",
            }
        }
        result = is_change_insync(change_id="/change/change-id-69")
        self.assertTrue(result)

    @patch("check_change_status.Route53Service")
    def test_change_not_insync(self, mock_route53):
        mock_route53.return_value.get_change_status.return_value = {
            "ChangeInfo": {
                "Id": "/change/change-id-69",
                "Status": "PENDING",
                "SubmittedAt": "2024-09-17T13:57:28.692000+00:00",
                "Comment": "Change: edbac",
            }
        }
        result = is_change_insync(change_id="/change/change-id-69")
        self.assertFalse(result)


class TestMainFunction(unittest.TestCase):
    @patch("check_change_status.CloudTrailService")
    @patch("check_change_status.Route53Service")
    def test_main_returns_expected_summary(self, mock_route53, mock_cloud_trail):

        mock_route53.return_value.get_aws_zones.return_value = {
            ("/hostedzone/hostedzone-id-69", "example1.com"),
            ("/hostedzone/hostedzone-id-70", "example2.com"),
            ("/hostedzone/hostedzone-id-71", "example3.com"),
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
                            "ResourceName": "hostedzone-id-69",
                        }
                    ],
                    "CloudTrailEvent": '{"responseElements":{"changeInfo":{"id":"/change/change-id-69"}}}',
                },
                {
                    "EventId": "event-id-2",
                    "EventName": "ChangeResourceRecordSets",
                    "Username": "octodns-cicd-user",
                    "Resources": [
                        {
                            "ResourceType": "AWS::Route53::HostedZone",
                            "ResourceName": "hostedzone-id-71",
                        }
                    ],
                    "CloudTrailEvent": '{"responseElements":{"changeInfo":{"id":"/change/change-id-71"}}}',
                },
            ]
        }
        mock_route53.return_value.get_change_status.side_effect = [
            {"ChangeInfo": {"Id": "/change/change-id-69", "Status": "INSYNC"}},
            {"ChangeInfo": {"Id": "/change/change-id-69", "Status": "INSYNC"}},
            {"ChangeInfo": {"Id": "/change/change-id-71", "Status": "PENDING"}},
            {"ChangeInfo": {"Id": "/change/change-id-71", "Status": "PENDING"}},
            {"ChangeInfo": {"Id": "/change/change-id-71", "Status": "INSYNC"}},
            {"ChangeInfo": {"Id": "/change/change-id-71", "Status": "INSYNC"}},
        ]
        result = main(
            hosted_zone_changed_files="hostedzones/example1.com.yaml hostedzones/example3.com.yml",
            wait_time_seconds=1,
            max_time_seconds=2,
        )
        expected = [
            (
                "\n"
                + "CHANGE STATUS for HZ NAME: example1.com\n"
                + "HZ ID: hostedzone-id-69\n"
                + "CHANGE ID: /change/change-id-69\n"
                + "CHANGE STATUS: INSYNC\n"
                + "\n"
                + "CHANGE STATUS for HZ NAME: example3.com\n"
                + "HZ ID: hostedzone-id-71\n"
                + "CHANGE ID: /change/change-id-71\n"
                + "CHANGE STATUS: INSYNC\n"
            )
        ]
        self.assertEqual(result, expected)
