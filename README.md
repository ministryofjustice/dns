# dns

This repo currently contains dumps of the existing `dsd.io` and
`justice.gov.uk` hosted zones, as well as tools for bulk-registration of
domains and managing our defensive domains estate (for which this
repository is the source of truth, and will override changes made in Route53).

It uses [OctoDNS](https://github.com/github/octodns) for the bulk of
its interactions with our DNS provider (Route53).

## `dsd.io` and `justice.gov.uk` dumps

Exported with octodns to the `output/` folder in this repo. See upstream docs for details on usage.

The simplest way to dump a single zone is:
```
octodns-dump --config-file config/mojdsd.yaml --lenient --output-dir output/ <zone-name> route53
```

## Domain registration

To register a batch of domains, call the `register-domains.sh` script like this:

```bash
$ ./script/register-domains.sh first-domain.com second-domain.net third-domain.org
```

It will use your existing AWS CLI credentials, and register the domains
in your default account. For the moment, there is no way to change this,
so if registering domains, please ensure you're using `mojdsd` as your
default account, as that's where we currently keep our domains.

## Defensive domain management

We have hundreds of defensively-registered domains, and need to [apply
the same DNS
records](https://ministryofjustice.github.io/security-guidance/guides/de
fensive-domain-registration/) to all of them. Unfortunately, at the
time of writing, [OctoDNS doesn't support applying records to multiple
zones](https://github.com/github/octodns/issues/7), so we're using
[Make](https://www.gnu.org/software/make/manual/make.html) to automate
generation of OctoDNS config for each domain.

This repository's code is the source of truth for our defensive domain
config, and the list of repos *should* be complete.

### Managing defensive domain DNS config

All our defensive domains are listed in `defensive-domains/domains.mk`,
as a single `$DEFENSIVE_DOMAINS` variable that contains a
whitespace-separated string which Make can then use to generate separate
OctoDNS config files for each of them (output to
`defensive-domains/config/<domain>.yaml`), based on the OctoDNS config
template in `defensive-domains/dns.tmpl.yaml`. This config is not dynamic
at present, as all the DNS records should be identical, and don't depend
on the domain names in any way.

These config files are only generated when Make needs them to carry out
some other action you specify.

### Updating defensive domain DNS records

If you update the list of defensive domains, or the OctoDNS config
template, you can validate your changes:

```bash
$ make defensive-domains-validate
# Prints nothing and returns 0 if everything is valid
```

Once you're happy with your changes, you can test them without applying them:

```bash
$ make defensive-domains-noop
```

And, once you're confident that they're good to be deployed, you can apply them:

```bash
$ make defensive-domains-apply
```
