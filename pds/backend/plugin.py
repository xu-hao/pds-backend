import logging
import json
import docker
from docker.types import Mount

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def start_plugins(pcs):
    for pc in pcs:
        run_container(pc)


def stop_plugins(pcs):
    for pc in pcs:
        stop_container(pc)


def remove_plugins(pcs):
    for pc in pcs:
        remove_container(pc)


def container_name(pc):
    return "plugin_config_" + pc["_id"]


def get_container(pc):
    client = docker.from_env()
    ret = client.containers.get(container_name(pc))
    return ret


def run_container(pc):
    client = docker.from_env()
    volumes = list(map(lambda l: Mount(l["target"], l["source"], type=l["type"], read_only=l["read_only"]), pc["mounts"]))
    logging.info("volumes = {0}".format(volumes))
    ret = client.containers.run(pc["image"], environment={
        "PARAMETERS": json.dumps(pc["parameters"])
    }, network=pc["network"], mounts=volumes, detach=True, stdout=True, stderr=True, name=container_name(pc))
    logging.info("ret = {0}".format(ret))
    return ret


def stop_container(pc):
    client = docker.from_env()
    ret = client.containers.get(container_name(pc))
    ret.stop()


def remove_container(pc):
    client = docker.from_env()
    ret = client.containers.get(container_name(pc))
    ret.remove()
