import json
from pathlib import Path

import pytest

from dpugen import sai

current_file_dir = Path(__file__).parent

# Constants
SWITCH_ID = 5


class TestSaigen:

    @pytest.mark.parametrize("config_file", ['vnet_outbound_simple', 'vnet_outbound_scale'])
    def test_(self, config_file):

        with (current_file_dir / f'{config_file}_in.json').open(mode='r') as in_file:
            in_commands = json.load(in_file)

        with (current_file_dir / f'{config_file}_out.json').open(mode='r') as out_file:
            out_commands_exp = json.load(out_file)

        confgen = sai.SaiConfig()
        confgen.merge_params(in_commands)
        confgen.generate()
        out_commands = list(confgen.items())

        print('OUT commands generated:')
        for item in out_commands:
            print(f"name: {item['name']}, type: {item['type']}")
        
        import io
        with io.open(f'C:/github-keysight/dpugen/unittests/{config_file}-gen.json','wt',encoding='ascii') as f:
            f.write(json.dumps(out_commands, indent=2))

        print('OUT commands expected:')
        for item in out_commands_exp:
            print(f"name: {item['name']}, type: {item['type']}")

        # pytest.set_trace()
        assert len(out_commands) == len(out_commands_exp), 'Unexpected number of generated commands.'

        for gen, exp in zip(out_commands, out_commands_exp):
            assert gen == exp
