dev:
	uvicorn src.main:app --reload

ttl_from_registry: registry.yml
	cd src && python3 sparql_endpoint.py $<

deploy:
	docker run -d -v $(PWD)/mappings.ttl:/code/mapping.ttl \
		-v $(PWD)/.env:/code/.env -p 80:80 anitacaron/sssom-api:v0.0.1

