from importlib import import_module
from pathlib import Path
import re


def load_dotenv(target, encoding='utf-8'):
    '''專案開始時呼叫，能讀取根目錄下env檔，將變數寫入環境變數中'''
    assert target in ['builtins', 'os'], 'target變數輸入錯誤，只允許 ["builtins", "os"]'

    p = Path('.env')

    if not p.exists():
        raise FileNotFoundError('找不到檔案：.env')

    lines = p.read_text(encoding=encoding)
    lines = re.split('\r?\n', lines)
    lines = filter(lambda x: '=' in x, lines)
    lines = map(lambda x: x.split('=', 1), lines)

    for key, value in lines:
        if target == 'builtins':
            module = import_module('builtins')
            setattr(module, key, value)
        elif target == 'os':
            module = import_module('os')
            module.environ[key] = value
