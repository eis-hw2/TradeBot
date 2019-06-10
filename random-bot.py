import requests
import pandas as pd
import socket
import json
import time
import _thread
import threading
import random

apiPath = "http://202.120.40.8:30255/"
fullApiPath = "http://202.120.40.8:30255/api/v1/"
socketPath = "47.106.8.44"
futureIndex = 2

class ACCOUNT:
    username = ""
    password = ""
    brokerSideUsers = {}
    brokers = []
    futures = {}
    sock = None
    token = ""
    currentPrice = 0
    buy_1 = 0
    sell_1 = 0
    smallInterval = 0.02
    largeInterval = 0.06
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def login(self):
        payload = {"username":self.username, "password":self.password}
        res = requests.post(apiPath+"login", params=payload)
        result = res.json()
        if(result['status'] != "success"):
            return False
        self.token = result['body']
        print("Login Result:\n", result)
    
    def getFutures(self):
        for broker in self.brokers:
            res = requests.get(fullApiPath+"Future?brokerId="+str(broker))
            result = res.json()
            if(result['status'] != "success"):
                return False
            self.futures[broker]=[]
            futures = result['body']
            for future in futures:
                self.futures[broker].append(future)
        print("GetFutures Result:\n", self.futures)
    
    def createOrder(self, orderType, brokerId, marketDepthId, side, count):
        payload = {"type":orderType, "side":side, "marketDepthId":marketDepthId, "count":count}
        res = requests.post(fullApiPath+"Order?brokerId="+brokerId, params=payload)
        result = res.json()
        print(result)
    
    def addBorkerAccount(self):
        payload = {
            "brokerId": 4,
            "password": self.password,
            "traderName": self.username,
            "username": self.username
        }
        headers = {
            'token':self.token,
            'Content-Type':'application/json'
        }
        res = requests.post(fullApiPath+"TraderSideUser/BrokerSideUser", data = json.dumps(payload), headers = headers)
        result = res.json()
        print("addBorkerAccount:", result)
    
    def getUserData(self):
        headers = {
            'token':self.token,
        }
        res = requests.get(fullApiPath+"TraderSideUser/myself", headers = headers)
        result = res.json()
        self.brokerSideUsers = result['body']['brokerSideUsers']
        for broker in result['body']['brokerSideUsers']:
            self.brokers.append(int(broker))
        print("UserData:\n", self.brokerSideUsers, self.brokers)

    def start(self):
        thread0 = threading.Thread(target=self.getQuotation,args=())
        thread1 = threading.Thread(target=self.random_sell,args=())
        thread2 = threading.Thread(target=self.random_buy,args=())
        thread0.start()
        time.sleep(10)
        thread1.start()
        thread2.start()

    def random_sell(self):
        while 1:
            print("SELL")
            time.sleep(random.randint(1, 3))
            bId = self.brokers[0]
            future = self.futures[bId][futureIndex]['description']
            headers = {
                'token':self.token,
                'Content-Type':'application/json'
            }
            count = random.randint(20, 200)
            price = random.randint(round(self.buy_1*(1-self.smallInterval)), round(self.sell_1*(1+self.largeInterval)))
            payload = {"type":"LimitOrder", "side":"SELLER", "futureName":future, "totalCount":count, "unitPrice": price}
            res = requests.post(fullApiPath+"Order?brokerId="+str(bId), headers = headers, data = json.dumps(payload))
            result = res.json()
            print(result)

    def random_buy(self):
        while 1:
            print("BUY")
            time.sleep(random.randint(1, 3))
            bId = self.brokers[0]
            future = self.futures[bId][futureIndex]['description']
            headers = {
                'token':self.token,
                'Content-Type':'application/json'
            }
            count = random.randint(20, 200)
            price = random.randint(round(self.buy_1*(1-self.largeInterval)), round(self.sell_1*(1+self.smallInterval)))
            payload = {"type":"LimitOrder", "side":"BUYER", "futureName":future, "totalCount":count, "unitPrice": price}
            res = requests.post(fullApiPath+"Order?brokerId="+str(bId), headers = headers, data = json.dumps(payload))
            result = res.json()
            print(result)
    
    def getQuotation(self):
        while 1:
            time.sleep(5)
            bId = self.brokers[0]
            mId = self.futures[bId][futureIndex]['marketDepthId']
            path = "http://202.120.40.8:30257/api/v1/Status?brokerId="+str(bId)+"&marketDepthId="+str(mId)
            res = requests.get(path)
            result = res.json()
            quotation = result['body']['marketQuotation']
            orderBook = result['body']['marketDepth']
            self.currentPrice = quotation['currentPrice']
            self.buy_1 = orderBook['buyers'][0]['price']
            self.sell_1 = orderBook['sellers'][0]['price']

def main():
    account = ACCOUNT('bot2', 'bot2')
    account.login()
    account.getUserData()
    account.getFutures()
    account.start()

main()
