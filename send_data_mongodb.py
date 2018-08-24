#!/usr/local/bin/python
import pymongo
from pymongo import MongoClient

class SendData():
    def __init__(self):
        self.dbclient = MongoClient('192.168.56.103', 27017)
        self.db = self.dbclient.qoemonitor.qoe
    def post(self):
        post_data = {"author" : "arslan",
                "test" : "checking the database connection"}
        posting = self.db.insert_one(post_data).inserted_id

if __name__ == '__main__':
    data=SendData()
    data.post()
