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
import yaml
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
        "environment": {},
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
        "environment": {},
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


echo_pc = {
    "image": "pds-backend-test-flask-echo-server:0.1.0",
    "environment": {},
    "name": "echo",
    "port": 80,
    "environment": {
        "HOST": "0.0.0.0",
        "PORT": "80"
    },
    "mounts": []
}

echo_pc2 = {
    "image": "pds-backend-test-flask-echo-server:0.1.0",
    "name": "echo",
    "port": 80,
    "environment": {
        "HOST": "0.0.0.0",
        "PORT": "80",
        "VAR": "data"
    },
    "mounts": []
}


fil = {"name": name}

fil2 = {"name": name2}

def test_run_container_get():
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


def test_run_container_from_init():
    try:
        apc = echo_pc
        init_plugin_path = "/plugin"
        os.mkdir(init_plugin_path)
        with open(f"{init_plugin_path}/echo.yaml", "w+") as f:
            yaml.dump(echo_pc, f, default_flow_style=False)
            
        os.environ["INIT_PLUGIN_PATH"] = init_plugin_path

        plugin.init_plugin()

        container_name = apc["name"]

        time.sleep(10)
        resp = requests.get("http://{host}/".format(host=container_name))

        assert resp.status_code == 200
        assert resp.json()["method"] == "GET"
        shutil.rmtree(init_plugin_path)
    finally:
        plugin.stop_container(apc)
        plugin.remove_container(apc)


def test_delete_container_from_init():
    apc = echo_pc
    init_plugin_path = "/plugin"
    os.mkdir(init_plugin_path)
    with open(f"{init_plugin_path}/echo.yaml", "w+") as f:
        yaml.dump(echo_pc, f, default_flow_style=False)
        
    os.environ["INIT_PLUGIN_PATH"] = init_plugin_path
        
    plugin.init_plugin()
        
    container_name = apc["name"]

    time.sleep(10)
    plugin.delete_init_plugin()

    with pytest.raises(Exception):
        resp = requests.get("http://{host}/".format(host=container_name))

    shutil.rmtree(init_plugin_path)



def test_run_container_get_echo():
    try:
        apc = echo_pc

        plugin.run_container(apc)

        container_name = apc["name"]

        time.sleep(10)
        resp = requests.get("http://{host}/".format(host=container_name))

        assert resp.status_code == 200
        assert resp.json()["method"] == "GET"

    finally:
        plugin.stop_container(apc)
        plugin.remove_container(apc)


def test_run_container_post_echo():
    s = "pds"
    try:
        apc = echo_pc

        plugin.run_container(apc)

        container_name = apc["name"]

        time.sleep(10)
        resp = requests.post("http://{host}/".format(host=container_name), headers={"Content-Type": "application/json"}, json=s)

        assert resp.status_code == 200
        assert resp.json()["data"] == json.dumps(s)
        assert resp.json()["method"] == "POST"
    finally:
        plugin.stop_container(apc)
        plugin.remove_container(apc)


def test_run_container_environment_post_echo():
    s = "pds"
    try:
        apc = echo_pc2
        plugin.run_container(apc)

        container_name = apc["name"]

        time.sleep(10)
        resp = requests.post("http://{host}/".format(host=container_name), headers={"Content-Type": "application/json"}, json=s)

        assert resp.status_code == 200
        assert resp.json()["data"] == json.dumps(s)
        assert resp.json()["method"] == "POST"
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


def test_update_plugin_config():
    try:
        apc = pc("/tmp")
        apc2 = pc2("/tmp")
        plugin_config.add_plugin_configs([apc])
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 1
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 1
        plugin_config.replace_plugin_config(name, apc2)
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 1
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 0
        ps = plugin_config.get_plugin_configs(fil2)
        assert len(ps) == 1
    finally:
        plugin_config.delete_plugin_configs({})


def test_delete_plugin_config():
    try:
        apc = pc("/tmp")
        plugin_config.add_plugin_configs([apc])
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 1
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 1
        plugin_config.delete_plugin_config(name)
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 0
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 0
    finally:
        plugin_config.delete_plugin_configs({})


def test_delete_plugin_configs_name_regex():
    try:
        apc = pc("/tmp")
        apc2 = pc2("/tmp")
        plugin_config.add_plugin_configs([apc, apc2])
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 2
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 1
        plugin_config.delete_plugin_configs({"name": {"$regex": "nginx.*"}})
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 0
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 0
    finally:
        plugin_config.delete_plugin_configs({})


