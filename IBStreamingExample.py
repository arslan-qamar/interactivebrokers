from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum
class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)
    def tickPrice(self, reqId, tickType, price, attrib):
        print("Tick Price. Ticker Id:", reqId, "tickType:",
        TickTypeEnum.to_str(tickType), "Price:", price, end=' ')
    def tickSize(self, reqId, tickType, size):        
        print("Tick Size. Ticker Id:", reqId, "tickType:",
        TickTypeEnum.to_str(tickType), "Size:", size)

def main():
    app = TestApp()
    app.connect("127.0.0.1", 7497, 0)
    contract = Contract()
    contract = Contract()
    contract.symbol = "EUR"
    contract.secType = "CASH"
    contract.currency = "USD"
    contract.exchange = "IDEALPRO"
    #contract.primaryExchange = "NASDAQ"
    app.reqMarketDataType(1) # switch to delayed-frozen data if live is not available
    app.reqMktData(1, contract, "", False, False, [])
    app.run()
if __name__ == "__main__":
    main()