import abc
import sys
import os
import json

import mnos

class Module(abc.ABC):
    def __init__(self, **kwargs):
        self.mnos = mnos.mnos

        module_file = sys.modules[self.__module__].__file__
        self._module_dir = os.path.dirname(module_file)

        with open(os.path.join(self._module_dir, "moduleinfo.json")) as f:
            self.module_info = json.load(f)

    @abc.abstractmethod
    def install(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def teardown(self):
        pass
