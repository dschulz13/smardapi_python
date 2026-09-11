import sys
from smardapi.functions_classes import SmardAPI

initialized_instance = SmardAPI()

sys.modules[__name__] = initialized_instance