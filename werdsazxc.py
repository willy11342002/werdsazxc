from inspect import signature
from functools import wraps
import traceback
import requests
import logging
import inspect
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
                    Dict(v) if isinstance(value, dict) else v
                    for v in value
                ]

    def __getattr__(self, key):
        if key.startswith('_'):
            return dict.__getattr__(self, key)
        return self.get(key)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            return dict.__setattr__(self, key, value)
        self[key] = value

    def __delattr__(self, key):
        del self[key]


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

