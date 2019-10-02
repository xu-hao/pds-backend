# tx-queue


## job submission format
```
{
  "image": docker image,
  "parameters": parameters,
  "network": network
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

## run with worker
```
docker-compose -f docker-compose.yml -f worker/docker-compose.yml up --build -V
```


## test
```
docker-compose -f docker-compose.yml -f test/docker-compose.yml up --build -V --exit-code-from txqueue-test
docker-compose -f docker-compose.yml -f worker/docker-compose.yml -f worker/test/docker-compose.yml up --build -V --exit-code-from txqueue-worker-test

```
