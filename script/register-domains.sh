#!/usr/bin/env bash

domains=("$@")
registrant="FirstName=Steve,LastName=Marshall,ContactType=PUBLIC_BODY,OrganizationName=Ministry of Justice,AddressLine1=102 Petty France,City=London,CountryCode=GB,ZipCode=SW1H 9AJ,Email=domains@digital.justice.gov.uk,PhoneNumber=+44.2033343555,ExtraParams=[{Name=UK_CONTACT_TYPE,Value=GOV}]"

existing_domains=$(aws route53domains list-domains --region us-east-1 | jq -r '.Domains[] .DomainName')

for domain in "${domains[@]}"; do
  if [[ ${existing_domains[*]} =~ ${domain} ]]; then
    echo "$domain is already registered"
    continue
  fi

  availability=$(aws route53domains check-domain-availability \
    --domain-name "$domain" --region us-east-1 \
    | jq -r '.Availability')
  if [[ 'AVAILABLE' == "$availability" ]]; then
    echo "$domain is available, registering"
    aws route53domains register-domain \
      --region us-east-1 \
      --domain-name "$domain"  --duration-in-years 1 \
      --admin-contact "$registrant" \
      --registrant-contact "$registrant" \
      --tech-contact "$registrant"
  else
    echo "$domain is not available"
  fi
done
