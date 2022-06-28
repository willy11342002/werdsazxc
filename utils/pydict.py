import pickle
import yaml
import json


class FileDict(dict):
    '''各種檔案格式存讀'''
    @classmethod
    def load_pickle(cls, file_path, file_kwargs={}, pickle_kwargs={}):
        with open(file_path, 'rb', **file_kwargs) as f:
            return cls(pickle.load(f, **pickle_kwargs))

    def dump_pickle(self, file_path, file_kwargs={}, pickle_kwargs={}):
        with open(file_path, 'wb', **file_kwargs) as f:
            pickle.dump(self, f, **pickle_kwargs)

    @classmethod
    def load_json(cls, file_path, file_kwargs={}, json_kwargs={}):
        with open(file_path, 'r', **file_kwargs) as f:
            return cls(json.load(f, **json_kwargs))

    def dump_json(self, file_path, file_kwargs={}, json_kwargs={}):
        with open(file_path, 'w', **file_kwargs) as f:
            json.dump(self, f, **json_kwargs)

    @classmethod
    def load_yaml(cls, file_path, file_kwargs={}, yaml_kwargs={'Loader': yaml.Loader}):
        with open(file_path, 'r', **file_kwargs) as f:
            return cls(yaml.load(f, **yaml_kwargs))

    def dump_yaml(self, file_path, file_kwargs={}, yaml_kwargs={'Dumper': yaml.Dumper}):
        with open(file_path, 'w', **file_kwargs) as f:
            yaml.dump(self, f, **yaml_kwargs)

    def __getstate__(self):
        return vars(self)

    def __setstate__(self, state):
        vars(self).update(state)


class JSDict(dict):
    '''JS Like Dict, 提供attribute的方式取值'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = JSDict(value)
            if type(value) == list:
                self[key] = [
                    JSDict(v) if isinstance(v, dict) else v
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


class Dict(FileDict, JSDict):
    pass
