dev:
	uvicorn src.main:app --reload

ttl_from_registry: registry.yml
	cd src && python.py sparql_endpoint.py $<