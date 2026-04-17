def dec2hex(dec):
    hex_str = hex(dec)[2:]
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str
    return hex_str

def hex2lehex(hex_str):
    # Convert hex string to little-endian hex string
    le_hex_str = ''.join(reversed([hex_str[i:i + 2] for i in range(0, len(hex_str), 2)]))
    return le_hex_str

def get_pl_sip_encoding(vni):
    # "::e903:64:ff71:0:0/::ffff:ffff:ffff:0:0"
    # 64 -> local region id 100 dec, in hex is 64 -> Hardcoded
    # d107->  07d1 -> vnet vni: dec 2001 = hex 07d1 = little endian d107
    # ff71 -> 71ff -> subnet label coming from ENI -> 29183  -> Hardcoded

    abc = dec2hex(vni)
    print(abc)
    vni_hex_le = hex2lehex(abc)
    return "::%s:64:ff71:0:0/::ffff:ffff:ffff:0:0" % vni_hex_le


print (get_pl_sip_encoding(1024))