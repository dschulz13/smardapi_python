import sys
from smardapi.functions_classes import SmardApi

initialized_instance = SmardApi()

sys.modules[__name__] = initialized_instance