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
import api
from debug.utils import bag_equal


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


name = "nginx10"
name2 = "nginx20"


def pc(temp_dir_name):
    return {
        "image": "nginx:1.17.4",
        "parameters": None,
        "name": name,
        "port": 80,
        "mounts": [
            {
                "target": "/usr/share/nginx/html",
                "source": temp_dir_name,
                "type": "bind",
                "read_only": True
            }
        ]
    
    }


def pc2(temp_dir_name):
    return {
        "image": "nginx:1.17.4",
        "parameters": None,
        "name": name2,
        "port": 80,
        "mounts": [
            {
                "target": "/usr/share/nginx/html",
                "source": temp_dir_name,
                "type": "bind",
                "read_only": True
            }
        ]
    
    }


fil = {"name": name}


def test_run_container():
    with tempfile.TemporaryDirectory(prefix="/tmp/") as temp_dir_name:
        os.chmod(temp_dir_name, 0o755)
        s = "pds"
        with open(os.path.join(temp_dir_name, "index.json"), "w+") as f:
            f.write(json.dumps(s))

        try:
            apc = pc(temp_dir_name)
            plugin.run_container(apc)

            container_name = apc["name"]

            resp = requests.get("http://{host}/index.json".format(host=container_name))

            assert resp.status_code == 200
            assert resp.json() == s
        finally:
            plugin.stop_container(apc)
            plugin.remove_container(apc)


def test_add_plugin_config():
    try:
        apc = pc("/tmp")
        plugin_config.add_plugin_configs([apc])
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 1
    finally:
        plugin_config.delete_plugin_configs({})


def test_add_plugin_config2():
    try:
        apc = pc("/tmp")
        plugin_config.add_plugin_configs([apc])
        with pytest.raises(Exception):
            plugin_config.add_plugin_configs([apc])
    finally:
        plugin_config.delete_plugin_configs({})


def test_run_plugin_container():
    with tempfile.TemporaryDirectory(prefix="/tmp/") as temp_dir_name:
        os.chmod(temp_dir_name, 0o755)
        s = "pds"
        with open(os.path.join(temp_dir_name, "index.json"), "w+") as f:
            f.write(json.dumps(s))

        try:
            apc = pc(temp_dir_name)
            plugin_config.add_plugin_configs([apc])
            ps = plugin_config.get_plugin_configs({"name": name})
            assert len(ps) == 1
            apc = ps[0]
            plugin.run_container(apc)
        
            resp = requests.get("http://pds-backend:8080/v1/plugin/{name}/index.json".format(name=name))
        
            assert resp.status_code == 200
            assert resp.json() == s
        finally:
            api.delete_containers()
            plugin_config.delete_plugin_configs({})


def test_run_plugin_container_api():
    with tempfile.TemporaryDirectory(prefix="/tmp/") as temp_dir_name:
        os.chmod(temp_dir_name, 0o755)
        s = "pds"
        with open(os.path.join(temp_dir_name, "index.json"), "w+") as f:
            f.write(json.dumps(s))

        try:
            apc = pc(temp_dir_name)
            plugin_config.add_plugin_configs([apc])
            ps = plugin_config.get_plugin_configs({"name": name})
            assert len(ps) == 1
            apc = ps[0]

            requests.put("http://pds-backend:8080/v1/admin/plugin/{name}/container".format(name=name))

            resp = requests.get("http://pds-backend:8080/v1/plugin/{name}/index.json".format(name=name))

            assert resp.status_code == 200
            assert resp.json() == s
        finally:
            api.delete_containers()
            plugin_config.delete_plugin_configs({})


def test_get_plugin_config_api():
    with tempfile.TemporaryDirectory(prefix="/tmp/") as temp_dir_name:
        os.chmod(temp_dir_name, 0o755)
        s = "pds"
        with open(os.path.join(temp_dir_name, "index.json"), "w+") as f:
            f.write(json.dumps(s))

        try:
            apc = pc(temp_dir_name)
            plugin_config.add_plugin_configs([apc])
            ps = plugin_config.get_plugin_configs({"name": name})
            assert len(ps) == 1
            apc = ps[0]
            apc["_id"] = str(apc["_id"])

            requests.put("http://pds-backend:8080/v1/admin/plugin/{name}/container".format(name=name))

            resp = requests.get("http://pds-backend:8080/v1/admin/plugin/{name}".format(name=name))

            assert resp.status_code == 200
            assert resp.json() == apc
        finally:
            api.delete_containers()
            plugin_config.delete_plugin_configs({})


