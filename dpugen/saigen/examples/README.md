# dpugen Examples

**Usage:**

Just type the name of the file on the command-line, it will emit output to the console.

Example:

```
examples$ ./saigen-example-defaults.py
generating config
  Generating Vips ...
  Generating DirectionLookup ...
  Generating Vnets ...
  Generating Enis ...
  Generating address maps ...
  Generating OutboundRouting ...
  Generating Outbound CA to PA validation entry ...
    map:eni:5000
    map:eni:6000
[{'attributes': ['SAI_VIP_ENTRY_ATTR_ACTION', 'SAI_VIP_ENTRY_ACTION_ACCEPT'],
  'key': {'switch_id': '$SWITCH_ID', 'vip': '221.0.0.2'},
  'name': 'vip_#1',
  'op': 'create',
  'type': 'SAI_OBJECT_TYPE_VIP_ENTRY'},
 {'attributes': ['SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION',
                 'SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION'],
  'key': {'switch_id': '$SWITCH_ID', 'vni': '5000'},
  'name': 'direction_lookup_entry_#5000',
  'op': 'create',
  'type': 'SAI_OBJECT_TYPE_DIRECTION_LOOKUP_ENTRY'},
...
```

| File                                                               | Description            |
|--------------------------------------------------------------------|------------------------|
| [saigen-example-defaults.py](saigen-example-defaults.py)           | Generate SAI records using default parameters; minimal example |
| [saigen-example-params.py](saigen-example-params.py)               | Generate SAI records using custom scaling parameters                 | 