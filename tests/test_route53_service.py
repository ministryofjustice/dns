import unittest
from unittest.mock import patch

from providers.route53 import Route53Service


class TestRoute53Service(unittest.TestCase):
    @patch("providers.route53.boto3")
    def setUp(self, mock_boto3):
        self.mock_boto3 = mock_boto3
        self.route53 = Route53Service()

    def test_get_aws_zones_successfully(self):
        self.mock_boto3.client().get_paginator().paginate.return_value = [
            {"HostedZones": [{"Id": "/hostedzone/Z1GDM6HEODZI69", "Name": "example.com."}]},
        ]
        zones = self.route53.get_aws_zones()

        self.assertEqual(zones, {("/hostedzone/Z1GDM6HEODZI69", "example.com")})

    def test_is_zone_empty_is_recognised(self):
        self.mock_boto3.client().get_paginator().paginate.return_value = [
            {
                "ResourceRecordSets": [
                    {"Type": "NS"},
                    {"Type": "SOA"},
                ]
            },
        ]
        is_empty = self.route53.is_zone_empty("zone_id")
        self.assertTrue(is_empty)

    def test_non_empty_zone_isnt_recognised(self):
        self.mock_boto3.client().get_paginator().paginate.return_value = [
            {
                "ResourceRecordSets": [
                    {"Type": "NS"},
                    {"Type": "SOA"},
                    {"Type": "A"},
                ]
            },
        ]
        is_empty = self.route53.is_zone_empty("zone_id")
        self.assertFalse(is_empty)


if __name__ == "__main__":
    unittest.main()
