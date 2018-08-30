#! /usr/bin/python
"""Written by Arslan Ahmad 2018-08-27
contact for more info at
arslan.ahmad@diee.unica.it

"""
from ryu.base import app_manager
from pymongo import MongoClient
import pymongo
import time
import threading
import os
import sys
import subprocess
import datetime
"""
modification tags the modification made by Arslan
Descrition of the database collections
qoe==> event based database update with the player stats
qoemetric==> only stalling events, stalling duration and time of occurance
qoefrequency==> frequecy based updates
"""
class slicing:
    FREQUENCY=float(sys.argv[1])
    """docstring forslicing."""
    def __init__(self):
        self.frequency=self.FREQUENCY
        self.client = MongoClient()
        self.db = self.client.qoemonitor
        self.cursor=[]
        self.buffer_size = 0
        self.bitrate = 0
        self.action = ''
        self.cursor = {}
        self.manager = None
        self.actual_start_time = None
        self.execution_time = None
        self.delay = None
        self.epochtime = None
    """ function to perform network management tasks"""
    def slicingqoe(self):
        """get data from database"""
        self.cursor=self.db.qoefrequency.find().sort([("_id", -1)]).limit(1)
        for document in self.cursor:
            self.buffer_size=int(document['CurrentBufferSize'])
            self.action=str(document['Action'])
            self.bitrate=float(document['Bitrate'])
            self.actual_start_time=float(document['SysTime'])
            self.epochtime=float(document['EpochTime'])
        self.manager = threading.Timer(self.frequency, self.slicingqoe)
        self.manager.start()
        if (self.bitrate<1000000.0 or self.buffer_size<5) and self.epochtime>30:
            print("done")
          ##3 QoS Setting to install flow entry
            subprocess.call('curl -X POST -d \'{\"port_name\": \"s1-eth1\", \"type\": \"linux-htb\", \"max_rate\": \"5000000\", \"queues\": [{\"max_rate\": \"1000000\"}, {\"min_rate\": \"2500000\"}]}\' http://localhost:8080/qos/queue/0000000000000001',shell=True)
            subprocess.call('curl -X POST -d \'{\"port_name\": \"s2-eth1\", \"type\": \"linux-htb\", \"max_rate\": \"5000000\", \"queues\": [{\"max_rate\": \"1000000\"}, {\"min_rate\": \"2500000\"}]}\' http://localhost:8080/qos/queue/0000000000000002',shell=True)
            subprocess.call('curl -X POST -d \'{\"port_name\": \"s2-eth2\", \"type\": \"linux-htb\", \"max_rate\": \"4000000\", \"queues\": [{\"max_rate\": \"4000000\"}, {\"min_rate\": \"2500000\"}]}\' http://localhost:8080/qos/queue/0000000000000002',shell=True)
            subprocess.call('curl -X POST -d \'{\"port_name\": \"s2-eth3\", \"type\": \"linux-htb\", \"max_rate\": \"1000000\", \"queues\": [{\"max_rate\": \"1500000\"}, {\"min_rate\": \"1000000\"}]}\' http://localhost:8080/qos/queue/0000000000000002',shell=True)
            subprocess.call('curl -X POST -d \'{\"match\": {\"nw_src\": \"10.0.0.1\", \"nw_proto\": \"TCP\", \"tp_dst\": \"80\"}, \"actions\":{\"queue\": \"1\"}}\' http://localhost:8080/qos/rules/0000000000000001',shell=True)
            subprocess.call('curl -X POST -d \'{\"match\": {\"nw_src\": \"10.0.0.2\", \"nw_proto\": \"TCP\", \"tp_dst\": \"80\"}, \"actions\":{\"queue\": \"0\"}}\' http://localhost:8080/qos/rules/0000000000000001',shell=True)
            subprocess.call('curl -X POST -d \'{\"match\": {\"nw_src\": \"10.0.0.1\", \"nw_proto\": \"TCP\", \"tp_dst\": \"80\"}, \"actions\":{\"queue\": \"1\"}}\' http://localhost:8080/qos/rules/0000000000000002',shell=True)
            subprocess.call('curl -X POST -d \'{\"match\": {\"nw_src\": \"10.0.0.2\", \"nw_proto\": \"TCP\", \"tp_dst\": \"80\"}, \"actions\":{\"queue\": \"0\"}}\' http://localhost:8080/qos/rules/0000000000000002',shell=True)

              #4 Verify the settings
            subprocess.call('curl -X GET http://localhost:8080/qos/rules/0000000000000001',shell=True)
            subprocess.call('curl -X GET http://localhost:8080/qos/rules/0000000000000002',shell=True)
            self.execution_time=time.time()
            self.delay = self.actual_start_time-self.execution_time
            f=open('controllactiontime.txt', 'a+')
            f.write("\n Frequency:%d" % self.frequency)
            f.write("\n Start time:%d" % self.actual_start_time)
            f.write("\n End time:%d" % self.execution_time)
            f.write("\n Delay time:%d" % self.delay)
            f.close()
            self.manager.cancel()
if __name__ == '__main__':
    slicing_manager= slicing()
    slicing_manager.slicingqoe()
