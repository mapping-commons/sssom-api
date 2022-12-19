# SSSOM-API

The Simple Standard for Sharing Ontological Mappings (SSSOM) API is a tool for accessing ontological mappings between different ontologies.

## SSSOM API locally

You can run the API locally using Docker:

1. `docker-compose up --build`

This will start the three services:

1. The API itself (`service api`)
2. Triplestore RDF4J (`service triplestore`)
3. Upload data into the triplestore (`service upload-triplestore`)

After the `service upload-triplestore` finish and stops, you can access the SSSOM API at `localhost:8008/docs`.

You can access the triplestore at `localhost:8080/rdf4j-workbench`.

## Endpoints

The SSSOM API is designed to be easy to use and has the following endpoints:

`/entity/{CURIE}`

Retrive all mappings with `CURIE` as `subject_id` or `object_id`

`/mappings/?filter`

Retrieve all mappings in the triplestore. It's possible to filter your results using the filter. The filter pattern is `[field]:[operator]:[value]`.

For the complete list of fields, check [here](https://mapping-commons.github.io/sssom/Mapping/).

The list of operators is:

| Operator | Description              |
|----------|--------------------------|
| ge       | greater than or equal to |
| gt       | greater than             |
| le       | less than or equal to    |
| lt       | less than                |
| contains | contains                 |

`/mappings/{field}/{value}`

Retrieve the mappings with `field=value`. Check [here](https://mapping-commons.github.io/sssom/Mapping/) to see the complete list of fields/slots for a mapping.

`/mapping_sets`

Retrieve the mapping_sets in the triplestore.

`/mapping_sets/{id}/mappings`

Retrieve the mappings for a mapping set.

