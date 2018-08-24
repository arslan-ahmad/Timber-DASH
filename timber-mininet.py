#!/usr/bin/python
# Written by Arslan Ahmad
# Dated: 17-01-2018
# email address: arslan.ahmad@diee.unica.it
# This topology is written to design SDN with dash streaming wfor investigation
# of the impact of the frequency on the QoE
# input argument for the trace file is required NumberOfRun_FrequencyInSec
from os import environ
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.log import lg, info
from mininet.topolib import TreeNet
from mininet.node import RemoteController
from mininet.term import makeTerms
from mininet.term import makeTerm
import os
import sys, getopt, datetime
import subprocess
import pexpect
from time import sleep
REMOTE_CONTROLLER_IP = "127.0.0.1"
MEDIA_SERVER_IP = "192.168.56.101"
#RUN_NUMBER = "1_2s"
RUN_NUMBER = sys.argv[1]
TODAY=str(datetime.date.today())


class SingleLoopTopo(Topo):
    # Single switch connected to n hosts
     # (or you can use brace syntax: linkopts = {'bw':10, 'delay':'5ms', ... } )
    def __init__(self, **opts):
        # Initialize topology and default optioe
        Topo.__init__(self, **opts)
        switches = []
        hosts = []
        # specify link QoS parameters
        linkopts = dict(bw=5, delay='5ms', loss=10, max_queue_size=1000, use_htb=True)
        # create switches
        for s in range(2):
            switches.append(self.addSwitch('s%s' % (s + 1), protocols='OpenFlow13'))

        # create hosts
        for h in range(2):
            hosts.append(self.addHost('h%s' % (h + 1)))
            #connecting switches with switches

        self.addLink(switches[0], switches[1], **linkopts) #link1 s1-s2
	#connecting hosts with the swtiches
        self.addLink(hosts[0], switches[1]) # server h1 link to s1
        self.addLink(hosts[1], switches[1]) # h2 client to s2
#function get the nodes and run commands in their terminals
def setHosts(net):
    #getting the node from network
    #h3= net.get('h3'); h4= net.get('h4')
    s1= net.get('s1'); s2= net.get('s2')#; s3= net.get('s3')
    s1.cmd('ovs-vsctl set Bridge s1 protocols=OpenFlow13')
    s1.cmd('ovs-vsctl set-manager ptcp:6632')
    s2.cmd('ovs-vsctl set Bridge s2 protocols=OpenFlow13')

def network_monitor():
    os.chdir("..")
    os.chdir("Timber-DASH/network_monitor_trace")
    trace_file="sudo tcpdump -A -i s2-eth1 -w "+RUN_NUMBER+TODAY+"-test-wire.pcap &"
    os.system(trace_file)

def run_dashclient(net):
    h1= net.get('h1'); h2= net.get('h2');
    #running DASH client in the h1 terminal
    network_monitor()
    print ("running DASH client in the h1")
    h1.cmd('cd')
    h1.cmd('cd AStream/dist/client/')
    h2.cmd('cd')
    h2.cmd('cd temp-download')
    #command to start dash player is h1
    start_client= "python dash_client.py -m http://"+MEDIA_SERVER_IP+"/BigBuckBunny_4s.mpd"
    # command for the starting download in h2 terminal
    web_traffic="sudo wget -bqc --tries=0 --read-timeout=5 http://"+MEDIA_SERVER_IP+"/bbb.zip"
    #web_traffic= "iperf -c "+MEDIA_SERVER_IP+" -u -b 1M -t 60 &"
    #TODO check if better to use sendCmd or cmd for automation

    try:
        web=h2.sendCmd(web_traffic)
        #h1.sendCmd(web_traffic)
        #print (web)
        client = h1.cmd(start_client)
        print (client)
    except:
        print ("Opss! DASH client is not running")


    #m= makeTerm(h1,cmd='ifconfig')
    # s3.cmd('ovs-vsctl set Bridge s3 protocols=OpenFlow13')


def startController():
    os.chdir("..")
    os.system("sed '/OFPFlowMod(/,/)/s/)/, table_id=1)/' ryu/ryu/app/simple_switch_13.py > ryu/ryu/app/qos_simple_switch_13.py")
    os.chdir("ryu/")
    os.system("python ./setup.py install")
    ctrlr = pexpect.spawn(
         'xterm -geometry 100x24+0+0 -e ryu-manager ryu.app.rest_qos ryu.app.qos_simple_switch_13 ryu.app.rest_conf_switch')
    #ctrlr1 = pexpect.spawn(
    #     'xterm h1 -geometry 100x24+0+0 -e ifconfig')
    return ctrlr
    # monitor = pexpect.spawn(
    #      'xterm -geometry 100x24+0+0 -e sudo tcpdump -A -i s2-eth1 -w test-wire.pcap')
    # return monitor

def setController(net):
    sleep(5)
    subprocess.call('curl -X PUT -d \'\"tcp:127.0.0.1:6632\"\' http://localhost:8080/v1.0/conf/switches/0000000000000001/ovsdb_addr',shell=True)
    sleep(2)
     #execute setting of Queue
    #subprocess.call('curl -X POST -d \'{\"port_name\": \"s1-eth1\", \"type\": \"linux-htb\", \"max_rate\": \"5000000\", \"queues\": [{\"max_rate\": \"500000\"}, {\"min_rate\": \"3000000\"}]}\' http://localhost:8080/qos/queue/0000000000000001',shell=True)
    #3 QoS Setting to install flow entry
    ##subprocess.call('curl -X GET http://localhost:8080/qos/rules/0000000000000001',shell=True)

if __name__ == '__main__':
    # Tell mininet to print useful information

    setLogLevel('info')
    ctrlr=startController()
    sleep(1)
    topo = SingleLoopTopo()
    net = Mininet(topo=topo,
                  controller=None, link=TCLink,
                  autoStaticArp=True)
    net.addController("c0",
                      controller=RemoteController,
                      ip=REMOTE_CONTROLLER_IP,
                      port=6633)
    net.addNAT().configDefault()
    net.start()
    setHosts(net)
    setController(net)
    #net.startTerms()
    # network_monitor()
    run_dashclient(net)
    # cli = CLI(net)
    sleep(180)
    net.stop()
    # ctrlr.sendcontrol('c')
    # ctrlr.close()
