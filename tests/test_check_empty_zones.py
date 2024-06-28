import unittest
from unittest.mock import MagicMock, patch

from check_empty_zones import main


class TestMainFunction(unittest.TestCase):
    @patch("check_empty_zones.Route53Facade")
    def test_main_with_empty_zones(self, MockRoute53Facade):
        mock_facade = MockRoute53Facade.return_value
        mock_facade.get_aws_zones.return_value = [("id1", "zone1."), ("id2", "zone2.")]
        mock_facade.is_zone_empty.side_effect = [True, False]

        expected_output = "The following zones are empty:\n  - zone1"
        expected_status = 1

        output, status = main()

        self.assertEqual(output, expected_output)
        self.assertEqual(status, expected_status)

    @patch("check_empty_zones.Route53Facade")
    def test_main_with_no_empty_zones(self, MockRoute53Facade):
        mock_facade = MockRoute53Facade.return_value
        mock_facade.get_aws_zones.return_value = [("id1", "zone1."), ("id2", "zone2.")]
        mock_facade.is_zone_empty.return_value = False

        expected_output = "No empty zones found."
        expected_status = 0

        output, status = main()

        self.assertEqual(output, expected_output)
        self.assertEqual(status, expected_status)


if __name__ == "__main__":
    unittest.main()
