from Crypto.Cipher import AES
import hashlib
import base64
import random
import json


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


