import argparse
import collections
import io
import itertools
import json
import sys
import textwrap

# From https://stackoverflow.com/questions/12670395/json-encoding-very-long-iterators
# Other articles to consider:
# https://stackoverflow.com/questions/21663800/python-make-a-list-generator-json-serializable/31517812#31517812
# https://stackoverflow.com/questions/1871685/in-python-is-there-a-way-to-check-if-a-function-is-a-generator-function-before
# https://stackoverflow.com/questions/6416538/how-to-check-if-an-object-is-a-generator-object-in-python
# https://pypi.org/project/json-stream/
# https://pythonspeed.com/articles/json-memory-streaming/


def dumps_json(data, indent=2, depth=1):
    assert depth > 0
    space = ' '*indent
    s = json.dumps(data, indent=indent)
    lines = s.splitlines()
    N = len(lines)

    # determine which lines to be shortened
    def is_over_depth_line(i):
        return i in range(N) and lines[i].startswith(space*(depth + 1))

    def is_open_bracket_line(i):
        return not is_over_depth_line(i) and is_over_depth_line(i + 1)

    def is_close_bracket_line(i):
        return not is_over_depth_line(i) and is_over_depth_line(i - 1)

    def shorten_line(line_index):
        if not is_open_bracket_line(line_index):
            return lines[line_index]
        # shorten over-depth lines
        start = line_index
        end = start
        while not is_close_bracket_line(end):
            end += 1
        has_trailing_comma = lines[end][-1] == ','
        _lines = [lines[start][-1], *lines[start+1:end], lines[end].replace(',', '')]
        d = json.dumps(json.loads(' '.join(_lines)))
        return lines[line_index][:-1] + d + (',' if has_trailing_comma else '')
    #
    s = '\n'.join([
        shorten_line(i)
        for i in range(N) if not is_over_depth_line(i) and not is_close_bracket_line(i)
    ])
    #
    return s


class IterEncoder(json.JSONEncoder):
    '''
    JSON Encoder that encodes iterators as well.
    Write directly to file to use minimal memory
    '''
    class FakeListIterator(list):
        def __init__(self, iterable):
            self.iterable = iter(iterable)
            try:
                self.firstitem = next(self.iterable)
                self.truthy = True
            except StopIteration:
                self.truthy = False

        def __iter__(self):
            if not self.truthy:
                return iter([])
            return itertools.chain([self.firstitem], self.iterable)

        def __len__(self):
            raise NotImplementedError('Fakelist has no length')

        def __getitem__(self, item):
            raise NotImplementedError('Fakelist has no getitem')

        def __setitem__(self, item, value):
            raise NotImplementedError('Fakelist has no setitem')

        def __bool__(self):
            return self.truthy

    def default(self, o):
        if isinstance(o, collections.abc.Iterable):
            return type(self).FakeListIterator(o)
        return super().default(o)


def write_list_file_iterator(config, format, filename='<stdout>'):
    if filename == '<stdout>':
        write_list_file_pointer_iterator(config, format, sys.stdout)
    else:
        with io.open(filename, 'wt') as file_pointer:
            write_list_file_pointer_iterator(config, format, file_pointer)


def write_list_file_pointer_iterator(config, format, file_pointer):
    if format == 'json':
        json.dump(config, file_pointer, cls=IterEncoder, indent=2, separators=(',', ': '))
    elif format == 'vjson':
        ss = dumps_json(config)
        print(ss)
    else:
        raise NotImplementedError(f'ERROR: unsupported format {format}')
# TODO - consider generic recursive approach


def write_dict_file_iterator(config, format, filename='<stdout>'):
    def _write_dict_file_iterator(config, file_pointer):
        file_pointer.write('{\n')
        first = True
        for key, list in config.items():
            if not first:
                file_pointer.write(',\n')
            file_pointer.write(f'  "{key}":\n')
            json.dump(list, file_pointer, cls=IterEncoder, indent=2, separators=(',', ': '))
            first = False
        file_pointer.write('\n}\n')

    if format == 'json':
        print(f'Writing the {format} config to {filename}...', file=sys.stderr)
        if filename == '<stdout>':
            file_pointer = sys.stdout
            _write_dict_file_iterator(config, file_pointer)
        else:
            with io.open(filename, 'wt') as file_pointer:
                _write_dict_file_iterator(config, file_pointer)
    else:
        raise NotImplementedError(f'ERROR: unsupported format {format}')


