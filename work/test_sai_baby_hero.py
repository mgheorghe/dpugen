# generate using saigen config.sai-baby-hero.json
# copy config.sai-baby-hero.json and this python script in https://github.com/sonic-net/DASH/tree/main/test/test-cases/functional/saic
# run it

import ipaddress
import json
import sys
import time
from pathlib import Path
from pprint import pprint

import macaddress
import pytest
from munch import DefaultMunch

sys.path.append("../utils")
import snappi_utils as su

ipa = ipaddress.ip_address  # optimization so the . does not get executed multiple times
maca = macaddress.MAC       # optimization so the . does not get executed multiple times

current_file_dir = Path(__file__).parent

"""
This covers following scenario :

Test vnet to vnet communication with ACL on outbound direction:
1. Configure DUT to deny and allow traffic
2. Configure TGEN traffic flow as one vnet to another vnet of two OpenTrafficGenerator ports
3. Verify Traffic denied through deny traffic IPs

Topology Used :

       --------          -------          -------- 
      |        |        |       |        |        |
      |        |        |       |        |        |
      |  TGEN  |--------|  DUT  |--------|  TGEN  |
      |        |        |       |        |        |
      |        |        |       |        |        |
       --------          -------          -------- 
       
"""

###############################################################
#                  Declaring Global variables
###############################################################

TOTALPACKETS = 1000
PPS = 1000
TRAFFIC_SLEEP_TIME = (TOTALPACKETS / PPS) + 10
PACKET_LENGTH = 128


# copy paste from github\dpugen\dpugen\saigen\dflt_params.py
dflt_params = {                        # CONFIG VALUE             # DEFAULT VALUE
    'SCHEMA_VER':                      '0.0.2',

    'DC_START':                        '220.0.1.1',                # '220.0.1.2'
    'DC_STEP':                         '0.0.1.0',                  # '0.0.1.0'

    'LOOPBACK':                        '221.0.0.1',                # '221.0.0.1'
    'PAL':                             '221.1.0.1',                # '221.1.0.1'
    'PAR':                             '221.2.0.1',                # '221.2.0.1'

    'ENI_START':                        1,                         # 1
    'ENI_COUNT':                        8,                         # 64
    'ENI_MAC_STEP':                     '00:00:00:18:00:00',       # '00:00:00:18:00:00'
    'ENI_STEP':                         1,                         # 1
    'ENI_L2R_STEP':                     1000,                      # 1000

    'VNET_PER_ENI':                     1,                         # 16 TODO: partialy implemented

    'MAC_L_START':                      '00:1A:C5:00:00:01',
    'MAC_R_START':                      '00:1B:6E:00:00:01',

    'IP_L_START':                       '1.1.0.1',               # local, eni
    'IP_R_START':                       '1.4.0.1',               # remote, the world

    'ACL_NSG_COUNT':                    5,                       # 5 (per direction per ENI)
    'ACL_RULES_NSG':                    10,                      # 1000
    'IP_PER_ACL_RULE':                  4,                       # 128
    # 128 (must be equal with IP_PER_ACL_RULE) TODO: not implemented
    'IP_MAPPED_PER_ACL_RULE':           4,
    'IP_ROUTE_DIVIDER_PER_ACL_RULE':    2,                       # 16 (must be 2^N)

    'ACL_NSG_MAC_STEP':                 '00:00:00:02:00:00',
    'ACL_POLICY_MAC_STEP':              '00:00:00:00:01:00',

    'IP_STEP1':                         '0.0.0.1',
    'IP_STEP_ENI':                      '0.64.0.0',
    'IP_STEP_NSG':                      '0.2.0.0',
    'IP_STEP_ACL':                      '0.0.1.0',
    'IP_STEPE':                         '0.0.0.2',

}
# end of copy paste

p = DefaultMunch.fromDict(dflt_params)

UNDERLAY_SRC_MAC = "80:09:02:01:00:01"
UNDERLAY_DST_MAC = "00:00:00:00:00:00"


###############################################################
#                  Start of the testcase
###############################################################

