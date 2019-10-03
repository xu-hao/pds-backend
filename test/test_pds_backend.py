import os
import requests
import time
import pytest
import json
import pymongo
import docker
from multiprocessing import Process
import shutil
from pds.backend import plugin, plugin_config
from contextlib import contextmanager
import tempfile
from bson.objectid import ObjectId


@pytest.fixture(scope="session", autouse=True)
def pause():
    yield
    if os.environ.get("PAUSE") == "1":
        input("Press Enter to continue...")

        
@pytest.fixture(scope='function', autouse=True)
def test_log(request):
    print("Test '{}' STARTED".format(request.node.nodeid)) # Here logging is used, you can use whatever you want to use for logs
    yield
    print("Test '{}' COMPLETED".format(request.node.nodeid))


def test_run_container():
    with tempfile.TemporaryDirectory(prefix="/tmp/") as temp_dir_nane:
        os.chmod(temp_dir_nane, 0o755)
        s = "pds"
        with open(os.path.join(temp_dir_nane, "index.json"), "w+") as f:
            f.write(json.dumps(s))

        pc = {
            "image": "nginx:1.17.4",
            "name": "nginx10",
            "parameters": None,
            "mounts": [
                {
                    "target": "/usr/share/nginx/html",
                    "source": temp_dir_nane,
                    "type": "bind",
                    "read_only": True
                }
            ]

        }

        try:
            plugin.run_container(pc)

            container_name = pc["name"]

            resp = requests.get("http://{host}/index.json".format(host=container_name))

            assert resp.status_code == 200
            assert resp.json() == s
        finally:
            plugin.stop_container(pc)
            plugin.remove_container(pc)


def test_add_plugin_config():
    name = "nginx10"
    pc = {
        "image": "nginx:1.17.4",
        "parameters": None,
        "name": name,
        "port": 80,
        "mounts": [
            {
                "target": "/usr/share/nginx/html",
                "source": "/tmp",
                "type": "bind",
                "read_only": True
            }
        ]

    }
    fil = {"name": name}

    try:
        plugin_config.add_plugin_configs([pc])
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 1
    finally:
        plugin_config.delete_plugin_configs(fil)


def test_run_plugin_container():
    with tempfile.TemporaryDirectory(prefix="/tmp/") as temp_dir_nane:
        os.chmod(temp_dir_nane, 0o755)
        s = "pds"
        with open(os.path.join(temp_dir_nane, "index.json"), "w+") as f:
            f.write(json.dumps(s))

        name = "nginx10"
        pc = {
            "image": "nginx:1.17.4",
            "parameters": None,
            "name": name,
            "port": 80,
            "mounts": [
                {
                    "target": "/usr/share/nginx/html",
                    "source": temp_dir_nane,
                    "type": "bind",
                    "read_only": True
                }
            ]

        }
        fil = {"name": name}

        try:
            plugin_config.add_plugin_configs([pc])
            ps = plugin_config.get_plugin_configs({"name": name})
            assert len(ps) == 1
            pc = ps[0]
            plugin.run_container(pc)

            plugin_id = pc["_id"]

            resp = requests.get("http://pds-backend:8080/v1/plugin/{plugin_id}/index.json".format(plugin_id=plugin_id))

            assert resp.status_code == 200
            assert resp.json() == s
        finally:
            plugin.stop_container(pc)
            plugin.remove_container(pc)
            plugin_config.delete_plugin_configs(fil)


