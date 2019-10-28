# pds-backend

## how to deploy

### set port

The default port is `8080`, if you want to change the port, update in `.env` file `API_PORT`. We assume that we use the default port in the following.

### run command

To start `pds-backend`
```
docker-compose up --build -d
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

parameters

`data_provider_plugin_interface`: which data provider plugin interface to use.

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
