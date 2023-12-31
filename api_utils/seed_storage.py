import os, logging
from api_utils.Seed import Seed
from api_utils.get_db import get_gcp_bucket
from api_utils.collections import SEEDS, SPOILER_LOGS, API_KEYS
from api_utils.get_timestamp import get_timestamp
import google
from google.cloud import datastore


class SeedStorage(object):

    @staticmethod
    def get_env():
        return os.getenv("ENV", "UNKNOWN")
    
    @staticmethod
    def get_seed_key(datastore_client, seed_id):
        return datastore_client.key(SEEDS + SeedStorage.get_env(), seed_id)
    
    @staticmethod
    def get_spoiler_log_key(datastore_client, seed_id):
        return datastore_client.key(SPOILER_LOGS + SeedStorage.get_env(), seed_id)
    
    @staticmethod
    def get_api_key_key(datastore_client, api_key):
        # I typo'd the name of the datastore when I first created it and am too lazy to correct it
        return datastore_client.key("api_key" + SeedStorage.get_env(), api_key)

    @staticmethod
    def get_patch_bucket():
        return os.environ.get('PATCH_BUCKET')

    @staticmethod
    def create_seed(seed: Seed, patch, spoiler_log):
        ''' Store the given seed, patch, and spoiler log in storage
            Return the JSON version of the seed
        '''
        ### store the seed and its spoiler log in datastore ###
        datastore_client = datastore.Client()

        # Seed insert
        store_key = SeedStorage.get_seed_key(datastore_client, seed.seed_id)
        entity = datastore.Entity(key = store_key, exclude_from_indexes=("flags",))
        entity["description"] = seed.description
        entity["flags"] = seed.flags
        entity["hash"] = seed.hash
        entity["type"] = seed.type
        entity["version"] = seed.version
        entity["created_by"] = seed.created_by
        entity["created_at"] = seed.created_at

        datastore_client.put(entity)

        #Spoiler Log insert
        store_key = SeedStorage.get_spoiler_log_key(datastore_client, seed.seed_id)
        entity = datastore.Entity(key = store_key, exclude_from_indexes=("log",))
        entity["log"] = spoiler_log
        entity["created_at"] = get_timestamp()

        datastore_client.put(entity)

        ### store the patch in the Google Cloud bucket ###
        bucket = get_gcp_bucket()
        blob = bucket.blob(seed.seed_id)
        blob.upload_from_string(patch)

        return seed.to_json()

    @staticmethod
    def get_api_key(key):
        ''' get the api key from the database -- return None if it doesn't exist '''
        api_key = None

        # try first from datastore
        datastore_client = datastore.Client()
        store_key = SeedStorage.get_api_key_key(datastore_client, key)
        entity = datastore_client.get(key=store_key)
        api_key = entity

        return api_key

    @staticmethod
    def get_spoiler_log(seed_id):
        ''' get the spoiler log from the database -- return None if it doesn't exist '''
        log = None

        # try first from datastore
        datastore_client = datastore.Client()
        store_key = SeedStorage.get_spoiler_log_key(datastore_client, seed_id)
        entity = datastore_client.get(key=store_key)
        log = entity

        return log

    @staticmethod
    def get_patch(seed_id):

        ''' get the patch for the given seed id -- return None if it doesn't exist '''
        bucket = get_gcp_bucket()

        try:
            blob = bucket.blob(seed_id)
            if blob is None:
                patch = None
            else:
                patch = blob.download_as_bytes().decode('utf-8')
        except google.api_core.exceptions.NotFound:
            patch = None

        return patch

    @staticmethod
    def get_seed(seed_id):
        ''' get the seed info for the given seed id -- return None if it doesn't exist '''
        seed_json = None

        datastore_client = datastore.Client()
        store_key = SeedStorage.get_seed_key(datastore_client, seed_id)
        entity = datastore_client.get(key=store_key)
        if entity is not None:
            s = Seed()
            s.seed_id = seed_id
            s.description = entity["description"]
            s.flags = entity["flags"]
            s.hash = entity["hash"]
            s.type = entity["type"]
            s.version = entity["version"]
            s.created_by = entity["created_by"]

            seed_json = s.to_json()

        return seed_json



