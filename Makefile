dev:
	uvicorn src.main:app --reload

ttl_from_registry: data/registry.yml
	cd src && python3 registry_parser.py $<

deploy_api:
	docker run -d -v $(PWD)/data/mappings.ttl:/code/mapping.ttl \
		-v $(PWD)/.env:/code/.env -p 80:80 anitacaron/sssom-api:v0.0.1

