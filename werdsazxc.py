from Crypto.Cipher import AES
import logging
import pickle
import yaml
import json
logger = logging.getLogger('robot')


class FileHandler:
    '''各種檔案格式存讀'''
    @classmethod
    def load_pickle(cls, file_path):
        with open(file_path, 'rb') as f:
            return cls(pickle.load(f))
    def dump_pickle(self, file_path):
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load_json(cls, file_path, **kwargs):
        with open(file_path, 'r', **kwargs) as f:
            return cls(json.load(f))
    def dump_json(self, file_path, **kwargs):
        with open(file_path, 'w', **kwargs) as f:
            json.dump(self, f)

    @classmethod
    def load_yaml(cls, file_path, Loader=yaml.CFullLoader, **kwargs):
        with open(file_path, 'r', **kwargs) as f:
            return cls(yaml.load(f, Loader))
    def dump_yaml(self, file_path, **kwargs):
        with open(file_path, 'w', **kwargs) as f:
            yaml.dump(self, f)

    def __getstate__(self):
        return vars(self)

    def __setstate__(self, state):
        vars(self).update(state)


class Dict(dict, FileHandler):
    '''JS Like Dict, 提供attribute的方式取值'''
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
    '''加解密物件, 使用AES_CBC方法, 適用於任何jsonable物件'''
    def __init__(self, password: bytes, mode=AES.MODE_CFB,
                 IV_SIZE: int=16, KEY_SIZE: int=16, SALT_SIZE: int=16):
        password = password * KEY_SIZE
        self.password = password[:KEY_SIZE]
        self.mode = mode
        self.IV_SIZE = IV_SIZE
        self.KEY_SIZE = KEY_SIZE
        self.SALT_SIZE = SALT_SIZE

    def cryptor(self, salt):
        import hashlib

        if salt:
            derived = hashlib.pbkdf2_hmac('sha256', self.password, salt, 100000, dklen=self.IV_SIZE + self.KEY_SIZE)
            iv = derived[:self.IV_SIZE]
            key = derived[self.IV_SIZE:]
            cryptor = AES.new(key, self.mode, iv)
        else:
            cryptor = AES.new(self.password, self.mode, self.password)

        return cryptor

    def encrypt(self, s, salt=False) -> str:
        '''加密, 傳入為任意jsonable物件, 返回加密文字'''
        import base64
        import json

        s = json.dumps(s)
        s = s.encode()

        if salt:
            salt = ''.join([chr(random.randint(0,255))] for i in range(self.SALT_SIZE)).encode()
            s = salt + self.cryptor(salt).encrypt(s)
        else:
            s = self.cryptor(salt).encrypt(s)

        s = base64.b64encode(s)

        s = s.decode()
        return s

    def decrypt(self, s: str, salt=False):
        '''解密, 傳入為加密文字, 傳出為解密後物件'''
        import base64
        import json

        s = s.encode()

        s = base64.b64decode(s)

        if salt:
            salt = s[:self.SALT_SIZE]
            s = self.cryptor(salt).decrypt(s[self.SALT_SIZE:])
        else:
            s = self.cryptor(salt).decrypt(s)

        s = s.decode()
        s = json.loads(s)
        return s


class EncryptFormatter(logging.Formatter):
    '''紀錄檔加解密功能'''
    ENCRYPT_SPLITTER = '//T//'
    def __init__(self, key=b'1234', salt=False, *args, **kw):
        super().__init__(*args, **kw)
        self.encryptor = Cryptor(key)
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


def log(func=None, logger=logger):
    '''裝飾器, 用於function定義上, 自動記錄傳入參數與傳出物件'''
    from functools import wraps, partial
    from inspect import signature

    if func is None:
        return partial(log, logger=logger)

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
            log_trackback()
            raise e

        # 紀錄結果
        logger.debug(f'{func.__name__} 返回: {result}')
        return result
    return wrapper


def log_trackback(*args):
    '''捕捉到錯誤時呼叫，能將完整報錯訊息打入紀錄檔'''
    import traceback

    logger.critical('\n' + traceback.format_exc())


def load_dotenv():
    '''專案開始時呼叫，能讀取根目錄下env檔，將變數寫入環境變數中'''
    from pathlib import Path
    import builtins

    p = Path('.env')
    if not p.exists():
        raise FileNotFoundError('找不到檔案：.env')
    for line in p.read_text(encoding='utf-8').split('\n'):
        if '=' not in line:
            continue
        line = line.split('=')
        key = line[0]
        value = '='.join(line[1:])
        setattr(builtins, key, value)
