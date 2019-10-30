# pds-backend

## how to deploy

### set port

The default port is `8080`, if you want to change the port, update in `.env` file `API_PORT`. We assume that we use the default port in the following.

### run command

To start `pds-backend`
```
docker-compose up --build -d
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
curl http://<host>:<port>/v1/plugin/<model_plugin_id>/plugin path\
```




### urls for plugins

#### dpi
```
curl http://localhost:8080/v1/plugin/pds-data-provider-mock-fhir/Patient/38
```

#### phenotype mapper

```
curl "http://localhost:8080/v1/plugin/pds-phenotype-mapping/mapping?data_provider_plugin_id=pdsdpi-mock-fhir&timestamp=2019-10-28T00:00:00Z&patient_id=38&clinical_feature_variable=age"
```

parameters

`data_provider_plugin_id`: which data provider plugin interface to use.

`timestamp`: a time stamp in ISO 8601 format. This is used to calculate some of the features such as age.

`patinet_id`: patient id

`clinical_feature_variable`: clinical feature variable

available variables
```
    "2160-0": serum_creatinine, # serum creatinine
    "82810-3": pregnancy, # pregnancy
    "HP:0001892": bleeding, # bleeding
    "HP:0000077": kidney_dysfunction, # kidney dysfunction
    "age": age,
    "race": race,
    "ethnicity": ethnicity,
    "gender": gender,
    "8302-2": height,
    "29463-7": weight,
    "39156-5": bmi
```

#### mpi
```
curl "http://localhost:8080/v1/plugin/pdsmpi-ref/plugin path"
```

#### profile
```
curl "http://localhost:8080/v1/plugin/pds-profile/profile?data_provider_plugin_id=pdsdpi-mock-fhir&phenotype_mapping_plugin_id=pds-phenotype-mapping&model_plugin_id=pdsmpi-ref&timestamp=2019-10-28T00:00:00Z&patient_id=38"
```

`data_provider_plugin_id`: which data provider plugin interface to use.

`model_plugin_id`: which model plugin interface to use.

`phenotype_mapping_plugin_id`: which phenotype mapping plugin interface to use.

`timestamp`: a time stamp in ISO 8601 format. This is used to calculate some of the features such as age.

`patinet_id`: patient id

#### logging
```
curl -X POST "http://localhost:8080/v1/plugin/logging/log" -H "Content-Type: application/json" -d '{
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
```



## run
```
docker-compose -f docker-compose.yml up --build -V
```

## test
```
docker-compose -f docker-compose.yml -f test/docker-compose.yml up --build -V --exit-code-from pds-backend-test
```
