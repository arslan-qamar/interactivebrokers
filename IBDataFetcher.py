from ib_insync import *
from datetime import datetime


class IBDataFetcher():
    ib = None
    def __init__(self):
        self.ib = IB()
        self.ib.connect('127.0.0.1', 7497, clientId=datetime.now().microsecond)
        
    def get_IBClient(self):
        return self.ib

   
