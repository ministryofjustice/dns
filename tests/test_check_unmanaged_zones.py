import unittest
from unittest.mock import patch

from bin.check_unmanaged_zones import get_config_zones, main


class TestMainFunction(unittest.TestCase):
    @patch("check_unmanaged_zones.Route53Service")
    def test_unmanaged_zones(self, mock_route53):
        mock_route53.return_value.get_aws_zones.return_value = [
            ("zone1", "zone1"),
            ("zone2", "zone2"),
        ]
        with patch("check_unmanaged_zones.get_config_zones", return_value=["zone1"]):
            output, code = main()
            self.assertEqual(code, 1)
            self.assertIn("zone2", output)

    @patch("check_unmanaged_zones.Route53Service")
    def test_all_zones_managed(self, mock_route53):
        mock_route53.return_value.get_aws_zones.return_value = [
            ("zone1", "zone1"),
            ("zone2", "zone2"),
        ]
        with patch(
            "check_unmanaged_zones.get_config_zones", return_value=["zone1", "zone2"]
        ):
            output, code = main()
            self.assertEqual(code, 0)
            self.assertIn("All AWS Route53 zones are managed by octoDNS.", output)


class TestGetConfigZones(unittest.TestCase):
    @patch("os.listdir")
    def test_get_config_zones(self, mock_listdir):
        mock_listdir.return_value = ["zone1.yaml", "zone2.yaml", "not_a_zone.txt"]

        expected_zones = ["zone1", "zone2"]
        actual_zones = get_config_zones()

        self.assertEqual(actual_zones, expected_zones)


if __name__ == "__main__":
    unittest.main()
