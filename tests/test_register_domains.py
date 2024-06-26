import unittest
from unittest.mock import MagicMock, patch

from register_domains import (
    check_and_register_domain,
    get_existing_domains,
    get_registrant_contact,
    main,
)


class TestDomainRegistration(unittest.TestCase):
    def test_get_registrant_contact(self):
        contact = get_registrant_contact()
        self.assertEqual(contact["FirstName"], "Steve")
        self.assertEqual(contact["LastName"], "Marshall")
        self.assertEqual(contact["OrganizationName"], "Ministry of Justice")

    @patch("boto3.client")
    def test_get_existing_domains(self, mock_boto_client):
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {
                "Domains": [
                    {"DomainName": "example1.com"},
                    {"DomainName": "example2.com"},
                ]
            },
            {"Domains": [{"DomainName": "example3.com"}]},
        ]
        mock_client = MagicMock()
        mock_client.get_paginator.return_value = mock_paginator
        mock_boto_client.return_value = mock_client

        domains = get_existing_domains(mock_client)
        self.assertEqual(domains, ["example1.com", "example2.com", "example3.com"])

    @patch("register_domains.print")
    def test_check_and_register_available_domain(self, mock_print):
        mock_client = MagicMock()
        mock_client.check_domain_availability.return_value = {
            "Availability": "AVAILABLE"
        }
        domain = "available-domain.com"
        check_and_register_domain(mock_client, domain, get_registrant_contact())
        calls = [
            unittest.mock.call(f"Checking domain: {domain}"),
            unittest.mock.call(f"{domain} is available, registering"),
            unittest.mock.call(f"Successfully registered {domain}"),
        ]
        mock_print.assert_has_calls(calls)
        mock_client.register_domain.assert_called_once()

    @patch("register_domains.print")
    def test_check_unavailable_domain(self, mock_print):
        mock_client = MagicMock()
        mock_client.check_domain_availability.return_value = {
            "Availability": "UNAVAILABLE"
        }
        domain = "unavailable-domain.com"
        check_and_register_domain(mock_client, domain, get_registrant_contact())
        calls = [
            unittest.mock.call(f"Checking domain: {domain}"),
            unittest.mock.call(f"{domain} is not available"),
        ]
        mock_print.assert_has_calls(calls)
        mock_client.register_domain.assert_not_called()

    @patch("register_domains.boto3.client")
    @patch("register_domains.get_existing_domains")
    @patch("register_domains.check_and_register_domain")
    def test_main(
        self, mock_check_and_register, mock_get_existing_domains, mock_boto_client
    ):
        mock_get_existing_domains.return_value = ["existing.com"]
        main(["new.com", "existing.com"])
        mock_check_and_register.assert_called_once_with(
            unittest.mock.ANY, "new.com", unittest.mock.ANY
        )


if __name__ == "__main__":
    unittest.main()
