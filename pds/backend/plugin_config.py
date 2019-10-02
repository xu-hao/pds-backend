import os
import logging
from pymongo import MongoClient
from contextlib import contextmanager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@contextmanager
def plugin_db():
    mongo_database = os.environ["MONGO_DATABASE"]
    c = MongoClient(os.environ["MONGO_HOST"], int(os.environ["MONGO_PORT"]), username=os.environ["MONGO_USERNAME"], password=os.environ["MONGO_PASSWORD"], authSource=mongo_database)
    try:
        db = c[mongo_database]
        collection = db[os.environ["MONGO_COLLECTION"]]
        yield collection
    finally:
        c.close()
    

def get_plugin_configs(fil):
    with plugin_db() as collection:
        return list(collection.find(fil))


def get_plugin_config(plugin_id):
    with plugin_db() as collection:
        return next(collection.find({"_id": plugin_id}))


def get_plugin_ids(fil):
    with plugin_db() as collection:
        return next(collection.find(fil, []))


def add_plugin_configs(pc):
    with plugin_db() as collection:
        return collection.insert_many(post).inserted_ids
    
    
def update_plugin_configs(fil, update):
    with plugin_db() as collection:
        return collection.update_many(fil, update).modified_count


def replace_plugin_configs(plugin_id, update):
    with plugin_db() as collection:
        return collection.replace_one({"_id": plugin_id}, update).modified_count


def delete_plugin_configs(fil):
    with plugin_db() as collection:
        return collection.delete_many(fil).deleted_count


def delete_plugin_config(plugin_id):
    with plugin_db() as collection:
        return collection.delete_one({"_id": plugin_id}).deleted_count

