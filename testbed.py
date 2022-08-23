TESTBED = {
    'stateless': [
        {
            'server': [
                {'addr': '10.36.78.203', 'rest': 11010}
            ],
            'tgen':    [
                {
                    'type': 'keysight',
                    'interfaces': [
                        {'location': '10.36.79.165;9;1', 'fec': True, 'an': False, 'ieee': False},
                        {'location': '10.36.79.165;9;2', 'fec': True, 'an': False, 'ieee': False},
                        {'location': '10.36.79.165;9;3', 'fec': True, 'an': False, 'ieee': False},
                        {'location': '10.36.79.165;9;4', 'fec': True, 'an': False, 'ieee': False},
                        {'location': '10.36.79.165;9;5', 'fec': True, 'an': False, 'ieee': False},
                        {'location': '10.36.79.165;9;6', 'fec': True, 'an': False, 'ieee': False},
                        {'location': '10.36.79.165;9;7', 'fec': True, 'an': False, 'ieee': False},
                        {'location': '10.36.79.165;9;8', 'fec': True, 'an': False, 'ieee': False},
                    ]
                }
            ],
            'dpu':     [
                {
                    'type': 'sku',
                    'interfaces': [
                        ['10.36.79.120', 'fpg0'],
                        ['10.36.79.120', 'fpg4'],
                        ['10.36.79.120', 'fpg8'],
                        ['10.36.79.120', 'fpg12'],
                        ['10.36.79.120', 'fpg16'],
                        ['10.36.79.120', 'fpg20'],
                        ['10.36.79.120', 'fpg24'],
                        ['10.36.79.120', 'fpg28'],
                    ]
                }
            ],
        }
    ],
    'stateful': [
        {
            'server': [{'addr': '10.36.77.107', 'rest': 10010}],
            'tgen':    [
                {
                    'type': 'keysight',
                            'interfaces': [['10.36.77.102', 2, 1],    ['10.36.77.102', 3, 2]]
                }
            ],
            'vxlan': [{
                'tgen': [['10.36.77.105', 'Ethernet1'],    ['10.36.77.106', 'Ethernet1']],
                'dpu':[['10.36.77.105', 'Ethernet2'],    ['10.36.77.106', 'Ethernet2']],
            }],
            'dpu':     [
                {'type': 'sku',
                 'interfaces': [['10.36.77.104', 1],    ['10.36.77.104', 2]]}
            ],
        }
    ],
}
