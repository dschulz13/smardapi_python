import sys
from .smardapi import SmardAPI

initialized_instance = SmardAPI()

sys.modules[__name__] = initialized_instance