# pds-backend

## how to deploy

### set port
update `.env` `API_PORT`

### run command
```
docker-compose up --build
```

### urls for plugins
#### dpi
```
curl http://localhost:8080/v1/plugin/pdsdpi-mock-fhir/Patient/38
```
#### phenotype mapper
```
curl "http://localhost:8080/v1/plugin/pds-phenotype-mapping/mapping?data_provider_plugin_interface=pdsdpi-mock-fhir&timestamp=2019-10-28T00:00:00Z&patient_id=38&clinical_feature_variable=age"
```

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
