import ipaddress
import pprint
from abc import (
    ABC,
    abstractmethod
)
from copy import deepcopy
from datetime import datetime

import macaddress
from munch import DefaultMunch

from dashgen.dflt_params import dflt_params

ipa = ipaddress.ip_address  # optimization so the . does not get executed multiple times
maca = macaddress.MAC       # optimization so the . does not get executed multiple times


class ConfBase(ABC):

    def __init__(self, params=None, defaults=None):
        self.dflt_params = deepcopy(defaults if defaults is not None else dflt_params)
        self.cooked_params = {}
        params = params or {}
        self.merge_params(params)
        self.num_yields = 0

    def merge_params(self, params):
        # Merge provided params into/onto defaults
        self.params_dict = deepcopy(self.dflt_params)
        self.params_dict.update(params)

        # make scalar attributes for speed & brevity (compared to dict)
        # https://stackoverflow.com/questions/1305532/how-to-convert-a-nested-python-dict-to-object
        self.cook_params()
        self.params = DefaultMunch.fromDict(self.params_dict)
        # print ('%s: self.params=' , self.params)
        self.cooked_params = DefaultMunch.fromDict(self.cooked_params_dict)
        # print ("cooked_params = ", self.cooked_params)

    def cook_params(self):
        self.cooked_params_dict = {}
        for ip in [
            'IP_STEP1',
            'IP_STEP_ENI',
            'IP_STEP_NSG',
            'IP_STEP_ACL',
            'IP_STEPE'
        ]:
            self.cooked_params_dict[ip] = int(ipa(self.params_dict[ip]))
        for ip in [
            'IP_L_START',
            'IP_R_START',
            'PAL',
            'PAR'
        ]:
            self.cooked_params_dict[ip] = ipa(self.params_dict[ip])
        for mac in [
            'MAC_L_START',
            'MAC_R_START'
        ]:
            self.cooked_params_dict[mac] = maca(self.params_dict[mac])

    @abstractmethod
    def items(self):
        pass

    # expensive - runs generator
    def item_count(self):
        return len(self.items())

    def items_generated(self):
        ''' Last count of # yields, reset each time at beginning'''
        return self.num_yields

    def get_params(self):
        return self.params_dict

    def get_meta(self, message=''):
        '''Generate metadata. For reference, could also add e.g. data to help drive tests'''
        return {
            'meta': {
                'tstamp': datetime.now().strftime('%m/%d/%Y, %H:%M:%S'),
                'msg': message,
                'params': self.get_params()
            }
        }

    def pretty(self):
        pprint.pprint(self.toDict())
