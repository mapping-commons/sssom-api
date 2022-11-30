dev:
	uvicorn src.main:app --reload

REGISTRY_URL = https://raw.githubusercontent.com/mapping-commons/mh_mapping_initiative/master/registry.yml

$(PWD)/data/registry.yml:
	wget $(REGISTRY_URL) -O $@

ttl_from_registry: $(PWD)/data/registry.yml
	cd src && python3 registry_parser.py $<

deploy_api:
	docker run -d -v $(PWD)/data/mappings.ttl:/code/mapping.ttl \
		-v $(PWD)/.env:/code/.env -p 80:80 anitacaron/sssom-api:v0.0.1

