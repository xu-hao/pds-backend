import requests
from pds.backend import plugin_config, plugin
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

get_headers = {
    "Accept": "application/json"
}

post_headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}


def get_plugin(plugin_id, path):
    logger.error("plugin_id = {0}".format(plugin_id))
    pc = plugin_config.get_plugin_config(plugin_id)
    resp = requests.get("http://{host}:{port}/{path}".format(host=pc["name"], port=pc["port"], path=path), headers=get_headers)
    return resp.json()


def post_plugin(plugin_id, path, body):
    pc = plugin_config.get_plugin_config(plugin_id)
    resp = requests.post("http://{host}:{port}/{path}".format(host=pc["name"], port=pc["port"], path=path), headers=post_headers, json=body)
    return resp.json()


def get_plugin_config(plugin_id):
    pc = plugin_config.get_plugin_config(plugin_id)
    return pc


def fil(name, name_regex):
    fils = []
    if name_regex is not None:
        fils.append({"name": {"$regex": name}})
    if name_regex is not None:
        fils.append({"name": name})
    return {"$and": fils}


def get_plugin_configs(name=None, name_regex=None):
    pc = plugin_config.get_plugin_configs(fil(name, name_regex))
    return pc


def get_plugin_ids(name=None, name_regex=None):
    ids = plugin_config.get_plugin_ids(fil(name, name_regex))
    return ids


def add_plugin_config(pc):
    pc = plugin_config.add_plugin_configs([pc])
    return pc


def delete_plugin_config(plugin_id):
    plugin_config.delete_plugin_configs([plugin_id])


def update_plugin_config(plugin_id, body):
    plugin_config.replace_plugin_config(plugin_id, body)


def get_plugin_container(plugin_id):
    pc = plugin_config.get_plugin_config(plugin_id)
    container = plugin.get_container(pc)
    if container is not None:
        return {
            "image": container.image,
            "statue": container.status
        }
    else:
        return None


def add_plugin_container(plugin_id):
    pc = plugin_config.get_plugin_config(plugin_id)
    plugin.run_container(pc)


def delete_plugin_container(plugin_id):
    pc = plugin_config.get_plugin_config(plugin_id)
    plugin.stop_container(pc)
    plugin.remove_container(pc)


def get_containers():
    containers = []
    for pc in plugin_config.get_plugin_configs({}):
        container = plugin.get_container(pc)
        if container is not None:
            cs = {
                "image": container.image,
                "statue": container.status
            }
        else:
            cs = None

        containers.append({
            "_id": pc["_id"],
            "name": pc["name"],
            "container": cs
        })
    return containers


def add_containers():
    for pc in plugin_config.get_plugin_configs({}):
        plugin.run_container(pc)


def delete_containers():
    for pc in plugin_config.get_plugin_configs({}):
        plugin.stop_container(pc)
        plugin.remove_container(pc)
