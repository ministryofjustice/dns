include defensive-domains/domains.mk

all:
.PHONY: all

install: requirements.txt
	pip install -r requirements.txt
.PHONY: install


# Defensive domain actions
# These all take the $DEFENSIVE_DOMAINS "array" (actually a
# whitespace-separated list of domains) and use Make's pattern
# substitution (https://www.gnu.org/software/make/manual/make.html#Text-Functions)
# to expand them into a list of config file paths.
#
# These config files are then prerequisites to be generated using the
# rules in "Defensive domain config", below

defensive-domains-validate: defensive-domains/config.yaml \
	$(DEFENSIVE_DOMAINS:%=defensive-domains/config/%.yaml)
	octodns-validate --config-file=defensive-domains/config.yaml
.PHONY: defensive-domains-validate

defensive-domains-noop: defensive-domains/config.yaml \
	$(DEFENSIVE_DOMAINS:%=defensive-domains/config/%.yaml) \
	defensive-domains-validate
	octodns-sync --config-file=defensive-domains/config.yaml
.PHONY: defensive-domains-noop

defensive-domains-apply: defensive-domains/config.yaml \
	$(DEFENSIVE_DOMAINS:%=defensive-domains/config/%.yaml) \
	defensive-domains-validate
	octodns-sync --config-file=defensive-domains/config.yaml --doit
.PHONY: defensive-domains-noop

defensive-domains-get-live-config: \
	$(DEFENSIVE_DOMAINS:%=defensive-domains/live/%.yaml)
.PHONY: get-live-defensive-domain-config


# Defensive domain config
# defensive-domains/config/%.yaml and defensive-domains/live/%.yaml are
# Make pattern rules (https://www.gnu.org/software/make/manual/make.html#Pattern-Rules)
# meaning that they match any file path that fits that format (where % is
# a wildcard).
#
# We then use the $< (first prerequisite), $@ (target filename), and
# $* (match stem)  automatic variables
# (https://www.gnu.org/software/make/manual/make.html#Automatic-Variables)
# to generate only the required configs.

defensive-domains/config.yaml: defensive-domains/config.tmpl.yaml defensive-domains/domains.mk
	@cat defensive-domains/config.tmpl.yaml > defensive-domains/config.yaml
	@echo "  $(DEFENSIVE_DOMAINS:%=%.:\n    sources:\n      - config\n    targets:\n      - route53\n )" >> defensive-domains/config.yaml

defensive-domains/config/%.yaml: defensive-domains/dns.tmpl.yaml
	@mkdir -p defensive-domains/config/
	@ln -s ../$(<F) $@

defensive-domains/live/%.yaml: defensive-domains/config.yaml
	octodns-dump \
	  --config-file=defensive-domains/config.yaml \
	  --output-dir=defensive-domains/live/ \
	  $*. route53


# Cleanup

clean:
	@rm -rf \
	  defensive-domains/config.yaml \
	  defensive-domains/config/ \
	  defensive-domains/live/
.PHONY: clean
