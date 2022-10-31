#! /usr/bin/env python
# A small script for vrrp devices discovery

import dpkt, ethernet, ip, ip6, vrrp
import sys
import pcapy
import socket
import ipaddr

from docopt import docopt

__doc__ = """Usage: %s [-h] <interface>

Listens on interface to discover devices emitting vrrp packets.

Arguments:
  interface     network interface to listen

Options:
  -h --help
""" % sys.argv[0]


ip_version_map = { 2: socket.AF_INET, 3: socket.AF_INET6 }

def discover_neighbors (interface, timeout=100):
    def on_vrrp_packet (header, data):
        ethernet_frame = ethernet.Ethernet(data)
        ip_packet = ethernet_frame.data
        vrrp_packet = ip_packet.vrrp
        # skip over IPv6 right now, IPv4 needs fixing first
        if vrrp_packet.version == 3:
            return

        print("")
        print(ip_packet.unpack)
        print(vrrp_packet.unpack)
        print(vrrp_packet.checksum)
        vrrp_packet.checksum = 0
        print(dpkt.in_cksum(vrrp_packet.pack_hdr() + vrrp_packet.addrs[0]))
        version = vrrp_packet.version
        for i in vrrp_packet.addrs:
            print(socket.inet_ntop(ip_version_map[version], i))
    
    try:
        pcap = pcapy.open_live (interface, 1524, 1, timeout)
        pcap.setfilter ('proto 112') # VRRP filter
        
        try:
            while True:
                # this is more responsive to  keyboard interrupts
                pcap.dispatch (1, on_vrrp_packet)
        except KeyboardInterrupt as e:
            pass
    except Exception as e:
        print(e)
    
if __name__ == "__main__" :
    options  = docopt(__doc__)
    discover_neighbors (options['<interface>'])
