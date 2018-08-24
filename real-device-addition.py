#!/usr/bin/python

"""
This example shows how to add an interface (for example a real
hardware interface) to a network after the network is created.
"""

import re
import sys
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info, error
from mininet.net import Mininet
from mininet.link import Intf
from mininet.topolib import TreeTopo
from mininet.util import quietRun
from mininet.node import RemoteController
REMOTE_CONTROLLER_IP = "127.0.0.1"

def checkIntf( intf ):
    "Make sure intf exists and is not configured."
    config = quietRun( 'ifconfig %s 2>/dev/null' % intf, shell=True )
    if not config:
        error( 'Error:', intf, 'does not exist!\n' )
        exit( 1 )
    ips = re.findall( r'\d+\.\d+\.\d+\.\d+', config )
    if ips:
        error( 'Error:', intf, 'has an IP address,'
               'and is probably in use!\n' )
        exit( 1 )

class SingleLoopTopo(Topo):
    # Single switch connected to n hosts
    def __init__(self, **opts):
        # Initialize topology and default optioe
        Topo.__init__(self, **opts)
        switches = []
        hosts = []

        # create switches
        s1=self.addSwitch('s1')
        h1= self.addHost ('h1', ip='10.131.2.130/24')
        h2= self.addHost ('h2', ip='10.131.2.133/24')
        self.addLink(h1,s1)
        self.addLink(h2,s1)

if __name__ == '__main__':
    setLogLevel( 'info' )
    topo = SingleLoopTopo()
    # try to get hw intf from the command line; by default, use eth1
    intfName = sys.argv[ 1 ] if len( sys.argv ) > 1 else 'eth1'
    info( '*** Connecting to hw intf: %s' % intfName )

    info( '*** Checking', intfName, '\n' )
    checkIntf( intfName )

    info( '*** Creating network\n' )
    net = Mininet(topo=topo,
                  controller=None,
                  autoStaticArp=True)
    net.addController("c0",
                      controller=RemoteController,
                      ip=REMOTE_CONTROLLER_IP,
                      port=6634)

    switch = net.switches[ 0 ]
    info( '*** Adding hardware interface', intfName, 'to switch',
          switch, '\n' )
    _intf = Intf( intfName, node=switch )

    info( '*** Note: you may need to reconfigure the interfaces for '
          'the Mininet hosts:\n', net.hosts, '\n' )

    net.start()
    CLI( net )
    net.stop()

# %%%%%%%%%%mininet brige
# # This file describes the network interfaces available on your system
# # and how to activate them. For more information, see interfaces(5).
#
# # The loopback network interface
# auto lo
# iface lo inet loopback
#
# # The primary network interface
# auto eth0
# iface eth0 inet dhcp
#
# iface nat0-eth0 inet manual