def test_add_plugin_config_api():
    try:
        apc = pc("/tmp")
        resp = requests.put("http://pds-backend:8080/v1/admin/plugin", headers={"Content-Type": "application/json"}, json=[apc])
        assert resp.status_code == 200
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 1
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 1
    finally:
        plugin_config.delete_plugin_configs({})


def test_update_plugin_config_api():
    try:
        apc = pc("/tmp")
        apc2 = pc2("/tmp")
        resp = requests.put("http://pds-backend:8080/v1/admin/plugin", headers={"Content-Type": "application/json"}, json=[apc])
        assert resp.status_code == 200
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 1
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 1
        resp = requests.post("http://pds-backend:8080/v1/admin/plugin/{name}".format(name=name), headers={"Content-Type": "application/json"}, json=apc2)
        assert resp.status_code == 200
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 1
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 0
        ps = plugin_config.get_plugin_configs(fil2)
        assert len(ps) == 1
    finally:
        plugin_config.delete_plugin_configs({})


def test_delete_plugin_config_api():
    try:
        apc = pc("/tmp")
        resp = requests.put("http://pds-backend:8080/v1/admin/plugin", headers={"Content-Type": "application/json"}, json=[apc])
        assert resp.status_code == 200
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 1
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 1
        resp = requests.delete("http://pds-backend:8080/v1/admin/plugin/{name}".format(name=name))
        assert resp.status_code == 200
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 0
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 0
    finally:
        plugin_config.delete_plugin_configs({})


def test_delete_plugin_configs_api_name():
    try:
        apc = pc("/tmp")
        resp = requests.put("http://pds-backend:8080/v1/admin/plugin", headers={"Content-Type": "application/json"}, json=[apc])
        assert resp.status_code == 200
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 1
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 1
        resp = requests.delete("http://pds-backend:8080/v1/admin/plugin?name={name}".format(name=name))
        assert resp.status_code == 200
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 0
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 0
    finally:
        plugin_config.delete_plugin_configs({})


def test_delete_plugin_configs_api_name_regex():
    try:
        apc = pc("/tmp")
        apc2 = pc2("/tmp")
        resp = requests.put("http://pds-backend:8080/v1/admin/plugin", headers={"Content-Type": "application/json"}, json=[apc])
        assert resp.status_code == 200
        resp = requests.put("http://pds-backend:8080/v1/admin/plugin", headers={"Content-Type": "application/json"}, json=[apc2])
        assert resp.status_code == 200
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 2
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 1
        resp = requests.delete("http://pds-backend:8080/v1/admin/plugin?name_regex=nginx.*")
        assert resp.status_code == 200
        ps = plugin_config.get_plugin_configs({})
        assert len(ps) == 0
        ps = plugin_config.get_plugin_configs(fil)
        assert len(ps) == 0
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

            resp = requests.put("http://pds-backend:8080/v1/admin/plugin/{name}/container".format(name=name))
            assert resp.status_code == 200

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

            resp = requests.put("http://pds-backend:8080/v1/admin/plugin/{name}/container".format(name=name))
            assert resp.status_code == 200

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

            resp = requests.put("http://pds-backend:8080/v1/admin/plugin/{name}/container".format(name=name))
            assert resp.status_code == 200

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

            resp = requests.put("http://pds-backend:8080/v1/admin/container")
            assert resp.status_code == 200

            resp = requests.get("http://pds-backend:8080/v1/plugin/{name}/index.json".format(name=name))

            assert resp.status_code == 200
            assert resp.json() == s
            resp2 = requests.get("http://pds-backend:8080/v1/plugin/{name}/index.json".format(name=name2))

            assert resp2.status_code == 200
            assert resp2.json() == s
        finally:
            api.delete_containers()
            plugin_config.delete_plugin_configs({})


def test_get_plugin_containers_api():
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

            resp = requests.put("http://pds-backend:8080/v1/admin/container")
            assert resp.status_code == 200

            resp = requests.get("http://pds-backend:8080/v1/admin/container")

            assert resp.status_code == 200
            assert bag_equal(resp.json(), [{"name": name, "container": {"status": "running"}}, {"name": name2, "container": {"status": "running"}}])
        finally:
            api.delete_containers()
            plugin_config.delete_plugin_configs({})