def common_arg_parser():
    parser = argparse.ArgumentParser(
        description='Generate ___ Configs',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent('''
Usage:
=========
./generate.d.py                - generate output to stdout using uber-generator
./generate.d.py -o tmp.json    - generate output to file tmp.json
./generate.d.py -o /dev/null   - generate output to nowhere (good for testing)
./generate.d.py -c list        - generate just the list items w/o parent dictionary
___gen/aclgroups.py [options] - run one sub-generator, e.g. acls, routetables, etc.
                               - many different subgenerators available, support same options as uber-generator

Passing parameters. Provided as Python dict, see dflt_params.py for available items
Can use defaults; override from file; override again from cmdline (all 3 sources merged).
================
./generate.d.py -d                          - display default parameters and quit
./generate.d.py -d -P PARAMS                - use given parameters, display and quit; see dflt_params.py for template
./generate.d.py -d -p PARAM_FILE            - override with parameters from file; display only
./generate.d.py -d -p PARAM_FILE -P PARAMS  - override with params from file and cmdline; display only
./generate.d.py -p PARAM_FILE -P PARAMS     - override with params from file and cmdline; generate output

Examples:
./generate.d.py -d -p params_small.py -P '{'ENI_COUNT': 16}'  - use params_small.py but override ENI_COUNT; display params
./generate.d.py -p params_hero.py -o tmp.json                 - generate full 'hero test' scale config as json file
___gen/vpcmappingtypes.py -m -M 'Kewl Config!'                - generate dict of vpcmappingtypes, include meta with message

        ''')
    )

    # parser.add_argument('-f', '--format', choices=['json', 'yaml'], default='json',
    parser.add_argument('-f', '--format', choices=['json', 'vjson'], default='json',
                        help='Config output format.')

    # parser.add_argument('-c', '--content', choices=['dict', 'list'], default='list',
    #                     help='Emit dictionary (with inner lists), or list items only')

    parser.add_argument('-d', '--dump-params', action='store_true',
                        help='Just dump paramters (defaults with user-defined merged in')

    parser.add_argument('-m', '--meta', action='store_true',
                        help='Include metadata in output (only if "-c dict" used)')

    parser.add_argument('-M', '--msg', default='', metavar='"MSG"',
                        help='Put MSG in metadata (only if "-m" used)')

    parser.add_argument('-P', '--set-params', metavar='"{PARAMS}"',
                        help='use parameter dict from cmdline, partial is OK; overrides defaults & from file')

    parser.add_argument('-p', '--param-file', metavar='PARAM_FILE',
                        help='use parameter dict from file, partial is OK; overrides defaults')

    parser.add_argument(
        '-o', '--output', default='<stdout>', metavar='OFILE',
        help='Output file (default: standard output)')

    return parser


def common_parse_args(self):
    parser = common_arg_parser()
    self.args = parser.parse_args()

    # Prams from file override defaults; params from cmd-line override all
    params = {}
    if self.args.param_file:
        with io.open(self.args.param_file, 'r') as file_pointer:
            params = eval(file_pointer.read())
    if self.args.set_params:
        params.update(eval(self.args.set_params))
    self.merge_params(params)

    if self.args.dump_params:
        print(self.params_dict)
        sys.exit()


def common_output(self):
    # import pdb
    # pdb.set_trace()
    # if self.args.content == 'dict':
    #     d = self.toDict()
    #     if (self.args.meta):
    #         d.update(self.get_meta(self.args.msg))
    #     # streaming dict output:
    #     write_dict_file_iterator(d, self.args.format, self.args.output)

    # elif self.args.content == 'list':
    #     # streaming list output:
    write_list_file_iterator(self.items(), self.args.format, self.args.output)
    # else:
    #     raise Exception('Unknown content specifier: '%s'' % self.args.content)


def common_main(self):
    common_parse_args(self)
    common_output(self)
