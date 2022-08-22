

TESTDATA = {
    "DEVICE_METADATA": {
        "localhost": {
            # "subtype": "Appliance",
            # "type": "SonicHost",
            # "switch_type": "dpu",
            # "sub_role": "None",
            "mac": "4c:76:25:f4:70:82",
            "bgp_asn": 100,
            "flow_timer": 1
        }
    },

    ### UNDERLAY SECTION from SONiC schema ###

    "INTERFACE": {
        # "Ethernet8|10.0.0.4/31": {}, https://github.com/sonic-net/SONiC/blob/master/doc/config_db.json
        "Ethernet0": {
            "ipv4": {
                "address": "220.0.1.1",
                "gwaddr": "220.0.1.2",  # TODO: tgen has eni count Ip's
                "prefix": 32
            }
        },
        "Ethernet4": {
            "ipv4": {
                "address": "220.0.2.1",
                "gwaddr": "220.0.2.2",  # TODO: tgen has eni count Ip's
                "prefix": 32
            }
        }
    },

    "LOOPBACK_INTERFACE": {
        # "Loopback0|10.1.0.32/32": {} https://github.com/sonic-net/SONiC/blob/master/doc/config_db.json
        "Loopback0": {
            "ipv4": {
                "address": "221.0.0.2",
                "prefix": 32
            }
        }
    },

    # https://github.com/sonic-net/SONiC/blob/master/doc/config_db.json
    "BGP_NEIGHBOR": {
        "220.0.1.2": {
            "local_addr": "220.0.1.1",
            "asn": 200
        },
        "220.0.2.2": {
            "local_addr": "220.0.2.1",
            "asn": 200
        }
    },

    # https://github.com/sonic-net/SONiC/blob/master/doc/vrf/sonic-vrf-hld.md
    "STATIC_ROUTE": {
        # TODO find a way to define 8 + 8 of those
        "221.0.1.1/32": {
            "nexthop": "220.0.1.2",
            "ifname": "Ethernet0"
        },
    },


    ### OVERLAY SECTION from SONiC-DASH schema https://github.com/Azure/DASH/blob/main/documentation/general/design/dash-sonic-hld.md ###

    # DASH_VNET:{{vnet_name}} 
    "DASH_VNET": {
        "name": "vnet",
        "vni": {
            "increment": {
                "start": 11,
                "step": 1,
                "count": 8  # TODO: copy count from eni count or make variables
            }
        }
    },

    # DASH_ENI:{{eni}} 
    "DASH_ENI": {
        "name": {
            "increment": {
                "base": "vnet",
                "start": 1,
                "step": 1,
                "count": 8  # TODO: copy count from eni count or make variables
            }
        },
        "eni_id": {  # supports: increment
            "increment": {
                "start": 1,
                "step": 1,
                "count": 8  # TODO: copy count from eni count or make variables
            }
        },
        "mac_address": {  # supports: increment
            "increment": {
                "start": "00:1A:C5:00:00:01",
                "step": "00:00:00:18:00:00",
                "count": 8  # TODO: copy count from eni count or make variables
            }
        },
        "underlay_ip": {  # supports: increment
            "increment": {
                "start": "1.1.0.1",
                "step": "1.0.0.0",
                "count": 8  # TODO: copy count from eni count or make variables
            }
        },
        "vnet": {  # supports: increment
            "substitution": {
                "base": "vnet#{0}abc-#{1}",
                "params": [
                    {
                        "start": 1,
                        "step": 1,
                        "count": 4  # TODO: copy count from eni count or make variables
                    },
                    {
                        "values": ["a", "b", "x"],
                    }
                ],
                "count": 8
            }
        }
    },

    # DASH_VNET_MAPPING_TABLE:{{vnet}}:{{ip_address}} 
    "SCALE_DASH_VNET_MAPPING_TABLE": {
        "vnet": {  # supports: increment
            "increment": {
                "base": "vnet",
                "start": 1,
                "step": 1,
                "count": 8  # TODO: copy count from eni count or make variables
            }
        },
        "ip_address": {
            "increment": {
                "start": "1.128.0.1",
                "eni_step": "1.0.0.0",  # TODO: get count from eni count or make variables
                "nsg_step": "0.4.0.0",  # TODO: get count from nsg count or make variables
                "acl_step": "0.0.2.0",  # TODO: get count from acl count or make variables
                "step": "0.0.0.1",
                "count": 40
            }
        },
        "underlay_ip": {
            "increment": {
                "start": "221.0.2.1",
                "step": "0.0.0.1",
                "count": 8  # TODO: copy count from eni count or make variables
            }
        },
        "mac_address": {
            "increment": {
                "start": "00:1B:6E:00:00:01",
                "step": "1.0.0.0",
                "count": 8  # TODO: copy count from eni count or make variables
            }
        },
    },

    # DASH_ACL_IN:{{eni}}:{{stage}}
    "DASH_ACL_IN": {
        "stage": {
            "increment": {
                "start": 1,
                "step": 1,
                "count": 3
            }
        },
        "ipv4": {
            "increment": {
                "step": '0.4.0.0'
            }
        }
    },

    # DASH_ACL_OUT:{{eni}}:{{stage}}
    "DASH_ACL_OUT": {
        "stage": {
            "increment": {
                "start": 1,
                "step": 1,
                "count": 3
            }
        }
        mac:
    },

    # DASH_ACL_RULE:{{group_id}}:{{rule_num}}
    "DASH_ACL_RULE": {
        "priority": {
            "increment": {
                "start": 1,
                "step": 1,
                "count": 1000
            }
        },
        "action": {  # supports: values
            "values": ["allow", "deny"]
        },
        "terminating": {  # supports: values
            "values": [True, False]
        },
        "protocol": [],
        "src_addr": {
            "increment": {
                "start": "from acl grp and eni",
                "step": '0.0.0.1',
                "count": 200
            }
        },
        "dst_addr": {
            "increment": {
                "step": '0.0.0.1',
                "count": 200
            }
        },
        "src_port": [],
        "dst_port": [],
    },

    # DASH_ROUTE_TABLE:{{eni}}:{{prefix}} 
    "DASH_ROUTE_TABLE": {
        "eni": "",
        "prefix": "",
        "action_type": "{{routing_type}} ",
        "vnet": "{{vnet_name}} (OPTIONAL)",
        "appliance": "{{appliance_id}} (OPTIONAL)",
        "overlay_ip": "{{ip_address}} (OPTIONAL)",
        "underlay_ip": "{{ip_address}} (OPTIONAL)",
        "overlay_sip": "{{ip_address}} (OPTIONAL)",
        "underlay_dip": "{{ip_address}} (OPTIONAL)",
        "metering_bucket": "{{bucket_id}} (OPTIONAL) ",
    },

    # DASH_ROUTE_RULE_TABLE:{{eni}}:{{vni}}:{{prefix}} 
    "DASH_ROUTE_RULE_TABLE": {
        "eni": "",
        "vni": "",
        "prefix": "",
        "action_type": "{{routing_type}} ",
        "priority": "{{priority}}",
        "protocol": "{{protocol_value}} (OPTIONAL)",
        "vnet": "{{vnet_name}} (OPTIONAL)",
        "pa_validation": "{{bool}} (OPTIONAL)",
        "metering_bucket": "{{bucket_id}} (OPTIONAL) ",
    }

}
