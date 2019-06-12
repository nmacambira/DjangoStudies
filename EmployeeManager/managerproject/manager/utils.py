import uuid
import os
import hashlib


def create_hash():
    """
    This function generate a hash
    :return: str
    """
    return uuid.uuid4().hex


def create_hash2():
    """
    This function generate 32 character long hash
    :return: str
    """
    random_data = os.urandom(128)
    return hashlib.sha224(random_data).hexdigest()
    # return hashlib.md5(random_data).hexdigest()
    # return hashlib.md5("whatever your string is".encode('utf-8')).hexdigest()