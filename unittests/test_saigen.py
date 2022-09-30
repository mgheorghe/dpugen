import json
from pathlib import Path

import pytest

current_file_dir = Path(__file__).parent

# Constants
SWITCH_ID = 5


class TestSaigen:

    # @pytest.mark.parametrize("config_file", ['vnet_outbound_simple', 'vnet_outbound_scale'])
    @pytest.mark.parametrize("config_file", ['vnet_outbound_simple'])
    def test_(self, confgen, config_file):

        with (current_file_dir / f'{config_file}_in.json').open(mode='r') as in_file:
            in_commands = json.load(in_file)

        with (current_file_dir / f'{config_file}_out.json').open(mode='r') as out_file:
            out_commands_exp = json.load(out_file)

        confgen.mergeParams(in_commands)
        confgen.generate()
        out_commands = list(confgen.items())

        print("OUT commands generated:")
        for item in out_commands:
            print(f"name: {item['name']}, type: {item['type']}")

        print("OUT commands expected:")
        for item in out_commands_exp:
            print(f"name: {item['name']}, type: {item['type']}")

        # pytest.set_trace()
        assert len(out_commands) == len(out_commands_exp), "Unexpected number of generated commands."

        for gen, exp in zip(out_commands, out_commands_exp):
             assert gen == exp
