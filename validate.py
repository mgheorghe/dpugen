import json
import os

from yangson import DataModel

os.chdir(r'/home/mircea/cgyang/models')


dm = DataModel()

print(dm.ascii_tree(), end='')


with open('/home/mircea/cgyang/test_data.json') as infile:
    ri = json.load(infile)
inst = dm.from_raw(ri)

print(inst.validate())
