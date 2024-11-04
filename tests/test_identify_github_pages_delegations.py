import unittest

from bin.identify_github_pages_delegations import format_output, process_record


class TestGithubPagesFunctions(unittest.TestCase):

    def test_format_output_with_record(self):
        result = format_output("www", "service.justice.gov.uk")
        self.assertEqual(result, "www.service.justice.gov.uk")

    def test_format_output_without_record(self):
        result = format_output("", "service.justice.gov.uk")
        self.assertEqual(result, "service.justice.gov.uk")

    def test_process_record_cname(self):
        records = []
        hostedzone = "service.justice.gov.uk"
        record_name = "www"
        record = {"type": "CNAME", "value": "username.github.io"}
        process_record(records, hostedzone, record_name, record)
        self.assertIn("www.service.justice.gov.uk", records)

    def test_process_record_a(self):
        records = []
        hostedzone = "service.justice.gov.uk"
        record_name = "example"
        record = {"type": "A", "values": ["185.199.108.153"]}
        process_record(records, hostedzone, record_name, record)
        self.assertIn("example.service.justice.gov.uk", records)

    def test_process_record_a_no_match(self):
        records = []
        hostedzone = "service.justice.gov.uk"
        record_name = "example"
        record = {"type": "A", "values": ["192.0.2.1"]}  # Not a GitHub Pages IP
        process_record(records, hostedzone, record_name, record)
        self.assertNotIn("example.service.justice.gov.uk", records)

    def test_process_record_aaaa(self):
        records = []
        hostedzone = "service.justice.gov.uk"
        record_name = "example"
        record = {"type": "AAAA", "values": ["2606:50c0:8000::153"]}
        process_record(records, hostedzone, record_name, record)
        self.assertIn("example.service.justice.gov.uk", records)

    def test_process_record_alias(self):
        records = []
        hostedzone = "service.justice.gov.uk"
        record_name = "aliasrecord"
        record = {"type": "ALIAS", "value": "USERNAME.github.io"}
        process_record(records, hostedzone, record_name, record)
        self.assertIn("aliasrecord.service.justice.gov.uk", records)


if __name__ == "__main__":
    unittest.main()
