import sys
from smardapi.SmardApi_Class import SmardApi

initialized_instance = SmardApi()

sys.modules[__name__] = initialized_instance