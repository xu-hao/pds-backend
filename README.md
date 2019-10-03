# pds-backend


## job submission format
```
{
  "image": docker image,
  "name": name,
  "port": port,
  "parameters": parameters,
  "mounts": [ {
    "source": source path,
    "target": target path,
    "type": type,
    "read_only": read only
  } ]
}
```



## run
```
docker-compose -f docker-compose.yml up --build -V
```

## test
```
docker-compose -f docker-compose.yml -f test/docker-compose.yml up --build -V --exit-code-from pds-backend-test
```
