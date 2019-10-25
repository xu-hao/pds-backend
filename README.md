# pds-backend


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
