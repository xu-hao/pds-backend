import logging
import json
import docker
from docker.types import Mount
import os
import yaml
from .plugin_config import add_plugin_configs, delete_plugin_configs, from_docker_compose, sort_plugin_configs

logger = logging.getLogger()
logger.setLevel(logging.INFO)

    
def start_plugins(pcs):
    for pc in sort_plugin_configs(pcs):
        run_container(pc)


def stop_plugins(pcs):
    for pc in reversed(sort_plugin_configs(pcs)):
        stop_container(pc)


def remove_plugins(pcs):
    for pc in pcs:
        remove_container(pc)


def get_container(pc):
    client = docker.from_env()
    ret = client.containers.get(pc["name"])
    return ret


def network():
    return os.environ["COMPOSE_PROJECT_NAME"] + "_default"


def run_container(pc):
    client = docker.from_env()
    volumes = list(map(lambda l: Mount(l["target"], l["source"], type=l["type"], read_only=l["read_only"]), pc.get("volumes", [])))
    logging.info("volumes = {0}".format(volumes))
    print(client.containers)
    ret = client.containers.run(pc["image"], environment=pc.get("environment", {}), network=network(), mounts=volumes, detach=True, stdout=True, stderr=True, name=pc["name"], hostname=pc["name"])
    logging.info("ret = {0}".format(ret))
    return ret


def stop_container(pc):
    client = docker.from_env()
    ret = client.containers.get(pc["name"])
    ret.stop()


def remove_container(pc):
    client = docker.from_env()
    ret = client.containers.get(pc["name"])
    ret.remove()


def load_plugins(f):
    return from_docker_compose(yaml.safe_load(f))


def init_plugin():
    init_plugin_path = os.environ.get("INIT_PLUGIN_PATH")

    if init_plugin_path is not None:
        for fn in os.listdir(init_plugin_path):
            if fn.endswith(".yml") or fn.endswith(".yaml"):
                with open(os.path.join(init_plugin_path, fn), "r") as f:
                    pcs = load_plugins(f)
                    start_plugins(pcs)
                    add_plugin_configs(pcs)    


def delete_init_plugin():
    init_plugin_path = os.environ.get("INIT_PLUGIN_PATH")

    if init_plugin_path is not None:
        for fn in os.listdir(init_plugin_path):
            if fn.endswith(".yml") or fn.endswith(".yaml"):
                with open(os.path.join(init_plugin_path, fn), "r") as f:
                    pcs = load_plugins(f)
                    stop_plugins(pcs)
                    remove_plugins(pcs)
                    for pc in pcs:
                        delete_plugin_configs(pc)