class TestDpuGen:

    @pytest.fixture(scope="class")
    def setup_config(self):
        current_file_dir = Path(__file__).parent
        with (current_file_dir / 'config.sai-baby-hero.json').open(mode='r') as config_file:
            setup_commands = json.load(config_file)
        return setup_commands

    def test_setup(self, dpu, setup_config):
        results = [*dpu.process_commands(setup_config)]
        print("\n======= SAI setup commands RETURN values =======")
        pprint(results)
        assert all(results), "Setup error"

    def test_udp_outbound(self, dataplane):

        flows = []

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            vtep_local = str(ipa(p.PAL) + int(ipa(p.IP_STEP1)) * eni_index)
            eni_ip = str(ipa(p.IP_L_START) + eni_index * int(ipa(p.IP_STEP_ENI)))
            eni_mac = str(
                maca(
                    int(maca(p.MAC_L_START)) +
                    eni_index * int(maca(p.ENI_MAC_STEP))
                )
            ).replace('-', ':')

            for nsg_index in range(1, (p.ACL_NSG_COUNT*2+1)):
                remote_ip = str(ipa(p.IP_R_START) + eni_index * int(ipa(p.IP_STEP_ENI)) + (nsg_index - 1) * int(ipa(p.IP_STEP_NSG)))

                if (eni % 4) == 1:

                    remote_mac = str(
                        maca(
                            int(maca(p.MAC_R_START)) +
                            eni_index * int(maca(p.ENI_MAC_STEP)) +
                            (nsg_index - 1) * int(maca(p.ACL_NSG_MAC_STEP))
                        )
                    ).replace('-', ':')

                    # Flow1 settings
                    flow = dataplane.configuration.flows.flow(name="OUT-ENI%d-NSG%d" % (eni, nsg_index))[-1]
                    flow.tx_rx.port.tx_name = dataplane.configuration.ports[0].name
                    flow.tx_rx.port.rx_name = dataplane.configuration.ports[1].name
                    flow.size.fixed = PACKET_LENGTH
                    # send n packets and stop
                    flow.duration.fixed_packets.packets = TOTALPACKETS
                    # send n packets per second
                    flow.rate.pps = PPS
                    flow.metrics.enable = True

                    under_eth, under_ip, under_udp, vxlan, over_eth, over_ip, over_udp = (
                        flow.packet.ethernet().ipv4().udp().vxlan().ethernet().ipv4().udp()
                    )

                    under_eth.src.value = UNDERLAY_SRC_MAC
                    under_eth.dst.value = UNDERLAY_DST_MAC
                    under_eth.ether_type.value = 2048

                    under_ip.src.value = vtep_local  # ENI - VTEP
                    under_ip.dst.value = p.LOOPBACK  # DPU - VTEP

                    under_udp.src_port.value = 11638
                    under_udp.dst_port.value = 4789

                    # vxlan.flags.value =
                    vxlan.vni.value = eni
                    vxlan.reserved0.value = 0
                    vxlan.reserved1.value = 0

                    print('%s - %s' % (remote_mac, remote_ip))
                    over_eth.src.value = eni_mac
                    over_eth.dst.increment.start = remote_mac
                    over_eth.dst.increment.step = p.ACL_POLICY_MAC_STEP
                    over_eth.dst.increment.count = (p.ACL_RULES_NSG // 2)

                    over_ip.src.value = eni_ip  # ENI
                    # over_ip.dst.value = p.IP_R_START  # world
                    over_ip.dst.increment.start = remote_ip
                    over_ip.dst.increment.step = p.IP_STEP_ACL
                    over_ip.dst.increment.count = (p.ACL_RULES_NSG // 2)

                    over_udp.src_port.value = 10000
                    over_udp.dst_port.value = 20000

                else:

                    remote_mac = str(
                        maca(
                            int(maca(p.MAC_R_START)) +
                            eni_index * int(maca(p.ENI_MAC_STEP))
                        )
                    ).replace('-', ':')

                    # Flow1 settings
                    flow = dataplane.configuration.flows.flow(name="OUT-ENI%d-NSG%d" % (eni, nsg_index))[-1]
                    flow.tx_rx.port.tx_name = dataplane.configuration.ports[0].name
                    flow.tx_rx.port.rx_name = dataplane.configuration.ports[1].name
                    flow.size.fixed = PACKET_LENGTH
                    # send n packets and stop
                    flow.duration.fixed_packets.packets = TOTALPACKETS
                    # send n packets per second
                    flow.rate.pps = PPS
                    flow.metrics.enable = True

                    under_eth, under_ip, under_udp, vxlan, over_eth, over_ip, over_udp = (
                        flow.packet.ethernet().ipv4().udp().vxlan().ethernet().ipv4().udp()
                    )

                    under_eth.src.value = UNDERLAY_SRC_MAC
                    under_eth.dst.value = UNDERLAY_DST_MAC
                    under_eth.ether_type.value = 2048

                    under_ip.src.value = vtep_local  # ENI - VTEP
                    under_ip.dst.value = p.LOOPBACK  # DPU - VTEP

                    under_udp.src_port.value = 11638
                    under_udp.dst_port.value = 4789

                    # vxlan.flags.value =
                    vxlan.vni.value = eni
                    vxlan.reserved0.value = 0
                    vxlan.reserved1.value = 0

                    over_eth.src.value = eni_mac
                    over_eth.dst.value = remote_mac

                    over_ip.src.value = eni_ip  # ENI
                    # over_ip.dst.value = p.IP_R_START  # world
                    over_ip.dst.increment.start = remote_ip
                    over_ip.dst.increment.step = p.IP_STEP_ACL
                    over_ip.dst.increment.count = (p.ACL_RULES_NSG // 2)

                    over_udp.src_port.value = 10000
                    over_udp.dst_port.value = 20000

                flows.append(flow)

        dataplane.set_config()

        # import pdb
        # pdb.set_trace()
        # print(flows[0].packet)

        print('Starting transmit on all configured flows ...')
        ts = dataplane.api.transmit_state()
        ts.state = ts.START
        dataplane.api.set_transmit_state(ts)

        print('Checking metrics on all configured ports ...')
        print('Expected\tTotal Tx\tTotal Rx')
        assert wait_for(lambda: metrics_ok(dataplane.api)), 'Metrics validation failed!'

        dataplane.teardown()

    def test_udp_inbound(self, dataplane):

        flows = []

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            vtep_remote = str(ipa(p.PAR) + int(ipa(p.IP_STEP1)) * eni_index)
            eni_ip = str(ipa(p.IP_L_START) + eni_index * int(ipa(p.IP_STEP_ENI)))
            eni_mac = str(
                maca(
                    int(maca(p.MAC_L_START)) +
                    eni_index * int(maca(p.ENI_MAC_STEP))
                )
            ).replace('-', ':')

            for nsg_index in range(1, (p.ACL_NSG_COUNT*2+1)):
                remote_ip = str(ipa(p.IP_R_START) + eni_index * int(ipa(p.IP_STEP_ENI)) + (nsg_index - 1) * int(ipa(p.IP_STEP_NSG)))

                if (eni % 4) == 1:

                    remote_mac = str(
                        maca(
                            int(maca(p.MAC_R_START)) +
                            eni_index * int(maca(p.ENI_MAC_STEP)) +
                            (nsg_index - 1) * int(maca(p.ACL_NSG_MAC_STEP))
                        )
                    ).replace('-', ':')

                    # Flow1 settings
                    flow = dataplane.configuration.flows.flow(name="IN-ENI%d-NSG%d" % (eni, nsg_index))[-1]
                    flow.tx_rx.port.tx_name = dataplane.configuration.ports[1].name
                    flow.tx_rx.port.rx_name = dataplane.configuration.ports[0].name
                    flow.size.fixed = PACKET_LENGTH
                    # send n packets and stop
                    flow.duration.fixed_packets.packets = TOTALPACKETS
                    # send n packets per second
                    flow.rate.pps = PPS
                    flow.metrics.enable = True

                    under_eth, under_ip, under_udp, vxlan, over_eth, over_ip, over_udp = (
                        flow.packet.ethernet().ipv4().udp().vxlan().ethernet().ipv4().udp()
                    )

                    under_eth.src.value = UNDERLAY_SRC_MAC
                    under_eth.dst.value = UNDERLAY_DST_MAC
                    under_eth.ether_type.value = 2048

                    under_ip.src.value = vtep_remote  # ENI - VTEP
                    under_ip.dst.value = p.LOOPBACK  # DPU - VTEP

                    under_udp.src_port.value = 11638
                    under_udp.dst_port.value = 4789

                    vxlan.vni.value = (eni + p.ENI_L2R_STEP)
                    vxlan.reserved0.value = 0
                    vxlan.reserved1.value = 0

                    over_eth.src.increment.start = remote_mac
                    over_eth.src.increment.step = p.ACL_POLICY_MAC_STEP
                    over_eth.src.increment.count = p.ACL_RULES_NSG

                    over_eth.dst.value = eni_mac

                    over_ip.src.increment.start = remote_ip
                    over_ip.src.increment.step = p.IP_STEP_ACL
                    over_ip.src.increment.count = p.ACL_RULES_NSG

                    over_ip.dst.value = eni_ip  # ENI

                    over_udp.src_port.value = 10000
                    over_udp.dst_port.value = 20000

                else:

                    remote_mac = str(
                        maca(
                            int(maca(p.MAC_R_START)) +
                            eni_index * int(maca(p.ENI_MAC_STEP))
                        )
                    ).replace('-', ':')

                    # Flow1 settings
                    flow = dataplane.configuration.flows.flow(name="OUT-ENI%d-NSG%d" % (eni, nsg_index))[-1]
                    flow.tx_rx.port.tx_name = dataplane.configuration.ports[1].name
                    flow.tx_rx.port.rx_name = dataplane.configuration.ports[0].name
                    flow.size.fixed = PACKET_LENGTH
                    # send n packets and stop
                    flow.duration.fixed_packets.packets = TOTALPACKETS
                    # send n packets per second
                    flow.rate.pps = PPS
                    flow.metrics.enable = True

                    under_eth, under_ip, under_udp, vxlan, over_eth, over_ip, over_udp = (
                        flow.packet.ethernet().ipv4().udp().vxlan().ethernet().ipv4().udp()
                    )

                    under_eth.src.value = UNDERLAY_SRC_MAC
                    under_eth.dst.value = UNDERLAY_DST_MAC
                    under_eth.ether_type.value = 2048

                    under_ip.src.value = vtep_remote  # ENI - VTEP
                    under_ip.dst.value = p.LOOPBACK  # DPU - VTEP

                    under_udp.src_port.value = 11638
                    under_udp.dst_port.value = 4789

                    # vxlan.flags.value =
                    vxlan.vni.value = (eni + p.ENI_L2R_STEP)
                    vxlan.reserved0.value = 0
                    vxlan.reserved1.value = 0

                    over_eth.src.value = remote_mac
                    over_eth.dst.value = eni_mac

                    # over_ip.dst.value = p.IP_R_START  # world
                    over_ip.src.increment.start = remote_ip
                    over_ip.src.increment.step = p.IP_STEP_ACL
                    over_ip.src.increment.count = p.ACL_RULES_NSG

                    over_ip.dst.value = eni_ip  # ENI

                    over_udp.src_port.value = 10450
                    over_udp.dst_port.value = 20450

                flows.append(flow)

        dataplane.set_config()

        print('Starting transmit on all configured flows ...')
        ts = dataplane.api.transmit_state()
        ts.state = ts.START
        dataplane.api.set_transmit_state(ts)

        print('Checking metrics on all configured ports ...')
        print('Expected\tTotal Tx\tTotal Rx')
        assert wait_for(lambda: metrics_ok(dataplane.api)), 'Metrics validation failed!'

        dataplane.teardown()

    def test_cleanup(self, dpu, setup_config):

        cleanup_commands = []
        for command in reversed(setup_config):
            command['op'] = 'remove'
            cleanup_commands.append(command)

        results = []
        for command in cleanup_commands:
            results.append(dpu.command_processor.process_command(command))
        print(results)
        print("\n======= SAI teardown commands RETURN values =======")
        assert all([x == 0 for x in results]), "Teardown Error"


def metrics_ok(api):
    # create a port metrics request and filter based on port names
    cfg = api.get_config()

    req = api.metrics_request()
    req.port.port_names = [p.name for p in cfg.ports]
    #import pdb;pdb.set_trace()
    # include only sent and received packet counts
    req.port.column_names = [req.port.FRAMES_TX, req.port.FRAMES_RX]
    # fetch port metrics
    res = api.get_metrics(req)
    # calculate total frames sent and received across all configured ports
    total_tx = sum([m.frames_tx for m in res.port_metrics])
    total_rx = sum([m.frames_rx for m in res.port_metrics])
    expected = sum([f.duration.fixed_packets.packets for f in cfg.flows])

    print('%d\t\t%d\t\t%d' % (expected, total_tx, total_rx))

    return expected == total_tx and total_rx >= expected


def wait_for(func, timeout=20, interval=0.2):
    '''
    Keeps calling the `func` until it returns true or `timeout` occurs
    every `interval` seconds.
    '''
    import time

    start = time.time()

    while time.time() - start <= timeout:
        if func():
            return True
        time.sleep(interval)

    print('Timeout occurred !')
    return False
