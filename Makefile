all: $(DEFENSIVE_DOMAINS:%=defensive-domains/config/%.yaml)

install:
	brew install octodns

defensive-domains/config/%.yaml: defensive-domains/dns.tmpl.yaml
	@mkdir -p defensive-domains/config/
	@ln -s ../$(<F) $@

clean:
	@rm -rf defensive-domains/config/*.yaml
