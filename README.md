# pds-backend

## how to deploy

### set port

The default port is `8080`, if you want to change the port, update in `.env` file `API_PORT`.

### run command

#### unsecure mode
##### start `pds-backend` 
```
docker-compose -f docker-compose.yml -f nginx/unsecure/docker-compose.yml up --build -d -V
```

##### stop `pds-backend`
```
docker-compose -f docker-compose.yml -f nginx/unsecure/docker-compose.yml down -t <timeout>
```

set `<timeout>` to a longer time in case it times out before graceful shutdown

#### secure mode
##### start `pds-backend` 

modify `.env`:

set the `JWT_SECRET` variable to a string

set `SSL_CERT_DIR` to a directory containing `cert.pem` and `key.pem`

```
docker-compose -f docker-compose.yml -f nginx/secure/docker-compose.yml up --build -d -V
```

##### stop `pds-backend`
```
docker-compose -f docker-compose.yml -f nginx/secure/docker-compose.yml down -t <timeout>
```



### urls for frontend

#### config
```curl http://<host>:<port>/v1/plugin/pds-config/config```

#### aggregator
```curl http://<host>:<port>/v1/plugin/pds-aggregator/guidance?patient_id=<patient_id>&model=<model>&model_plugin_id=<model_plugin_id>&timestamp=<timestamp>```

parameters

`model_plugin_id`: which model plugin id to use.

`timestamp`: a time stamp in ISO 8601 format. This is used to calculate some of the features such as age.

`patinet_id`: patient id.

`model`: which model to use.

This end point will construct the following calls to the model plugin:

clinical feature variables
```
curl -X GET http://<host>:<port>/v1/plugin/<model_plugin_id>/clinical_feature_variables
```

This expects 
```
[{
  "clinical_feature_variable": <clinical_feature_variable>,
  "title": <title>,
  "description": <description>,
  "unit": <unit>, # optional
  ...
}, ...]
```

guidance
```
curl -X POST http://<host>:<port>/v1/plugin/<model_plugin_id>/guidance/{model} -d '
[{
  "clinical_feature_variable": <clinical feature variable>,
  "title": <title>,
  "description": <description>,
  "value", <value>,
  "calculation": <calculation>,
  "certitude": <certitude>
}, ...]'
```


#### model
```
curl http://<host>:<port>/v1/plugin/<model_plugin_id>/plugin path
```


### urls for plugins

```
curl "http://<host>:<port>/v1/plugin/<name>/<path>"
```

#### dpi
```
curl http://<host>:<port>/v1/plugin/pds-data-provider-mock-fhir/Patient/38
```

#### phenotype mapper

```
curl "https//<host>:<port>/v1/plugin/pds-phenotype-mapping/mapping?data_provider_plugin_id=pds-data-provider-mock-fhir&timestamp=2019-10-28T00:00:00Z&patient_id=38" -d '[{
  "clinical_feature_variable": <clinical_feature_variable>,
  "unit": <unit> # optional
}, ...]
```

parameters

`data_provider_plugin_id`: which data provider plugin interface to use.

`timestamp`: a time stamp in ISO 8601 format. This is used to calculate some of the features such as age.

`patinet_id`: patient id

`clinical_feature_variable`: clinical feature variable

available variables
```
    LOINC:2160-0: serum creatinine
    LOINC:82810-3: pregnancy
    HP:0001892: bleeding
    HP:0000077: kidney dysfunction
    LOINC:30525-0: Age
    LOINC:54134-2: Race
    LOINC:54120-1: Ethnicity
    LOINC:21840-4: Sex
    LOINC:8302-2: height
    LOINC:29463-7: weight
    LOINC:39156-5: bmi
```

`unit`: unit

```
LOINC:2160-0: type: number, possible values [0..), units: 'mg/dL',
LOINC:82810-3: type: boolean, possible values: [ true | false ], units: n/a
HP:0001892: type: boolean, possible values: [ true | false ], units: n/a
HP:0000077: type: boolean, possible values [ true | false ], units: n/a
LOINC:30525-0: type: integer, possible values [0..), unit: year
LOINC:54134-2: type: string, possible values: https://www.hl7.org/fhir/v3/Race/cs.html, unit: n/a
Race - FHIR v4.0.1
This Code system is used in the following value sets: ValueSet: v2 ETHNIC GROUP (FHIR Value set/code system definition for HL7 v2 table 0005 ( ETHNIC GROUP)) ValueSet: v3 Code System Race ( In the United States, federal standards for classifying data on race determine the categories used by federal agencies and exert a strong influence on categorization by state and local agencies and private ...
www.hl7.org

LOINC:54120-1: type: string, possible values: https://www.hl7.org/fhir/v3/Ethnicity/cs.html, unit: n/a
LOINC:21840-4: type: string, possible values: http://hl7.org/fhir/2018Sep/codesystem-administrative-gender.html, unit: n/a
Codesystem-administrative-gender - FHIR v3.5.0
Normative Candidate Note: This page is candidate normative content for R4 in the Patient Package.Once normative, it will lose it's Maturity Level, and breaking changes will no longer be made.. This is a code system defined by the FHIR project.
hl7.org

LOINC:8302-2: type: number, possible values [0..), unit: m
LOINC:29463-7: type: number, possible values [0..), unit kg
LOINC:39156-5: type: number, possible values [0..), unit kg/m^2
```
#### mpi
```
curl "http://<host>:<port>/v1/plugin/pdsmpi-ref/plugin path"
```

#### profile
```
curl "http://<host>:<port>/v1/plugin/pds-profile/profile?data_provider_plugin_id=pds-data-provider-mock-fhir&phenotype_mapping_plugin_id=pds-phenotype-mapping&model_plugin_id=pdsmpi-ref&timestamp=2019-10-28T00:00:00Z&patient_id=38"
```

`data_provider_plugin_id`: which data provider plugin interface to use.

`model_plugin_id`: which model plugin interface to use.

`phenotype_mapping_plugin_id`: which phenotype mapping plugin interface to use.

`timestamp`: a time stamp in ISO 8601 format. This is used to calculate some of the features such as age.

`patinet_id`: patient id

#### logging
```
curl -X POST "http://<host>:<port>/v1/plugin/logging/log" -H "Content-Type: application/json" -d '{
  "event": "e",
  "timestamp": "2019-10-28T00:00:00Z",
  "source": "source",
  "level": "1"
}'
```

## plugin configuration format
```
{
  "image": docker image,
  "name": name,
  "port": port,
  "environment": environment,
  "volumes": [ {
    "source": source path,
    "target": target path,
    "type": type,
    "read_only": read only
  } ],
  depends_on: [ service ]
}
```

## plugin configuration format for INIT_PLUGIN_PATH
`.yaml` or `.yml`

```
services:
  <name>:
    image: <docker image>
    port: <port>
    environment: <environment>
    volumes:
      - source: <source path>
        target: <target path>
        type: <type>
        read_only: <read only>
    depends_on:
      - <service>
volumes:
  <name>:
    persistent: <persistent>
```

## test
```
./test.sh
```
