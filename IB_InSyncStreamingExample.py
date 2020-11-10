from IBDataFetcher import IBDataFetcher
from ib_insync.contract import Forex
import pandas as pd
import matplotlib.pyplot as plt
from ib_insync import util

ib = IBDataFetcher().get_IBClient()

contract = Forex('EURUSD')

bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr='900 S',
        barSizeSetting='10 secs',
        whatToShow='MIDPOINT',
        useRTH=True,
        formatDate=1,
        keepUpToDate=True)

def onBarUpdate(bars, hasNewBar):
    print(bars[-1])


bars = ib.reqRealTimeBars(contract, 6, 'MIDPOINT', False)
bars.updateEvent += onBarUpdate

ib.sleep(30)
ib.cancelRealTimeBars(bars)