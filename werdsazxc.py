from random import randint
from Crypto.Cipher import AES
from inspect import signature
from functools import wraps
import traceback
import logging
import inspect
import hashlib
import base64
import json
import sys
import re
logger = logging.getLogger('Tools')


class Dict(dict):
    # 實體化時將所有子物件也實體化為JSLike Dict物件
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = Dict(value)
            if type(value) == list:
                self[key] = [
                    Dict(v) if isinstance(v, dict) else v
                    for v in value
                ]

    def sub(self, keys):
        return {k: v for k, v in self.items() if k in keys}

    def __getattr__(self, key):
        try:
            return self.__getattribute__(key)
        except AttributeError as e:
            return self.get(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]


class Cryptor:
    def __init__(self, key: bytes):
        self.key = hashlib.md5(key).hexdigest().encode()

    @property
    def cryptor(self):
        return AES.new(self.key, AES.MODE_CBC, self.key[:AES.block_size])

    def pad(self, s: bytes) -> bytes:
        '''補字以滿足CBC MODE'''
        n = AES.block_size - len(s) % AES.block_size
        s = s + n * chr(n).encode()
        return s

    def unpad(self, s: bytes) -> bytes:
        '''解CBC MODE後綴'''
        s = s.decode()
        s = s[0: -ord(s[-1])]
        return s.encode()

    def encrypt(self, s) -> str:
        '''加密, 傳入為任意jsonable物件, 返回加密文字'''
        s = json.dumps(s)
        s = s.encode()

        s = self.pad(s)
        s = self.cryptor.encrypt(s)
        s = base64.b64encode(s)

        s = s.decode()
        return s

    def decrypt(self, s: str):
        '''解密, 傳入為加密文字, 傳出為解密後物件'''
        s = s.encode()

        s = base64.b64decode(s)
        s = self.cryptor.decrypt(s)
        s = self.unpad(s)

        s = s.decode()
        s = json.loads(s)
        return s


def log(func):
    @wraps(func)
    def wrapper(*args, **kw):
        # 紀錄傳入參數
        sig = signature(func)
        bound = sig.bind_partial(*args, **kw)
        bound.apply_defaults()
        logger.debug(f'{func.__name__} 傳入: {dict(bound.arguments)}')

        # 執行函數
        try:
            result = func(*args, **kw)
        # 紀錄報錯訊息, 紀錄後依舊拋出錯誤
        except Exception as e:
            logger.error(f'{func.__name__} 錯誤: {e.__class__.__name__} {e}')
            logger.error('\n' + traceback.format_exc())
            raise e

        # 紀錄結果
        logger.debug(f'{func.__name__} 返回: {result}')
        return result
    return wrapper
