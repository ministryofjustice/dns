import sys

import boto3


def get_registrant_contact():
    return {
        "FirstName": "Steve",
        "LastName": "Marshall",
        "ContactType": "PERSON",
        "OrganizationName": "Ministry of Justice",
        "AddressLine1": "102 Petty France",
        "City": "London",
        "CountryCode": "GB",
        "ZipCode": "SW1H 9AJ",
        "Email": "domains@digital.justice.gov.uk",
        "PhoneNumber": "+44.2033343555",
        "ExtraParams": [{"Name": "UK_CONTACT_TYPE", "Value": "GOV"}],
    }


def get_existing_domains(client):
    domains = []
    paginator = client.get_paginator("list_domains")
    for page in paginator.paginate():
        domains.extend([domain["DomainName"] for domain in page["Domains"]])
    return domains


def check_and_register_domain(client, domain, registrant):
    print(f"Checking domain: {domain}")

    # Check if domain is available
    response = client.check_domain_availability(DomainName=domain)

    if response["Availability"] == "AVAILABLE":
        print(f"{domain} is available, registering")
        try:
            client.register_domain(
                DomainName=domain,
                DurationInYears=1,
                AdminContact=registrant,
                RegistrantContact=registrant,
                TechContact=registrant,
            )
            print(f"Successfully registered {domain}")
        except Exception as e:
            print(f"Failed to register {domain}: {str(e)}")
    else:
        print(f"{domain} is not available")


def main(domains):
    client = boto3.client("route53domains", region_name="us-east-1")
    registrant = get_registrant_contact()
    existing_domains = get_existing_domains(client)

    for domain in domains:
        if domain in existing_domains:
            print(f"{domain} is already registered")
            continue

        check_and_register_domain(client, domain, registrant)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py domain1.com domain2.com ...")
        sys.exit(1)

    domains = sys.argv[1:]
    main(domains)
