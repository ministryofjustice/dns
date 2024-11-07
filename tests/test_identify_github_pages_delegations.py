import unittest
from unittest.mock import patch

from bin.identify_github_pages_delegations import (
    find_github_pages_records,
    format_output,
    process_hostedzone_records,
    process_record_generator,
)


class TestGithubPagesFunctions(unittest.TestCase):
    def test_format_output_with_record(self):
        result = format_output("www", "service.justice.gov.uk")
        self.assertEqual(result, "www.service.justice.gov.uk")

    def test_format_output_without_record(self):
        result = format_output("", "service.justice.gov.uk")
        self.assertEqual(result, "service.justice.gov.uk")

    def test_process_record_generator_cname(self):
        hostedzone = "service.justice.gov.uk"
        record_name = "www"
        record = {"type": "CNAME", "value": "username.github.io"}
        results = list(process_record_generator(hostedzone, record_name, record))
        self.assertIn("www.service.justice.gov.uk", results)

    def test_process_record_generator_a(self):
        hostedzone = "service.justice.gov.uk"
        record_name = "example"
        record = {"type": "A", "values": ["185.199.108.153"]}
        results = list(process_record_generator(hostedzone, record_name, record))
        self.assertIn("example.service.justice.gov.uk", results)

    def test_process_record_generator_a_no_match(self):
        hostedzone = "service.justice.gov.uk"
        record_name = "example"
        record = {"type": "A", "values": ["192.0.2.1"]}  # Not a GitHub Pages IP
        results = list(process_record_generator(hostedzone, record_name, record))
        self.assertNotIn("example.service.justice.gov.uk", results)

    def test_process_record_generator_aaaa(self):
        hostedzone = "service.justice.gov.uk"
        record_name = "example"
        record = {"type": "AAAA", "values": ["2606:50c0:8000::153"]}
        results = list(process_record_generator(hostedzone, record_name, record))
        self.assertIn("example.service.justice.gov.uk", results)

    def test_process_record_generator_alias(self):
        hostedzone = "service.justice.gov.uk"
        record_name = "aliasrecord"
        record = {"type": "ALIAS", "value": "ministryofjustice.github.io"}
        results = list(process_record_generator(hostedzone, record_name, record))
        self.assertIn("aliasrecord.service.justice.gov.uk", results)

    def test_process_hostedzone_records(self):
        hostedzone = "service.justice.gov.uk"
        records = {
            "www": {"type": "CNAME", "value": "ministryofjustice.github.io"},
            "example": {"type": "A", "values": ["185.199.108.153"]},
        }
        results = list(process_hostedzone_records(hostedzone, records))
        self.assertIn("www.service.justice.gov.uk", results)
        self.assertIn("example.service.justice.gov.uk", results)

    @patch("os.scandir")
    def test_find_github_pages_records_empty(self, mock_scandir):
        mock_scandir.return_value = []
        results = list(find_github_pages_records("mocked_directory"))
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
