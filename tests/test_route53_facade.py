import unittest
from unittest.mock import patch

from providers.route53 import Route53Facade


class TestRoute53Facade(unittest.TestCase):
    @patch("providers.route53.boto3")
    def setUp(self, mock_boto3):
        self.mock_boto3 = mock_boto3
        self.route53 = Route53Facade()

    def test_get_aws_zones_successfully(self):
        self.mock_boto3.client().get_paginator().paginate.return_value = [
            {"HostedZones": [{"Id": "zone_id", "Name": "example.com."}]}
        ]
        zones = self.route53.get_aws_zones()

        self.assertEqual(zones, {("zone_id", "example.com")})


if __name__ == "__main__":
    unittest.main()
