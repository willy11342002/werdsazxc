from importlib import import_module
from inspect import signature
from functools import partial
from functools import wraps
from logging import *
import traceback
import logging


class EncryptFormatter(logging.Formatter):
    '''紀錄檔加解密功能'''
    ENCRYPT_SPLITTER = '//T//'
    def __init__(self, key=b'1234', salt=False, *args, **kw):
        super().__init__(*args, **kw)
        cryutils = import_module('cryutils')
        self.encryptor = cryutils.Cryptor(key)
        self.salt = salt

    def format(self, record):
        if not hasattr(record, '_is_password'):
            record.msg = (
                f'{self.ENCRYPT_SPLITTER}'
                f'{self.encryptor.encrypt(record.msg, salt=self.salt)}'
            )
            record._is_password = True
        return super().format(record)

    def decrypt(self, line):
        if not line.strip():
            return ''
        strs = line.split(self.ENCRYPT_SPLITTER)
        info = strs[0]
        encrypted = self.ENCRYPT_SPLITTER.join(strs[1:])
        decrypted = self.encryptor.decrypt(encrypted, self.salt)
        return info + decrypted

    def decrypt_file(self, ori, des, encoding='utf-8'):
        with open(ori, 'r', encoding=encoding) as f:
            lines = f.readlines()

        lines = [self.decrypt(line) for line in lines]

        with open(des, 'w', encoding=encoding) as f:
            f.write('\n'.join(lines))


def record(func=None, log_input=True, log_output=True, log_exception=True, logger=logging):
    '''裝飾器, 用於function定義上, 自動記錄傳入參數與傳出物件'''
    if func is None:
        return partial(record, log_input=True, log_output=True, log_exception=True, logger=logger)

    @wraps(func)
    def wrapper(*args, **kw):
        # 紀錄傳入參數
        if log_input:
            sig = signature(func)
            bound = sig.bind_partial(*args, **kw)
            bound.apply_defaults()
            logger.debug(f'{func.__name__} 傳入: {dict(bound.arguments)}')

        # 執行函數
        try:
            result = func(*args, **kw)
        # 紀錄報錯訊息, 紀錄後依舊拋出錯誤
        except Exception as e:
            if log_exception:
                log_trackback(logger=logger)
            raise e

        # 紀錄結果
        if log_output:
            logger.debug(f'{func.__name__} 返回: {result}')
        return result
    return wrapper


def log_trackback(*args, logger=logging):
    '''捕捉到錯誤時呼叫，能將完整報錯訊息打入紀錄檔'''
    logger.critical('\n' + traceback.format_exc())

# TODO: 快速建立基本logging模板
# TODO: 實作DataBaseLgger