def test_get_plugin_configs_api_name():
    with tempfile.TemporaryDirectory(prefix="/tmp/") as temp_dir_name:
        os.chmod(temp_dir_name, 0o755)
        s = "pds"
        with open(os.path.join(temp_dir_name, "index.json"), "w+") as f:
            f.write(json.dumps(s))

        try:
            apc = pc(temp_dir_name)
            plugin_config.add_plugin_configs([apc])
            ps = plugin_config.get_plugin_configs({"name": name})
            assert len(ps) == 1
            apc = ps[0]
            apc["_id"] = str(apc["_id"])

            resp = requests.get("http://pds-backend:8080/v1/admin/plugin?name={name}".format(name=name))

            assert resp.status_code == 200
            assert resp.json() == [apc]
        finally:
            plugin_config.delete_plugin_configs({})



def test_get_plugin_configs_name_regex():
    with tempfile.TemporaryDirectory(prefix="/tmp/") as temp_dir_name:
        os.chmod(temp_dir_name, 0o755)
        s = "pds"
        with open(os.path.join(temp_dir_name, "index.json"), "w+") as f:
            f.write(json.dumps(s))

        try:
            apc = pc(temp_dir_name)
            apc2 = pc2(temp_dir_name)
            plugin_config.add_plugin_configs([apc, apc2])
            ps = plugin_config.get_plugin_configs({})
            assert len(ps) == 2
            for apc0 in ps:
                apc0["_id"] = str(apc0["_id"])

            ps2 = plugin_config.get_plugin_configs({"name": {"$regex": "nginx.*"}})
            for a in ps2:
                a["_id"] = str(a["_id"])

            assert bag_equal(ps2, ps)
        finally:
            plugin_config.delete_plugin_configs({})


def test_get_plugin_configs_api_name_regex():
    with tempfile.TemporaryDirectory(prefix="/tmp/") as temp_dir_name:
        os.chmod(temp_dir_name, 0o755)
        s = "pds"
        with open(os.path.join(temp_dir_name, "index.json"), "w+") as f:
            f.write(json.dumps(s))

        try:
            apc = pc(temp_dir_name)
            apc2 = pc2(temp_dir_name)
            plugin_config.add_plugin_configs([apc, apc2])
            ps = plugin_config.get_plugin_configs({})
            assert len(ps) == 2
            for apc0 in ps:
                apc0["_id"] = str(apc0["_id"])

            resp = requests.get("http://pds-backend:8080/v1/admin/plugin?name_regex={name_regex}".format(name_regex="nginx.*"))

            assert resp.status_code == 200
            assert bag_equal(resp.json(), ps)
        finally:
            plugin_config.delete_plugin_configs({})


def test_get_plugin_container_api():
    with tempfile.TemporaryDirectory(prefix="/tmp/") as temp_dir_name:
        os.chmod(temp_dir_name, 0o755)
        s = "pds"
        with open(os.path.join(temp_dir_name, "index.json"), "w+") as f:
            f.write(json.dumps(s))

        try:
            apc = pc(temp_dir_name)
            plugin_config.add_plugin_configs([apc])
            ps = plugin_config.get_plugin_configs({"name": name})
            assert len(ps) == 1
            apc = ps[0]

            requests.put("http://pds-backend:8080/v1/admin/plugin/{name}/container".format(name=name))

            resp = requests.get("http://pds-backend:8080/v1/admin/plugin/{name}/container".format(name=name))

            assert resp.status_code == 200
            assert resp.json() == {"status": "running"}
        finally:
            api.delete_containers()
            plugin_config.delete_plugin_configs({})


def test_run_plugin_containers_api():
    with tempfile.TemporaryDirectory(prefix="/tmp/") as temp_dir_name:
        os.chmod(temp_dir_name, 0o755)
        s = "pds"
        with open(os.path.join(temp_dir_name, "index.json"), "w+") as f:
            f.write(json.dumps(s))

        try:
            apc = pc(temp_dir_name)
            apc2 = pc2(temp_dir_name)
            plugin_config.add_plugin_configs([apc, apc2])
            ps = plugin_config.get_plugin_configs({})
            assert len(ps) == 2
            apc = ps[0]

            requests.put("http://pds-backend:8080/v1/admin/container")

            resp = requests.get("http://pds-backend:8080/v1/plugin/{name}/index.json".format(name=name))

            assert resp.status_code == 200
            assert resp.json() == s
            resp2 = requests.get("http://pds-backend:8080/v1/plugin/{name}/index.json".format(name=name2))

            assert resp2.status_code == 200
            assert resp2.json() == s
        finally:
            api.delete_containers()
            plugin_config.delete_plugin_configs({})


